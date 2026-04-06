# attack_sim.py
# Simulates CAN bus attacks against the ACC system
# Demonstrates system behaviour with and without MAC authentication
# Attack types: distance spoofing, replay attack
# Linked to: CR-01, CR-02, CR-03, CR-04
# Part of: Secure-ACC Project

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vehicle_model import VehicleModel
from radar_sim import RadarSensor
from acc_controller import ACCController
from can_sim import CANBus
from mac_auth import MACAuthenticator

# ── Attack parameters ───────────────────────────────────────
ATTACK_START_STEP  = 20     # step at which attack begins
FAKE_DISTANCE      = 2.0    # metres - injected by attacker
SIMULATION_STEPS   = 50     # total steps to simulate


def run_simulation(use_security=True, inject_attack=False):
    """
    Run ACC simulation for one scenario.
    use_security  : True = MAC authentication enabled
    inject_attack : True = attacker injects fake distance
    Returns list of results per step.
    """
    # Initialise components
    ego      = VehicleModel(initial_velocity=20.0)
    lead     = VehicleModel(initial_velocity=15.0)
    radar    = RadarSensor()
    acc      = ACCController()
    can_bus  = CANBus()
    auth     = MACAuthenticator()

    # Start lead vehicle 50m ahead
    lead.position = 50.0

    results = []

    for step in range(SIMULATION_STEPS):
        # Update lead vehicle
        lead.update(throttle_pct=20, brake_pct=0)

        # Get current states
        ego_state  = ego.get_state()
        lead_state = lead.get_state()

        # Radar measures gap
        radar.update(
            ego_state["position_m"],  ego_state["velocity_ms"],
            lead_state["position_m"], lead_state["velocity_ms"]
        )
        m = radar.get_measurement()

        # ── Attack injection ─────────────────────────────
        if inject_attack and step >= ATTACK_START_STEP:
            attack_distance = FAKE_DISTANCE
        else:
            attack_distance = m["distance_m"]

        # ── CAN message with optional security ───────────
        message = can_bus.send_radar_message(
            attack_distance,
            m["relative_vel_mps"],
            m["target_detected"]
        )

        # If message was rejected by range/spike check
        if message is None:
            distance_to_use = m["distance_m"]
            message_accepted = False
        elif use_security:
            # Sign legitimate messages, attacker cannot sign
            if not (inject_attack and step >= ATTACK_START_STEP):
                message = auth.sign_message(message)
            # Verify MAC
            valid, reason = auth.verify_message(message)
            if valid:
                distance_to_use  = message["payload"]["distance_m"]
                message_accepted = True
            else:
                distance_to_use  = m["distance_m"]
                message_accepted = False
                print(f"  [SECURITY] Step {step}: {reason}")
        else:
            distance_to_use  = message["payload"]["distance_m"]
            message_accepted = True

        # ACC computes command using accepted distance
        acc.update(
            ego_state["velocity_ms"],
            distance_to_use,
            m["target_detected"]
        )
        cmd = acc.get_command()

        # Apply command to ego vehicle
        ego.update(cmd["throttle_pct"], cmd["brake_pct"])

        # Store results
        results.append({
            "step":             step,
            "time_s":           round(step * 0.1, 1),
            "ego_velocity_kmh": ego_state["velocity_kmh"],
            "distance_m":       distance_to_use,
            "throttle_pct":     cmd["throttle_pct"],
            "brake_pct":        cmd["brake_pct"],
            "attack_active":    inject_attack and step >= ATTACK_START_STEP,
            "msg_accepted":     message_accepted
        })

    return results