# mac_auth.py
# HMAC-SHA256 based message authentication for CAN messages
# Simulates AUTOSAR SecOC (Secure Onboard Communication) concept
# Linked to: CR-01, CR-02
# Part of: Secure-ACC Project

import hmac
import hashlib
import json

# ── Secret key (in production this would be derived via
#    a key management system - HSM in real ECUs) ────────────
SECRET_KEY = b"SecureACC_SharedKey_2026"


class MACAuthenticator:
    """
    Provides HMAC-SHA256 authentication for CAN messages.
    Simulates SecOC module in AUTOSAR stack.

    In real AUTOSAR SecOC:
    - Key stored in Hardware Security Module (HSM)
    - Freshness value prevents replay attacks
    - Truncated MAC (24-64 bits) fits in CAN frame
    """

    def __init__(self, key=SECRET_KEY):
        self.key             = key
        self.verified_count  = 0
        self.rejected_count  = 0

    def _serialize_payload(self, payload):
        """
        Convert payload dictionary to consistent byte string.
        Sorting keys ensures same order every time.
        """
        return json.dumps(payload, sort_keys=True).encode('utf-8')

    def generate_mac(self, msg_id, payload):
        """
        Generate HMAC-SHA256 for a CAN message.
        Inputs : msg_id (hex string), payload (dict)
        Output : MAC as hex string (truncated to 16 chars)
        """
        # Combine message ID and payload into one string
        data = f"{msg_id}:{self._serialize_payload(payload).decode()}"

        # Generate HMAC-SHA256
        mac = hmac.new(
            self.key,
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Truncate to 16 chars (64 bits) - simulates CAN frame size limit
        return mac[:16]

    def sign_message(self, message):
        """
        Add MAC to a CAN message dictionary.
        Returns message with MAC field filled.
        """
        mac = self.generate_mac(
            message["msg_id"],
            message["payload"]
        )
        message["mac"] = mac
        return message

    def verify_message(self, message):
        """
        Verify MAC on received CAN message.
        Returns True if authentic, False if tampered.
        Implements CR-01 and CR-02.
        """
        if message.get("mac") is None:
            self.rejected_count += 1
            return False, "No MAC present"

        # Recompute expected MAC
        expected_mac = self.generate_mac(
            message["msg_id"],
            message["payload"]
        )

        # Compare using hmac.compare_digest (timing-safe comparison)
        if hmac.compare_digest(message["mac"], expected_mac):
            self.verified_count += 1
            return True, "MAC verified"
        else:
            self.rejected_count += 1
            return False, "MAC mismatch - message rejected"

    def get_stats(self):
        """Return authentication statistics"""
        total = self.verified_count + self.rejected_count
        return {
            "verified":       self.verified_count,
            "rejected":       self.rejected_count,
            "rejection_rate": round(
                self.rejected_count / max(1, total) * 100, 2)
        }
    
    
    # ── Quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    print("--- MAC Authentication Test ---")
    auth = MACAuthenticator()

    # Build a test message
    test_message = {
        "msg_id":  "0x1a3",
        "timestamp": 0.1,
        "cycle_counter": 1,
        "payload": {
            "distance_m":       30.5,
            "relative_vel_mps": -5.0,
            "target_detected":  True
        },
        "mac": None
    }

    # Sign it
    signed = auth.sign_message(test_message)
    print(f"Generated MAC : {signed['mac']}")

    # Verify legitimate message
    valid, reason = auth.verify_message(signed)
    print(f"Legitimate msg: {valid} — {reason}")

    # Tamper with payload - simulate attack
    tampered = dict(signed)
    tampered["payload"] = dict(signed["payload"])
    tampered["payload"]["distance_m"] = 2.0  # attacker injects 2m
    valid, reason = auth.verify_message(tampered)
    print(f"Tampered msg  : {valid} — {reason}")

    print(f"\nStats: {auth.get_stats()}")