# Milestones

Platform: **Digilent Eclypse Z7** + **2× Zmod Scope 1410** + **FT601**  
(See [docs/ADR-001-eclypse-z7-instrumentation.md](docs/ADR-001-eclypse-z7-instrumentation.md).)

## Phase 1 — Eclypse + FT601 transport

**Goal:** `FPGA → FT601 → USB3 → Linux` bit-perfect test stream.

**Pass:** contiguous sequence, host `verify_stream.py` PASS (≥10 s).

---

## Phase 2 — FPGA infrastructure

Registers, clocks, FIFOs, timestamp counter, host command channel.

---

## Phase 3 — Zmod Scope 1410 acquisition

**Goal:** Synchronized capture on up to 4 ADC channels into fabric → FT601.

**Pass:** Host receives framed samples with timestamps; known test signal recoverable.

---

## Phase 4 — ESP32 CAN-FD

**Goal:** `ESP32 → CAN-FD → Eclypse` via [field-bus](https://github.com/TheBabelDragon/field-bus).

**Pass:** HELLO / STATUS / TIME_SYNC; node ONLINE.

---

## Phase 5 — Hall array on bus

Ten Hall channels via ESP32; aligned with FPGA timebase where possible.

---

## Phase 6 — S/PDIF

`PCM → TX → optical → RX → PCM` bit-perfect, then into existing DAC path.

---

## Phase 7 — Amp / sub (low level) + measure

Stimulus → amp → sub; electrical/physical response on Zmod 1410s (+ Hall).

---

## Phase 8 — MetaField adapter (first closed loop)

Measurements → MetaField → new stimulus → Eclypse → S/PDIF → … → measure again.

**Pass:** Supervisory close without Linux in the sample path.

---

## Tracking

Record each pass under `lab/`. Do not start Phase n+1 until Phase n is checked off.

**Deferred:** Zmod AWG 1411 until Phase 8 limitations justify it.
