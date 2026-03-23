# Secure-ACC: Adaptive Cruise Control with CAN Security Simulation

## Overview
A simulation of an Adaptive Cruise Control (ACC) system integrating ADAS perception,
longitudinal vehicle control (PID), CAN bus communication, and cybersecurity (MAC-based
message authentication). Built to mirror Tier-1 automotive development practices.

## Domain Coverage
- ADAS: Radar-based perception, safe distance logic
- Control Systems: PID longitudinal controller, vehicle dynamics model
- Cybersecurity: TARA, CAN message spoofing attack, HMAC-based mitigation

## Folder Structure
- requirements/ --- Software Requirements Specification (SRS)
- architecture/ --- ECU data flow diagrams
- src/          --- Python simulation modules
- tara/         --- Threat Analysis and Risk Assessment
- fmea/         --- Failure Mode and Effects Analysis
- results/      --- Test output plots

## CI/CD
GitHub Actions runs automated tests on every commit. See .github/workflows/

## Status
Week 1 - Requirements and architecture phase
