# MetaField Physical-Computational Integration Architecture

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
                         │         ZYBO Z7-20           │
                         │  ARM PROCESSOR   FPGA FABRIC │
                         │ local control       DSP      │
                         │ networking           timing   │
                         │ orchestration       capture  │
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

## 3. Zybo Z7-20 — Local Heterogeneous Compute Node

**Selected FPGA/SoC platform: Digilent Zybo Z7-20**

Contains both:

- Zynq **ARM** processing system
- programmable **FPGA fabric**

```
                 ZYBO Z7-20
        ┌─────────────────────────┐
        │   ARM PROCESSOR         │
        │        │ AXI            │
        │        ▼                │
        │   FPGA FABRIC           │
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

- high-speed acquisition, timestamping
- deterministic signal processing / DSP / correlation / filtering
- event detection, hardware state machines
- S/PDIF encoding/decoding, digital audio processing
- analog I/O control (via Pmods)
- low-latency control loops, custom accelerators
- FPGA-side CAN interface
- real-time physical-system interaction

ARM and FPGA provide deliberate redundancy at **different levels**, not duplicated workload.

---

## 4. FTDI FT601Q-B / UMFT601A-B

USB 3.0 FIFO bridge between Zybo FPGA fabric and host.

```
MetaField / ProDesk
        │ USB 3
     FT601Q-B
        │ 32-bit FIFO
   Zybo FPGA
```

Treat as **high-bandwidth host transport**, not a general-purpose sensor interface.

Potential data: raw captures, processed frames, Hall-array state, timestamps, PCM, diagnostics, experiment/model state, control parameters, high-rate telemetry.

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

Zybo (ARM and/or fabric) should become a first-class CAN participant so not every ESP32 must talk directly to Linux.

---

## 6. TCA9548A I²C Infrastructure

Inventory: **6 × TCA9548A** (8-channel I²C mux each).

Use for structured, **lower-rate** peripherals (ADS1115, FRAM, MCP23017, env sensors, config devices, address conflicts).  
**Not** the primary high-rate Hall waveform path.

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
- Zybo FPGA + MetaField host

Objective: measure electromagnetic response of the actuator and use that as feedback — not merely audio playback.

```
audio/control command → amp → sub → magnetic field
  → Hall ×10 → ESP32 → CAN-FD → Zybo → FT601 → MetaField
  → model / prediction / control → Zybo → audio/control  ↺
```

Measured response becomes part of the state; the actuator is not assumed to match the model exactly.

---

## 8. Analog I/O

### Pmod AD1

Direct analog measurement, test signals, feedback, instrumentation.  
**Not** a direct connection to high-power amp outputs — use conditioning/protection.

### Pmod DA4

Four-channel analog generation, experimental control, audio/control prototyping.  
**Not** a power amplifier — conditioning before amp.

---

## 9. S/PDIF / Optical Audio Path

```
FPGA PCM → S/PDIF encoder → optical TX → TOSLINK → optical RX
  → S/PDIF decoder → PCM
```

FPGA implements S/PDIF logic (not a black-box USB audio gadget).

**Initial milestone:** known PCM → TX → optical → RX → bit-perfect compare.  
Only then integrate the amplifier chain.

See [SPIDF_M0.md](SPIDF_M0.md) (adapted to Zybo pinout when hardware is fixed).

---

## 10. Audio Control Paths

| Path | Chain |
|------|--------|
| Digital | FPGA → S/PDIF → optical → amp |
| Analog | FPGA → DA4 → conditioning → amp |
| Measurement | physical → AD1 / sensors → FPGA |

Compare electrical, digital, and physical behavior deliberately.

---

## 11. Closed-Loop Timing Hierarchy

| Layer | Role |
|-------|------|
| ProDesk / MetaField | global model / simulation |
| Zybo ARM | local orchestration |
| Zybo FPGA | deterministic physical loop |
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
   Zybo Z7-20 (ARM orchestration + FPGA acquisition/DSP/timing/S/PDIF/control)
        │
   ┌────┼────┐
 CAN-FD  AD1  DA4
   │
 ESP32 × N  →  TCA9548A / sensors / Hall / optical nodes
   │
 PHYSICAL SYSTEM (3 kRMS sub, magnetic field, optical substrate)
   └───────────────────────────────↺
```

---

## 13. First Implementation Sequence

### Phase 1 — Zybo + FT601

Prove: `FPGA → FT601 → USB 3 → Linux` with deterministic test data.

Deliverables: FIFO implementation, FT601 interface, host receiver, framing, sequence numbers, timestamps, integrity checking.

### Phase 2 — FPGA development infrastructure

Register interface, clock domains, FIFOs, timestamp counter, event system, DMA/buffering, host command channel.

### Phase 3 — ESP32 CAN integration

Prove: `ESP32 → CAN-FD → Zybo` with Field Bus (node IDs, message types, timestamps, sensor/config/command/health frames).

### Phase 4 — Hall array

Ten Hall sensors via ESP32; synchronized state `H(t) = [H0…H9]`. FPGA receives raw or processed frames per bandwidth.

### Phase 5 — S/PDIF

`PCM → S/PDIF TX → optical → RX → PCM` exact recovery.

### Phase 6 — Amplifier / subwoofer

Verified path → amp at **low** levels. Establish commanded waveform → electrical → Hall response.

### Phase 7 — MetaField adapter

Physical-state interface adapted to existing MetaField API (not a parallel simulator):

```text
physical_state = read_physical_state()
predicted_state = meta_field.step(physical_state=...)
control_state = controller(physical_state, predicted_state)
```

---

## 14. Closed-Loop Development Target

```
MetaField (predicted state)
    → Zybo ARM (orchestration)
    → Zybo FPGA (deterministic control)
    → actuator → physical response → sensors
    → ESP32 → CAN-FD → Zybo FPGA → FT601 → MetaField
    ↺
```

The experiment becomes part of the model’s state-transition loop.

---

## 15. Design Principle

| Layer | Question |
|-------|----------|
| MetaField / ProDesk | What **should** happen? |
| Zybo ARM | How should the local system be **coordinated**? |
| Zybo FPGA | What must happen **deterministically right now**? |
| ESP32 nodes | What is happening at the **distributed edge**? |
| Physical system | What **actually** happened? |

That separation is the core architectural principle.

---

## 16. Current Hardware Integration Inventory

**Host:** HP ProDesk 600 G6 Minis; Ryzen/AM4 B450M Pro4 available later  
**FPGA/SoC:** Digilent **Zybo Z7-20**  
**High-speed:** FTDI **FT601Q-B / UMFT601A-B**  
**Analog:** Pmod AD1, Pmod DA4  
**Edge:** ESP32 / ESP32-S3 / WROOM-32UE as appropriate  
**Network:** SN65HVD230 (classic), **MCP2518FD** (CAN-FD), Field Bus protocol  
**I²C:** 6× TCA9548A, ADS1115, MCP23017, MB85RC256V FRAM  
**Sense:** 10× Hall, BPW34 / optical substrate  
**Actuate:** 3 kRMS sub, amp chain, custom S/PDIF optical path  
**Lab:** KORAD KD3005D, rework tools, thermal, wiring inventory  

---

## 17. Long-Term Physical-Computational Vision

Heterogeneous substrate across CPU, optional GPU, ARM, FPGA, ESP32 edge, optical/EM interactions, sensor-derived state, and model state — with **feedback** between domains.

Not `computer → experiment`, but:

```text
computer ↔ experiment
model ↔ hardware ↔ physical system
```

---

## 18. Immediate Next Milestone

Do not expand inventory unnecessarily.

```
ZYBO Z7-20 → FPGA test logic → FT601Q-B → ProDesk Linux → capture/verification
```

Then: `ESP32 → CAN-FD → Zybo`  
Then: `Hall → CAN-FD → Zybo → FT601 → MetaField`  
Then: `MetaField → Zybo → S/PDIF/DA4 → amp → sub`  
Then close the loop.

**Build from the transport boundary outward.**
