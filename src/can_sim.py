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