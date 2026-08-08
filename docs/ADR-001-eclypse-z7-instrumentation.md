# ADR-001: Eclypse Z7 Instrumentation Pivot

**Status:** Accepted  
**Date:** 2026-08-08  
**Supersedes:** Zybo Z7-20 + Pmod-heavy instrumentation plan (INTEGRATION.md sections targeting Zybo/Pmod AD1/DA4 as primary analog I/O)

---

## Decision

The FPGA centerpiece is upgraded from the previously considered **Zybo Z7-20 + Pmod-heavy** instrumentation architecture to the **Digilent Eclypse Z7 + Zmod** instrumentation architecture.

The reason is **architectural** rather than simply computational: the project has evolved into a closed-loop physical computing and instrumentation system, making **high-speed deterministic analog acquisition** more valuable than the Zybo’s integrated HDMI, MIPI camera, onboard audio, and larger number of Pmod connectors.

### Current target purchase

| Item | Role |
|------|------|
| **Eclypse Z7** | Zynq-7020 ARM + FPGA real-time core |
| **2 × Zmod Scope 1410** | 4 high-speed ADC channels |
| **UMFT601A-B / FT601Q-B** | USB3 FIFO to ProDesk / MetaField |
| Existing S/PDIF optical hardware | Digital audio transport |
| Existing external DAC + amp + 3 kRMS sub | Physical audio actuation |
| Existing ESP32 / CAN-FD network | Distributed sensing |

**Zmod AWG 1411 is deferred** / intentionally omitted from the initial build.

---

## Why the Eclypse Z7

Same fundamental Zynq-7020 ARM + FPGA architecture as Zybo, but expansion is oriented toward **high-speed instrumentation**.

**Previous emphasis (Zybo):**

```
Zybo
├── Pmods
├── onboard audio
├── HDMI
├── MIPI camera
└── general-purpose FPGA experimentation
```

**New emphasis (Eclypse):**

```
Eclypse
├── FPGA real-time processing
├── ARM control/orchestration
├── high-speed Zmod acquisition
├── deterministic physical I/O
├── distributed CAN-FD sensors
└── high-bandwidth host connection
```

Loss of HDMI, MIPI camera, and onboard audio is acceptable — those are not fundamental to the physical-computing loop. **ProDesk** remains responsible for visualization, MetaField computation, development, storage, and host-side orchestration.

---

## Zmod Scope 1410 Decision

Eclypse bundle: **Eclypse Z7 + 2 × Zmod Scope 1410** (~$690) is economically correct versus buying 1410s individually.

```
1410 #1 → ADC ch 0, ch 1
1410 #2 → ADC ch 2, ch 3
→ 4 independent high-speed analog measurement channels
```

More valuable to the initial physical-feedback experiment than a second analog-output module.

**Example allocation (experimental, not locked):**

| Channel | Candidate use |
|---------|----------------|
| ADC 0 | Commanded / reference signal |
| ADC 1 | Amplifier / electrical response |
| ADC 2 | Physical / subwoofer response |
| ADC 3 | Secondary sensor / experimental |

---

## Why No Zmod AWG 1411 Initially

Primary audio stimulus path is already defined:

```
MetaField / ProDesk → FT601 → Eclypse FPGA → S/PDIF → optical
  → existing DAC → amplifier → 3 kRMS subwoofer
```

Existing DAC/amp provides the audio-output endpoint. The 1410s measure electrical and physical behavior independently. **1411 later** if experiments require direct FPGA-controlled analog stimulus.

---

## Closed-Loop Physical Architecture

```
                    ┌─────────────────────┐
                    │      PRODESK        │
                    │ MetaField / Models  │
                    │ Visualization       │
                    │ Orchestration       │
                    └──────────┬──────────┘
                               │ FT601
                    ┌──────────▼──────────┐
                    │     ECLYPSE Z7      │
                    │ ARM + FPGA          │
                    │ Real-time / DSP / I/O│
                    └───────┬─────┬──────┘
                            │     │
                         Zmods   CAN-FD
                            │     │
                  ┌─────────┘     └─────────────┐
             1410 #1 / #2                 ESP32 nodes
           4-channel ADC              Hall / optical / …
                  │                             │
                  └─────────────┬───────────────┘
                         physical state → MetaField → control ↺
```

### Layer separation

| Layer | Owner | Responsibility |
|-------|--------|----------------|
| Host | ProDesk / MetaField | Modeling, learning, visualization, orchestration, storage, higher-level decisions |
| Real-time physical | Eclypse FPGA | Deterministic acquisition, DSP, sync, low-latency feedback, hardware state |
| Distributed sensors | ESP32 + CAN-FD | Hall, optical, local preprocess, physical placement |
| Audio transport | S/PDIF | Digital audio to existing DAC |
| Analog / power | DAC → amp → sub | High-power physical stimulus |

---

## Subwoofer Experiment Loop

Not dependent on Zybo onboard audio:

```
MetaField → control/waveform → Eclypse → S/PDIF → existing DAC → amp → sub
                │                                    │
          electrical response              physical response
                │                                    │
             1410 ADCs                          Hall network
                │                                    │
                └────────── Eclypse → FT601 → MetaField → updated model ↺
```

**stimulus → physical response → measurement → model update → new stimulus**

Audio is one actuator inside a broader instrumentation and learning architecture — not “playback.”

---

## Previous Pmod Architecture — Superseded

No longer required for the **initial** Eclypse architecture:

- Pmod AD5, DA3, DA4, I2S2, TPH2, DIP, SW, DPOT
- additional audio ADC/DAC breakout boards as primary path

Not obsolete forever — **lower priority**. Zmod layer is the stronger foundation.

**Still useful** (distributed sensing, not competing with Zmod primary path):

- ADS1115, TCA9548A, MCP23017, FRAM
- ESP32 peripherals, Hall sensors, BPW34 optical sensors

---

## FT601 Role

High-bandwidth boundary: `MetaField ↔ FT601 USB3 FIFO ↔ Eclypse FPGA ↔ real-time physical system`.

FPGA does not wait on a GPOS for time-critical acquisition or control.

---

## CAN-FD Role

Distributed sensor/actuator backbone (six-node infrastructure retained):

```
Eclypse — CAN-FD — ESP32 (Hall) / ESP32 (optical) / …
```

CAN = distributed physical nervous system; Eclypse = local real-time processing/control core.

---

## Architecture Principle

**Functional separation**, not interface accumulation.

| Piece | Role |
|-------|------|
| ProDesk | Computation / visualization |
| FT601 | High-bandwidth boundary |
| Eclypse FPGA | Deterministic physical computation |
| Zmod 1410 ×2 | High-speed measurement |
| CAN-FD | Distributed sensing |
| S/PDIF | Digital audio transport |
| Existing DAC + amp | Physical audio actuation |
| Hall / optical | Physical observation |
| MetaField | Model / learning / reconstruction |

---

## Current Hardware Decision Summary

**Buy:** Eclypse Z7, 2× Zmod Scope 1410, UMFT601A-B/FT601Q-B, S/PDIF optical as required  

**Retain:** ProDesk G6, ESP32 nodes, CAN-FD gear, Hall, BPW34, ADS1115, TCA9548A, MCP23017, FRAM, existing DAC/amp/sub, Arty A7  

**Defer:** Zmod AWG 1411, additional Zmods, Pmod cart, dedicated I²S ADC/DAC boards as primary path  

Reconsider 1411 only after the first complete **acquisition → modeling → actuation** loop is operational.

---

## Immediate Development Goal

Not “get the FPGA talking to a DAC.”

**First genuine closed loop:**

1. Synchronized physical measurements on the Eclypse (Zmod 1410s)  
2. Through FT601 into MetaField  
3. Controlled digital stimulus out  
4. S/PDIF → existing DAC → amp → sub  
5. Resulting measurements back into the model  

Once that exists, more hardware is justified by **actual limitation**, not speculation.

---

## Consequences for this repository

- Platform string / docs: **Eclypse Z7** (not Zybo-primary)
- Phase-1 transport (FT601 frames, host verifier) remains valid
- S/PDIF M0 remains valid (pinout becomes Eclypse-specific)
- Primary analog path: **Zmod Scope 1410**, not Pmod AD1/DA4
- Zybo / Arty references become historical or secondary platforms
