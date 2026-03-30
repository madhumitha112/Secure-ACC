# acc_controller.py
# Adaptive Cruise Control PID Controller
# Computes throttle and brake commands based on distance error
# Linked to: FR-01, FR-02, FR-03, FR-04, SR-01, SR-03, SR-04
# Part of: Secure-ACC Project

# ── PID Tuning Constants ────────────────────────────────────
KP = 0.4       # Proportional gain
KI = 0.01      # Integral gain
KD = 0.1       # Derivative gain

# ── ACC Constants ───────────────────────────────────────────
TIME_GAP      = 2.0    # seconds - target time headway (FR-01)
MIN_DISTANCE  = 5.0    # metres - emergency brake threshold (SR-01)
MAX_SPEED     = 33.3   # m/s - 120 kmh speed limit (SR-04)
MAX_DECEL     = 0.8    # g - maximum deceleration (SR-03)
TIME_STEP     = 0.1    # seconds - 100ms control loop (PR-01)

class ACCController:
    """
    PID-based Adaptive Cruise Control controller.
    Computes throttle and brake commands every 100ms.
    Implements anti-windup clamping on integral term.
    Linked to: FR-01 through FR-07, SR-01, SR-03, SR-04
    """

    def __init__(self):
        self.integral        = 0.0    # accumulated error (I term)
        self.previous_error  = 0.0    # last step's error (D term)
        self.throttle_pct    = 0.0    # output: 0-100%
        self.brake_pct       = 0.0    # output: 0-100%

    def compute_target_distance(self, ego_velocity):
        """
        Target distance = ego speed x time gap (2 seconds)
        This implements the 2-second rule from FR-01.
        Minimum 10 metres even at very low speeds.
        """
        return max(10.0, ego_velocity * TIME_GAP)

    def compute_pid(self, error):
        """
        Core PID calculation.
        Returns a control output between -100 and +100.
        Positive = accelerate, Negative = brake.
        """
        # P term - proportional to current error
        p_term = KP * error

        # I term - accumulate error over time
        self.integral += error * TIME_STEP

        # Anti-windup - clamp integral to prevent runaway
        self.integral = max(-50.0, min(50.0, self.integral))
        i_term = KI * self.integral

        # D term - rate of change of error
        derivative = (error - self.previous_error) / TIME_STEP
        d_term = KD * derivative

        # Store error for next cycle
        self.previous_error = error

        return p_term + i_term + d_term

    def update(self, ego_velocity, distance, target_detected):
        """
        Main ACC update - runs every 100ms.
        ego_velocity    : current ego speed (m/s)
        distance        : radar measured distance to lead (m)
        target_detected : whether radar sees a lead vehicle
        """
        # SR-01: Emergency brake if too close
        if distance <= MIN_DISTANCE:
            self.throttle_pct = 0.0
            self.brake_pct    = 100.0
            return

        # SR-04: No acceleration beyond max speed
        if ego_velocity >= MAX_SPEED and not target_detected:
            self.throttle_pct = 0.0
            self.brake_pct    = 0.0
            return

        # No lead vehicle - cruise at current speed
        if not target_detected:
            self.throttle_pct = 20.0
            self.brake_pct    = 0.0
            return

        # Compute distance error
        target_distance = self.compute_target_distance(ego_velocity)
        error = distance - target_distance

        # PID output
        pid_output = self.compute_pid(error)

        # Positive output = too far = accelerate
        # Negative output = too close = brake
        if pid_output >= 0:
            self.throttle_pct = min(100.0, pid_output)
            self.brake_pct    = 0.0
        else:
            self.throttle_pct = 0.0
            self.brake_pct    = min(100.0, abs(pid_output))

    def get_command(self):
        """Return current ACC command as dictionary"""
        return {
            "throttle_pct": round(self.throttle_pct, 2),
            "brake_pct":    round(self.brake_pct, 2)
        }
    
    # ── Quick test ───────────────────────────────────────────────
if __name__ == "__main__":
    from vehicle_model import VehicleModel
    from radar_sim import RadarSensor

    print("--- ACC Controller Test ---")
    ego      = VehicleModel(initial_velocity=20.0)
    lead     = VehicleModel(initial_velocity=15.0)
    radar    = RadarSensor()
    acc      = ACCController()

    # Start lead vehicle 50m ahead
    lead.position = 50.0

    print(f"{'Step':<6} {'Ego km/h':<12} {'Distance':<12} {'Throttle%':<12} {'Brake%'}")
    print("-" * 55)

    for step in range(30):
        # Update lead vehicle - constant speed
        lead.update(throttle_pct=20, brake_pct=0)

        # Radar measures gap
        ego_state  = ego.get_state()
        lead_state = lead.get_state()
        radar.update(
            ego_state["position_m"],  ego_state["velocity_ms"],
            lead_state["position_m"], lead_state["velocity_ms"]
        )
        m = radar.get_measurement()

        # ACC computes command
        acc.update(
            ego_state["velocity_ms"],
            m["distance_m"],
            m["target_detected"]
        )
        cmd = acc.get_command()

        # Apply command to ego vehicle
        ego.update(cmd["throttle_pct"], cmd["brake_pct"])

        print(f"{step:<6} {ego_state['velocity_kmh']:<12} "
              f"{m['distance_m']:<12} {cmd['throttle_pct']:<12} "
              f"{cmd['brake_pct']}")