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