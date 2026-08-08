# Milestones

Platform: **Eclypse Z7** + **2× Zmod Scope 1410**  
Host link: **Gigabit Ethernet** (ADR-002). FT601 deferred.

## Phase 1 — Eclypse ↔ Ethernet ↔ MetaField

**Goal:** PS transport up; UDP data plane + optional TCP control.

**Pass:** `host/phase1_ethernet/verify_udp_stream.py` PASS ≥10 s.

---

## Phase 2 — Zmod → FPGA → DMA → Ethernet

1410 acquisition into framed UDP (`ADC_RAW` / later FEATURE).

**Pass:** known test signal recoverable on host with timestamps.

---

## Phase 3 — CAN-FD + synchronized time

ESP32 Field Bus + Eclypse; correlate Hall with Zmod timestamps.

---

## Phase 4 — S/PDIF → amp → sub → measure

Digital stimulus path + 1410/Hall feedback (low level).

---

## Phase 5 — FPGA DSP / features

RAW | FEATURE | HYBRID modes; reduce continuous raw bandwidth.

---

## Phase 6 — MetaField closes the loop

`acquire → observe → command → actuate → measure`.

---

## Phase 7 — FT601 only if needed

Measured Ethernet bottleneck → then evaluate USB3 FIFO.

---

Record passes under `lab/`.
