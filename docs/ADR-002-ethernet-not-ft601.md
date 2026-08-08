# ADR-002: Eclypse Gigabit Ethernet Transport (FT601 Deferred)

**Status:** Accepted  
**Date:** 2026-08-08  
**Supersedes:** FT601 as *required* Phase-1 host link (ADR-001 purchase list / Phase-1 FT601 milestone)

---

## Decision

**Do not buy FT601 for the initial build.**

Host ↔ Eclypse transport is **Gigabit Ethernet** on the Eclypse Z7:

- **Control plane:** TCP (reliable, low bandwidth) — configure, trigger, status  
- **Data plane:** UDP (sequence + timestamps owned by us) — samples, features, commands  

FT601 / USB3 FIFO is **deferred** until measured throughput shows Ethernet is the actual bottleneck.

We are **not** implementing USB 3 in the FPGA. MetaField talks to the **Zynq PS**; fabric ↔ PS is **AXI DMA**.

---

## Pipeline

```
PRODESK
  MetaField / acquisition API
        │ Ethernet
Zynq PS  (MAC, Linux/FreeRTOS, transport)
        │ AXI DMA
FPGA PL  (DSP, sync, control, acquisition)
        │
Zmod Scope 1410 ×2
        │
physical system
```

MetaField never needs to understand FPGA registers, AXI, Ethernet packets, or Zmod hardware — only framed payloads.

---

## Two planes

### Control plane (TCP)

```
MetaField → Ethernet/TCP → Zynq PS → AXI-Lite → FPGA registers
```

Examples: `SET_SAMPLE_RATE`, `SET_TRIGGER`, `SET_GAIN`, `START_CAPTURE`, `STOP_CAPTURE`, `SET_MODE`, `GET_STATUS`.

### Data plane (UDP)

**Uplink (acquire):**

```
1410 → FPGA → AXI Stream → AXI DMA → DDR → Zynq PS → UDP → MetaField
```

**Downlink (command / waveform marks):**

```
MetaField → UDP → Zynq PS → DDR → AXI DMA → FPGA DSP/control → S/PDIF …
```

UDP is appropriate because **sequence numbers and timestamps are mandatory in the payload**; we do not trust packet arrival time for correlation.

---

## Frame contract (application level)

```
FRAME
├── magic
├── version
├── sequence
├── timestamp          // acquisition time, not host RX time
├── node / source
├── channel
├── sample_rate
├── sample_count
├── payload_type       // RAW | FEATURE | HYBRID | COMMAND | …
└── samples[] / body
```

Conceptual MetaField loop:

```text
frame = acquire()
prediction = metafield(frame)
command = controller(prediction)
send(command)
```

Same shape for CAN/Hall frames so MetaField can correlate Zmod analog, Hall, and commanded waveform without relying on Ethernet latency.

---

## FPGA first design (minimal)

```
Zmod 1410 → ADC interface → sample formatter → AXI-Stream FIFO → AXI DMA → DDR → PS → Ethernet
```

Reverse path later:

```
Ethernet → PS → DDR → AXI DMA → FIFO → FPGA DSP/control → S/PDIF
```

FPGA = real-time acquisition/control engine; ARM = network gateway.

---

## Bandwidth honesty

Four channels at high rate (e.g. ~100 MS/s × 14-bit class) exceed continuous Gigabit Ethernet.

**Do not design for “stream all ADC samples to MetaField forever.”**

Instead:

```
FPGA: acquisition → real-time DSP + circular buffer
         ├── features (RMS, FFT, phase, peak, envelope, correlations)
         └── raw windows on demand
              → Ethernet → MetaField
```

Modes: **RAW** | **FEATURE** | **HYBRID**.

Subwoofer experiment fits: short high-res windows + continuous features.

---

## When to revisit FT601

Only after a real measurement:  
*“Gigabit Ethernet limits us to X; we need more continuous raw throughput.”*

Not because theoretical USB3 numbers look attractive.

---

## Revised development sequence

| Phase | Goal |
|-------|------|
| 1 | Eclypse → Ethernet → MetaField (control + test data plane) |
| 2 | 1410 → FPGA → DMA → Ethernet → MetaField |
| 3 | CAN + 1410 synchronized acquisition |
| 4 | S/PDIF → amp → sub → 1410 / Hall feedback |
| 5 | FPGA-side DSP + feature extraction |
| 6 | MetaField closes the loop |
| 7 | Evaluate FT601 / USB3 FIFO **only if** measured bottleneck |

---

## MetaField transport sketch (host)

```text
metafield/
  transport/   protocol, ethernet, framing, timestamp, stream
  hardware/    eclypse, zmod1410
  control/     acquisition, waveform, synchronization
```

```python
eclypse = Eclypse("192.168.1.50")
eclypse.configure(sample_rate=1_000_000, channels=[0, 1, 2, 3])
eclypse.start()
while True:
    frame = eclypse.read()
    state = metafield.observe(frame)
    command = controller(state)
    eclypse.command(command)
```

---

## Consequences

- **Purchase:** Eclypse Z7 + 2× Zmod Scope 1410; **no FT601** on the critical path  
- Phase-1 host work targets **Ethernet framing**, not FT601 FIFO dumps  
- Existing `protocols/ft601_frames_v0.md` and `host/phase1_ft601/` remain **optional / future** reference  
- New primary protocol docs: Ethernet frame + control commands (this ADR + follow-on)
