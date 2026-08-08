# Milestones

## M0 — S/PDIF digital highway (first Arty project)

**Goal:** Bit-perfect optical digital audio path through the FPGA.

```
Arty generates known PCM
  → S/PDIF encode
  → optical TX (TOSLINK)
  → optical RX
  → S/PDIF decode
  → compare to original
```

**Pass criteria:**

- Locked sample rate (start: 48 kHz, 16-bit or 24-bit stereo)
- Continuous TX of a known tone or PRBS-in-PCM
- RX recovers samples with **zero** mismatches over a fixed window (e.g. 10 s) *or* documented BER = 0 under lab conditions
- LEDs / UART report lock, mismatch count, sample rate

**Out of scope for M0:** amplifier, Hall, MetaField, CAN.

Details: [SPIDF_M0.md](SPIDF_M0.md)

---

## M1 — Amplifier in the middle

```
Arty → S/PDIF → TOSLINK → amp / DSP → sub
```

**Pass:** audible/known tone; no FPGA RX required if amp is sink-only.  
Optional: split optical and keep RX monitor path from M0.

---

## M2 — Field Bus southbound live

- A7 talks CAN-FD (via MCP2518FD or soft+PHY — board-dependent)
- Implements Field Bus: emits `TIME_SYNC`, receives `NODE_STATUS` / sensor telemetry
- At least one ESP32 node (Hall or optical) heartbeats and is visible to A7

**Pass:** A7 UART/host log shows node 0x0N ONLINE with fresh timestamps.

---

## M3 — Hall array correlation

```
audio sample index  ↔  Hall ×10 snapshot
```

**Pass:** recorded stream where each field frame references `sample_index` or network time aligned to audio.

---

## M4 — FT601 to ProDesk

- Bulk transfer of PCM markers + field state + status to host
- MetaField or a thin logger consumes frames (no control law required yet)

**Pass:** ProDesk captures >N seconds of aligned data without drops (budget TBD on FT601 throughput).

---

## M5 — Supervisory close

- MetaField sends setpoints / mode / excitation plan to A7 over FT601
- Fast loop still runs on A7; model loop is slow

**Pass:** change in MetaField policy visibly changes A7 behavior (tone, gain schedule, or excitation) within agreed latency bound.

---

## Tracking rule

Do not start Mn+1 until Mn pass criteria are checked off in a short lab note (even a markdown file in this repo).
