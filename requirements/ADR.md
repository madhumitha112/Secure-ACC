# Architecture Decision Records (ADR)
## Project: Secure-ACC

This document logs key design decisions made during the project, the reasoning behind them, and the alternatives considered.

---

## ADR-001: Vehicle Model Abstraction

**Date:** 23-03-2026
**Status:** Accepted

**Decision:**
Simulate vehicle speed and position using Newton's second law (F = ma). Derive wheel speed directly from vehicle speed without modelling wheel slip or tire dynamics.

**Reasoning:**
- Sufficient to validate PID controller behaviour
- Sufficient to demonstrate cybersecurity attack scenarios
- Wheel slip modelling adds complexity without adding value to our learning objectives

**What a full implementation would use:**
- CarMaker or IPG Vehicle Dynamics for HIL testing at OEM level
- Separate wheel speed sensor ECU feeding CAN bus

**Note:**
"Implemented a longitudinal dynamics model based on Newton's second law. Wheel speed was derived directly from vehicle speed since wheel slip was out of scope. A production system would use CarMaker or similar for full vehicle dynamics validation."

---

## ADR-002: CAN Bus Simulation Approach

**Date:** 23-03-2026
**Status:** Accepted

**Decision:**
Simulate CAN bus communication using Python dictionaries representing CAN frames — message ID, signal values, timestamp, and MAC field.

**Reasoning:**
- No real CAN hardware available
- The authentication logic (SecOC concept) is identical whether running on real CAN hardware or simulated frames
- Focus is on cybersecurity logic, not electrical layer

**What a full implementation would use:**
- Real CAN hardware (PCAN-USB or Kvaser interface)
- python-can library with actual CAN frames
- CANoe for professional bus analysis

**Note:**
"Simulated CAN frames as structured Python objects with message ID, payload, periodicity, and HMAC field — matching the AUTOSAR SecOC message structure conceptually. Real hardware integration could use python-can with a PCAN or Kvaser interface."

---

## ADR-003: Single CAN Network

**Date:** 23-03-2026
**Status:** Accepted

**Decision:**
Simulate one CAN bus connecting all ECUs. No separation into multiple networks (e.g. powertrain CAN vs. chassis CAN).

**Reasoning:**
- Real vehicles have multiple CAN networks but separation adds no value to demonstrating ACC + security logic
- Keeps architecture simple and understandable

**What a full implementation would use:**
- Separate CAN networks per domain
- Gateway ECU managing inter-network communication
- Possibly CAN-FD or Automotive Ethernet for higher bandwidth

---