# MetaField Physical-Computational Integration Architecture

> **Platform update (2026-08-08):** FPGA centerpiece is **Digilent Eclypse Z7** + **2× Zmod Scope 1410**, not Zybo Z7-20 as primary.  
> See **[docs/ADR-001-eclypse-z7-instrumentation.md](docs/ADR-001-eclypse-z7-instrumentation.md)** for the decision record.  
> Sections below that name Zybo / Pmod AD1 / DA4 describe the *prior* plan; substitute **Eclypse** for Zybo and **Zmod 1410** for primary high-speed analog I/O. Pmod path is deferred. Zmod AWG 1411 is deferred.

## 0. Executive Architecture

This project is evolving from a collection of independent experiments into a heterogeneous, closed-loop physical-computational system.

The central architecture is:

```
                         ┌─────────────────────────────┐
                         │          METAFIELD           │
                         │ physics / state / simulation │
                         │ AI / reconstruction / model  │
                         │ global experiment control    │
                         └──────────────┬──────────────┘
                                        │
                                  USB 3 / FT601
                                        │
                         ┌──────────────▼──────────────┐
                         │        ECLYPSE Z7            │
                         │  ARM PROCESSOR   FPGA FABRIC │
                         │ local control       DSP      │
                         │ orchestration    Zmod 1410×2 │
                         └──────────────┬──────────────┘
                                        │
                              CAN / CAN-FD + I/O
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                 ESP32               ESP32               ESP32...
                    │                   │                   │
               sensors / IO        optical nodes        actuators
                    │                   │                   │
                    └───────────────────┼───────────────────┘
                                        │
                              PHYSICAL EXPERIMENT
                       ┌────────────────┴───────────────┐
                 Hall-field system              optical system
                       └────────────────┬───────────────┘
                                        └───────────────↺
```

The intended system is not simply a PC controlling peripherals.  
**The physical system becomes part of the computational loop.**

---

## 1. System Roles

### 1.1 ProDesk 600 G6 — Heavy Host / World Model

The existing HP ProDesk 600 G6 Minis are sufficient for initial development and should be used before moving to a larger motherboard.

**Primary responsibilities:**

- MetaField execution
- computationally expensive simulation
- machine learning / reconstruction
- large state spaces, dataset generation, visualization
- experiment analysis, long-term storage/logging
- global orchestration

The ProDesk is the heavyweight computational layer.  
It does **not** need to provide deterministic real-time physical control.

---

## 2. MetaField

MetaField is the high-level computational / world-model layer.

The existing MetaField repository contains the physics/simulation machinery and is intended to evolve from a purely simulated environment into a system capable of consuming measured physical state and producing predicted/control state.

```
physical measurement
        ↓
    state vector
        ↓
     MetaField
        ↓
 predicted state
        ↓
 control / experiment state
```

Long-term: physical observations become inputs to the model rather than an unrelated external experiment.

Repo: [metafield](https://github.com/TheBabelDragon/metafield)

---

## 3. Eclypse Z7 — Local Heterogeneous Compute Node

**Selected FPGA/SoC platform: Digilent Eclypse Z7** (Zynq-7020)

Contains both:

- Zynq **ARM** processing system
- programmable **FPGA fabric**
- **Zmod** high-speed SYZYGY instrumentation ports

```
                 ECLYPSE Z7
        ┌─────────────────────────┐
        │   ARM PROCESSOR         │
        │        │ AXI            │
        │        ▼                │
        │   FPGA FABRIC           │
        │        │                │
        │   Zmod Scope 1410 ×2    │
        └─────────────────────────┘
```

### ARM responsibilities

Local control/orchestration plane — **not** a duplicate MetaField host:

- local experiment orchestration
- CAN/CAN-FD management
- configuration, buffering, logging
- local networking, FPGA config/control, register access
- parameter management, monitoring, fault detection
- safety/interlock handling
- communication with the ProDesk

### FPGA responsibilities

Deterministic physical-computing layer:

- high-speed acquisition (Zmod 1410), timestamping
- deterministic signal processing / DSP / correlation / filtering
- event detection, hardware state machines
- S/PDIF encoding/decoding, digital audio processing
- low-latency control loops, custom accelerators
- FPGA-side CAN interface
- real-time physical-system interaction

ARM and FPGA provide deliberate redundancy at **different levels**, not duplicated workload.

*(Historical: Zybo Z7-20 + Pmod AD1/DA4 plan — superseded by ADR-001.)*

---

## 4. FTDI FT601Q-B / UMFT601A-B

USB 3.0 FIFO bridge between Eclypse FPGA fabric and host.

```
MetaField / ProDesk
        │ USB 3
     FT601Q-B
        │ 32-bit FIFO
   Eclypse FPGA
```

Treat as **high-bandwidth host transport**, not a general-purpose sensor interface.

Potential data: raw Zmod captures, processed frames, Hall-array state, timestamps, PCM, diagnostics, experiment/model state, control parameters, high-rate telemetry.

**Initial implementation target:**

```
FPGA counter/test stream → FT601 → USB 3 → Linux → bit-perfect verification
```

Once that works, it becomes the primary high-speed host interface.

---

## 5. ESP32 Distributed Network

ESP32 devices remain the distributed **edge** layer. They do not compete with the FPGA.

Localized: sensor acquisition, actuator control, preprocessing, I/O, device management, physical placement flexibility.

**Bus:** CAN / CAN-FD ([field-bus](https://github.com/TheBabelDragon/field-bus))

```
                    CAN-FD
                       │
       ┌───────────────┼───────────────┐
     ESP32           ESP32           ESP32
    sensors         optical          I/O
```

Eclypse (ARM and/or fabric) should become a first-class CAN participant so not every ESP32 must talk directly to Linux.

---

## 6. TCA9548A I²C Infrastructure

Inventory: **6 × TCA9548A** (8-channel I²C mux each).

Use for structured, **lower-rate** peripherals (ADS1115, FRAM, MCP23017, env sensors, config devices, address conflicts).  
**Not** the primary high-rate acquisition path (that is Zmod 1410).

```
I²C master (ESP32 / ARM / FPGA)
             │
         TCA9548A
    ┌────────┼────────┐
  CH0      CH1      CH2 ...
 ADS1115   FRAM    MCP23017
```

---

## 7. Hall Sensor + 3 kRMS Subwoofer Experiment

First major closed-loop physical demonstrator:

- 10 Hall sensors
- 3 kRMS subwoofer + amplifier chain
- ESP32 acquisition + CAN-FD
- Eclypse FPGA + Zmod measurement + MetaField host

Objective: measure electromagnetic response of the actuator and use that as feedback — not merely audio playback.

```
audio/control command → S/PDIF → existing DAC → amp → sub → magnetic field
  → Hall ×10 → ESP32 → CAN-FD → Eclypse (+ Zmod electrical/physical channels)
  → FT601 → MetaField → model / prediction / control → Eclypse → audio/control  ↺
```

Measured response becomes part of the state; the actuator is not assumed to match the model exactly.

---

## 8. Analog I/O (current)

### Primary: Zmod Scope 1410 ×2

Four high-speed ADC channels (see ADR-001 for example allocation).

### Stimulus: existing DAC path via S/PDIF

Not Zmod AWG 1411 initially (deferred).

### Historical / deferred: Pmod AD1, DA4, etc.

Lower priority; not required for the first closed loop.

---

## 9. S/PDIF / Optical Audio Path

```
FPGA PCM → S/PDIF encoder → optical TX → TOSLINK → optical RX
  → S/PDIF decoder → existing DAC → amp → sub
```

FPGA implements S/PDIF logic (not a black-box USB audio gadget).

**Initial milestone:** known PCM → TX → optical → RX → bit-perfect compare.  
Only then integrate the amplifier chain.

See [SPIDF_M0.md](SPIDF_M0.md).

---

## 10. Audio Control Paths

| Path | Chain |
|------|--------|
| Digital | FPGA → S/PDIF → optical → existing DAC → amp |
| Measurement | physical / electrical → Zmod 1410 → FPGA |
| Distributed | Hall / optical → ESP32 → CAN-FD → FPGA |

---

## 11. Closed-Loop Timing Hierarchy

| Layer | Role |
|-------|------|
| ProDesk / MetaField | global model / simulation |
| Eclypse ARM | local orchestration |
| Eclypse FPGA | deterministic physical loop |
| ESP32 | distributed edge acquisition |
| Physical system | actual physics |

**Important boundary: the FPGA.**  
Linux/MetaField need not provide deterministic timing for every physical event.

---

## 12. Proposed Full Architecture

```
MetaField (simulation, world model, AI, reconstruction, global orchestration)
        │ USB 3
     FT601Q-B
        │ 32-bit FIFO
   Eclypse Z7 (ARM orchestration + FPGA + Zmod Scope 1410 ×2)
        │
   ┌────┼────┐
 CAN-FD  Zmod  S/PDIF
   │
 ESP32 × N  →  TCA9548A / sensors / Hall / optical nodes
   │
 PHYSICAL SYSTEM (3 kRMS sub, magnetic field, optical substrate)
   └───────────────────────────────↺
```

---

## 13. First Implementation Sequence

See [MILESTONES.md](MILESTONES.md) and ADR-001.

1. Eclypse + FT601 test stream  
2. FPGA infrastructure  
3. Zmod 1410 acquisition into host  
4. ESP32 CAN-FD  
5. Hall array  
6. S/PDIF  
7. Amp/sub + measure  
8. MetaField closed loop  

---

## 14. Closed-Loop Development Target

```
MetaField (predicted state)
    → Eclypse ARM (orchestration)
    → Eclypse FPGA (deterministic control)
    → S/PDIF → DAC → amp → actuator → physical response → sensors / Zmod
    → ESP32 → CAN-FD → Eclypse FPGA → FT601 → MetaField
    ↺
```

---

## 15. Design Principle

| Layer | Question |
|-------|----------|
| MetaField / ProDesk | What **should** happen? |
| Eclypse ARM | How should the local system be **coordinated**? |
| Eclypse FPGA | What must happen **deterministically right now**? |
| ESP32 nodes | What is happening at the **distributed edge**? |
| Physical system | What **actually** happened? |

---

## 16. Current Hardware Integration Inventory

**Host:** HP ProDesk 600 G6 Minis; Ryzen/AM4 B450M Pro4 available later  
**FPGA/SoC:** Digilent **Eclypse Z7**  
**Instrumentation:** **2× Zmod Scope 1410**  
**High-speed host link:** FTDI **FT601Q-B / UMFT601A-B**  
**Deferred:** Zmod AWG 1411, Pmod cart as primary path  
**Edge:** ESP32 / ESP32-S3 as appropriate  
**Network:** SN65HVD230, **MCP2518FD**, Field Bus  
**I²C:** 6× TCA9548A, ADS1115, MCP23017, FRAM  
**Sense:** 10× Hall, BPW34 / optical substrate  
**Actuate:** 3 kRMS sub, existing DAC + amp, S/PDIF optical path  
**Also owned:** Arty A7 (secondary)  

---

## 17. Long-Term Physical-Computational Vision

Heterogeneous substrate across CPU, optional GPU, ARM, FPGA, ESP32 edge, optical/EM interactions, sensor-derived state, and model state — with **feedback** between domains.

```text
computer ↔ experiment
model ↔ hardware ↔ physical system
```

---

## 18. Immediate Next Milestone

```
Eclypse Z7 → FPGA test logic → FT601 → ProDesk → verify
```

Then Zmod acquisition, CAN-FD, Hall, S/PDIF, amp/sub, MetaField close.

**Build from the transport boundary outward.**
