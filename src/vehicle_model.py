# vehicle_model.py
# Simulates longitudinal dynamics of the ego vehicle
# Based on Newton's second law: F = ma
# Part of: Secure-ACC Project

# ── Constants ──────────────────────────────────────────────
MASS = 1500          # kg - typical sedan mass
CD = 0.3             # drag coefficient - typical sedan
FRONTAL_AREA = 2.2   # m² - frontal area of vehicle
AIR_DENSITY = 1.2    # kg/m³ - air density at sea level
MAX_BRAKE_FORCE = 8000   # N - maximum braking force
MAX_THROTTLE_FORCE = 3000  # N - maximum engine force
TIME_STEP = 0.1      # seconds - 100ms control loop


class VehicleModel:
    """
    Simulates ego vehicle longitudinal dynamics.
    Inputs  : throttle_pct (0-100), brake_pct (0-100)
    Outputs : velocity (m/s), position (m)
    """

    def __init__(self, initial_velocity=0.0, initial_position=0.0):
        self.velocity = initial_velocity    # m/s
        self.position = initial_position    # m
        self.acceleration = 0.0            # m/s²

    def compute_drag(self):
        """Aerodynamic drag force opposing motion"""
        return 0.5 * AIR_DENSITY * CD * FRONTAL_AREA * (self.velocity ** 2)

    def update(self, throttle_pct, brake_pct):
        """
        Update vehicle state for one time step.
        throttle_pct : 0-100 (percentage of max throttle)
        brake_pct    : 0-100 (percentage of max braking)
        """
        # Convert percentages to forces
        throttle_force = (throttle_pct / 100) * MAX_THROTTLE_FORCE
        brake_force = (brake_pct / 100) * MAX_BRAKE_FORCE
        drag_force = self.compute_drag()

        # Newton's second law
        f_net = throttle_force - brake_force - drag_force

        # Calculate acceleration
        self.acceleration = f_net / MASS

        # Update velocity - cannot go below zero
        self.velocity = max(0.0, self.velocity + self.acceleration * TIME_STEP)

        # Update position
        self.position = self.position + self.velocity * TIME_STEP

    def get_state(self):
        """Return current vehicle state as a dictionary"""
        return {
            "velocity_ms": round(self.velocity, 3),
            "velocity_kmh": round(self.velocity * 3.6, 3),
            "position_m": round(self.position, 3),
            "acceleration": round(self.acceleration, 3)
        }

    # ── Quick test (remove before final submission) ────────────
if __name__ == "__main__":
    print("--- Vehicle Model Test ---")
    car = VehicleModel(initial_velocity=0.0)

    print(f"{'Step':<6} {'Velocity (m/s)':<16} {'Velocity (kmh)':<16} {'Position (m)':<14} {'Acceleration'}")
    print("-" * 70)

    for step in range(20):
        car.update(throttle_pct=50, brake_pct=0)
        s = car.get_state()
        print(
            f"{
                step:<6} {
                s['velocity_ms']:<16} {
                s['velocity_kmh']:<16} {
                    s['position_m']:<14} {
                        s['acceleration']}")
