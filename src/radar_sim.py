# radar_sim.py
# Simulates a forward-facing radar sensor on the ego vehicle
# Measures distance and relative velocity to lead vehicle
# Based on: SRS-ACC-001 requirement FR-06
# Part of: Secure-ACC Project

import random

# ── Radar constants ─────────────────────────────────────────
MAX_RANGE = 200.0       # metres - maximum radar detection range
MIN_RANGE = 0.5         # metres - minimum detection distance
NOISE_STD = 0.2         # metres - Gaussian noise standard deviation
VELOCITY_NOISE = 0.05   # m/s - velocity measurement noise
UPDATE_RATE = 0.1       # seconds - 100ms, matches PR-01

class RadarSensor:
    """
    Simulates a forward-facing automotive radar sensor.
    Computes distance and relative velocity to lead vehicle.
    Adds realistic Gaussian noise to measurements.
    Linked to: FR-06, CR-03, CR-04
    """

    def __init__(self):
        self.distance = MAX_RANGE       # metres
        self.relative_velocity = 0.0    # m/s (negative = closing in)
        self.is_target_detected = False

    def update(self, ego_position, ego_velocity,
               lead_position, lead_velocity):
        """
        Update radar measurement for current time step.
        ego_position  : position of ego vehicle (m)
        ego_velocity  : speed of ego vehicle (m/s)
        lead_position : position of lead vehicle (m)
        lead_velocity : speed of lead vehicle (m/s)
        """
        # True distance between vehicles
        true_distance = lead_position - ego_position

        # True relative velocity (negative means closing in)
        true_relative_velocity = lead_velocity - ego_velocity

        # Check if target is within radar range
        if MIN_RANGE <= true_distance <= MAX_RANGE:
            self.is_target_detected = True

            # Add Gaussian noise to distance measurement
            noise = random.gauss(0, NOISE_STD)
            self.distance = round(true_distance + noise, 3)

            # Add noise to relative velocity measurement
            vel_noise = random.gauss(0, VELOCITY_NOISE)
            self.relative_velocity = round(
                true_relative_velocity + vel_noise, 3)

        else:
            self.is_target_detected = False
            self.distance = MAX_RANGE
            self.relative_velocity = 0.0

    def get_measurement(self):
        """Return current radar measurement as CAN-ready dictionary"""
        return {
            "distance_m":        self.distance,
            "relative_vel_mps":  self.relative_velocity,
            "target_detected":   self.is_target_detected
        }
    
    # ── Quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    print("--- Radar Sensor Test ---")
    radar = RadarSensor()

    # Simulate: ego at 0m doing 20m/s, lead at 50m doing 15m/s
    ego_pos, ego_vel = 0.0, 20.0
    lead_pos, lead_vel = 50.0, 15.0

    print(f"{'Step':<6} {'Distance(m)':<14} {'Rel Vel(m/s)':<16} {'Detected'}")
    print("-" * 50)

    for step in range(10):
        # Lead vehicle moves forward
        lead_pos += lead_vel * UPDATE_RATE
        ego_pos += ego_vel * UPDATE_RATE

        radar.update(ego_pos, ego_vel, lead_pos, lead_vel)
        m = radar.get_measurement()

        print(f"{step:<6} {m['distance_m']:<14} "
              f"{m['relative_vel_mps']:<16} {m['target_detected']}")