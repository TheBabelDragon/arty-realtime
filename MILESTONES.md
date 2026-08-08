# Milestones

Aligned with [INTEGRATION.md](INTEGRATION.md). Platform: **Zybo Z7-20**.

## Phase 1 — Zybo + FT601 transport

**Goal:** `FPGA → FT601 → USB3 → Linux` bit-perfect test stream.

**Pass:** sequence numbers, timestamps, integrity check; host captures without silent drops.

---

## Phase 2 — FPGA infrastructure

Registers, clock domains, FIFOs, timestamp counter, host command channel, clean HW/SW interface.

---

## Phase 3 — ESP32 CAN-FD

**Goal:** `ESP32 → CAN-FD → Zybo` using [field-bus](https://github.com/TheBabelDragon/field-bus).

**Pass:** HELLO / STATUS / TIME_SYNC; at least one node ONLINE on Zybo side.

---

## Phase 4 — Hall array

Ten Hall channels via ESP32; synchronized `H(t) = [H0…H9]` into Zybo (raw or framed).

---

## Phase 5 — S/PDIF

`PCM → TX → optical → RX → PCM` bit-perfect (see [SPIDF_M0.md](SPIDF_M0.md)).

---

## Phase 6 — Amp / sub (low level)

Verified path into amp; commanded waveform vs electrical vs Hall response.

---

## Phase 7 — MetaField adapter

`read_physical_state` / step / control into existing MetaField API; supervisory close.

---

## Tracking

Record each pass under `lab/` (e.g. `lab/phase1_ft601.md`). Do not start Phase n+1 until Phase n is checked off.
