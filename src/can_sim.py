# can_sim.py
# Simulates CAN bus communication between ECUs
# Implements AUTOSAR-style message framing with SecOC placeholder
# Linked to: FR-06, FR-07, CR-01, CR-02, CR-03, CR-04
# Part of: Secure-ACC Project

import time

# ── CAN Message IDs (hex - matches architecture diagram) ────
RADAR_MSG_ID  = 0x1A3    # Radar ECU → ACC ECU
ACC_MSG_ID    = 0x2B1    # ACC ECU → Brake ECU

# ── Message cycle times ─────────────────────────────────────
CYCLE_TIME_MS = 100      # milliseconds - matches PR-01

# ── Signal validity ranges (CR-03) ──────────────────────────
MAX_DISTANCE     = 200.0   # metres
MIN_DISTANCE     = 0.0     # metres
MAX_REL_VELOCITY = 50.0    # m/s
MIN_REL_VELOCITY = -50.0   # m/s
MAX_THROTTLE     = 100.0   # percent
MIN_THROTTLE     = 0.0     # percent

class CANBus:
    """
    Simulates CAN bus message passing between ECUs.
    Each message contains:
    - Message ID (hex)
    - Payload (signal values)
    - Timestamp
    - MAC field (placeholder for SecOC - filled by mac_auth.py)
    - Cycle counter (for replay attack detection)
    """

    def __init__(self):
        self.message_log   = []      # stores all messages
        self.rejected_log  = []      # stores rejected messages (CR-05)
        self.cycle_counter = 0       # increments every message

    def _validate_radar_signals(self, distance, rel_velocity):
        """
        Validate radar signal ranges before accepting message.
        Implements CR-03 - range check.
        Returns True if valid, False if suspicious.
        """
        if not (MIN_DISTANCE <= distance <= MAX_DISTANCE):
            return False, f"Distance {distance}m out of range"

        if not (MIN_REL_VELOCITY <= rel_velocity <= MAX_REL_VELOCITY):
            return False, f"Relative velocity {rel_velocity} out of range"

        return True, "OK"

    def _validate_spike(self, distance, message_log):
        """
        Detect sudden distance spikes - implements CR-04.
        A real vehicle cannot jump more than 10m in 100ms.
        """
        if len(message_log) < 1:
            return True, "OK"

        last_distance = message_log[-1]["payload"]["distance_m"]
        change = abs(distance - last_distance)

        if change > 10.0:
            return False, f"Distance spike detected: {change:.2f}m change"

        return True, "OK"

    def send_radar_message(self, distance, rel_velocity,
                           target_detected, mac=None):
        """
        Radar ECU sends message to ACC ECU over CAN bus.
        Validates signals before accepting onto bus.
        """
        self.cycle_counter += 1
        timestamp = round(self.cycle_counter * CYCLE_TIME_MS / 1000, 3)

        # CR-03: Range validation
        valid, reason = self._validate_radar_signals(
            distance, rel_velocity)

        if not valid:
            self._log_rejection(RADAR_MSG_ID, timestamp, reason)
            return None

        # CR-04: Spike detection
        radar_log = [m for m in self.message_log
                     if m["msg_id"] == RADAR_MSG_ID]
        valid, reason = self._validate_spike(distance, radar_log)

        if not valid:
            self._log_rejection(RADAR_MSG_ID, timestamp, reason)
            return None

        # Build CAN frame
        message = {
            "msg_id":        hex(RADAR_MSG_ID),
            "timestamp":     timestamp,
            "cycle_counter": self.cycle_counter,
            "payload": {
                "distance_m":       round(distance, 3),
                "relative_vel_mps": round(rel_velocity, 3),
                "target_detected":  target_detected
            },
            "mac": mac    # filled by mac_auth.py
        }

        self.message_log.append(message)
        return message

    def send_acc_message(self, throttle_pct, brake_pct, mac=None):
        """
        ACC ECU sends command message to Brake ECU over CAN bus.
        """
        self.cycle_counter += 1
        timestamp = round(self.cycle_counter * CYCLE_TIME_MS / 1000, 3)

        message = {
            "msg_id":        hex(ACC_MSG_ID),
            "timestamp":     timestamp,
            "cycle_counter": self.cycle_counter,
            "payload": {
                "throttle_pct": round(throttle_pct, 2),
                "brake_pct":    round(brake_pct, 2)
            },
            "mac": mac
        }

        self.message_log.append(message)
        return message

    def _log_rejection(self, msg_id, timestamp, reason):
        """
        Log rejected messages with timestamp and reason.
        Implements CR-05 - rejection logging.
        """
        rejection = {
            "msg_id":    hex(msg_id),
            "timestamp": timestamp,
            "reason":    reason
        }
        self.rejected_log.append(rejection)
        print(f"  [CAN REJECTED] t={timestamp}s | {reason}")

    def get_stats(self):
        """Return message statistics"""
        return {
            "total_sent":     len(self.message_log),
            "total_rejected": len(self.rejected_log),
            "rejection_rate": round(
                len(self.rejected_log) /
                max(1, len(self.message_log) +
                    len(self.rejected_log)) * 100, 2)
        }