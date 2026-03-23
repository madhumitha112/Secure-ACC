# SRS-ACC-v1: Software Requirements Specification
## Adaptive Cruise Control (ACC) with CAN Security Simulation

---

| Field        | Details                        |
|--------------|-------------------------------|
| Document ID  | SRS-ACC-001                   |
| Version      | v1.0                          |
| Status       | Draft                         |
| Author       | Madhu                         |
| Date         | 23-03-2026                    |
| Project      | Secure-ACC                    |

---

## 1. Purpose

This document defines the software requirements for a simulated Adaptive Cruise Control (ACC) system. The system integrates ADAS perception, longitudinal vehicle control, CAN bus communication, and cybersecurity mechanisms. It is developed to mirror Tier-1 automotive development practices.

---

## 2. Scope

The simulation covers:
- Radar-based distance and relative velocity sensing
- Safe following distance logic (2-second time gap rule)
- PID-based longitudinal control (throttle and brake commands)
- CAN bus message simulation between ECUs
- HMAC-based message authentication (SecOC concept)
- Attack simulation and mitigation demonstration

Out of scope:
- Hardware-in-the-loop (HIL) testing
- Real vehicle CAN bus integration
- Lateral control

---

## 3. Definitions

| Term     | Meaning                                                    |
|----------|------------------------------------------------------------|
| ACC      | Adaptive Cruise Control                                    |
| ECU      | Electronic Control Unit                                    |
| CAN      | Controller Area Network - vehicle communication bus        |
| PID      | Proportional-Integral-Derivative controller                |
| HMAC     | Hash-based Message Authentication Code                     |
| SecOC    | Secure Onboard Communication (AUTOSAR security module)     |
| TARA     | Threat Analysis and Risk Assessment (ISO 21434)            |
| TTC      | Time To Collision                                          |
| THW      | Time Headway - time gap between ego and lead vehicle       |

---

## 4. Requirements

### 4.1 Functional Requirements

| Req ID   | Requirement                                              | Rationale                              |
|----------|----------------------------------------------------------|----------------------------------------|
| FR-01    | The system shall maintain a minimum time headway (THW) of 2 seconds to the lead vehicle | Safety: 2s THW is standard ACC design rule |
| FR-02    | The system shall adjust ego vehicle speed based on lead vehicle speed and distance | Core ACC behaviour |
| FR-03    | The system shall command throttle reduction when THW drops below 2 seconds | Prevents rear collision |
| FR-04    | The system shall command braking when THW drops below 1 second | Emergency response |
| FR-05    | The system shall resume set speed when no lead vehicle is detected within range | Standard ACC cruise behaviour |
| FR-06    | The radar ECU shall transmit distance and relative velocity to ACC ECU every 100ms | AUTOSAR signal periodicity standard |
| FR-07    | The ACC ECU shall transmit throttle and brake commands to Brake ECU every 100ms | Actuator update rate |

### 4.2 Safety Requirements

| Req ID   | Requirement                                              | Rationale                              |
|----------|----------------------------------------------------------|----------------------------------------|
| SR-01    | The system shall apply maximum braking if distance to lead vehicle drops below 5 metres | Fail-safe: prevent collision |
| SR-02    | The system shall default to maximum braking on sensor signal loss | Fail-safe: safe state on failure |
| SR-03    | The system shall limit maximum deceleration to 0.8g to prevent rear-end collision by following vehicle | Physical safety limit |
| SR-04    | The system shall not accelerate beyond the driver-set maximum speed | Speed limiter requirement |

### 4.3 Cybersecurity Requirements

| Req ID   | Requirement                                              | Rationale                              |
|----------|----------------------------------------------------------|----------------------------------------|
| CR-01    | The system shall authenticate all CAN messages using HMAC-SHA256 | Prevents message spoofing (ISO 21434) |
| CR-02    | The system shall reject any CAN message that fails MAC verification | Mitigation against injection attacks |
| CR-03    | The system shall detect distance values outside the valid range (0-200 metres) and discard them | Anomaly detection |
| CR-04    | The system shall detect sudden distance changes greater than 10 metres in one cycle and flag them | Spoofing pattern detection |
| CR-05    | The system shall log all rejected messages with timestamp and reason | Traceability for incident analysis |

### 4.4 Performance Requirements

| Req ID   | Requirement                                              | Rationale                              |
|----------|----------------------------------------------------------|----------------------------------------|
| PR-01    | The control loop shall execute at 10Hz (every 100ms)     | Standard ACC update rate               |
| PR-02    | The PID controller shall reach steady-state within 5 seconds of a speed change | Control stability requirement |
| PR-03    | The system shall simulate a minimum of 60 seconds of driving scenario | Sufficient test coverage               |

---

## 5. ECU Architecture

The system consists of three simulated ECUs communicating over a CAN bus:

- **Radar ECU** — generates distance and relative velocity signals
- **ACC ECU** — receives radar data, runs PID controller, outputs commands
- **Brake ECU** — receives throttle/brake commands, updates vehicle model

Architecture diagram: see `/architecture/ECU_dataflow.png`

---

## 6. Traceability Matrix

| Req ID | Implemented In       | Test Scenario          |
|--------|----------------------|------------------------|
| FR-01  | src/acc_controller.py | test_normal_following  |
| FR-02  | src/acc_controller.py | test_speed_adjustment  |
| FR-03  | src/acc_controller.py | test_close_following   |
| FR-04  | src/acc_controller.py | test_emergency_brake   |
| SR-01  | src/acc_controller.py | test_emergency_brake   |
| SR-02  | src/vehicle_model.py  | test_sensor_loss       |
| CR-01  | src/mac_auth.py       | test_mac_valid         |
| CR-02  | src/mac_auth.py       | test_mac_rejected      |
| CR-03  | src/can_sim.py        | test_range_check       |
| CR-04  | src/can_sim.py        | test_spike_detection   |

---

## 7. Open Issues

| Issue ID | Description                  | Status  |
|----------|------------------------------|---------|
| OI-01    | HMAC key management strategy to be defined | Open |
| OI-02    | Sensor loss simulation method to be confirmed | Open |

---

*End of Document*