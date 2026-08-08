# arty-realtime

**Eclypse Z7 real-time boundary** for MetaField physical experiments  
*(repo name is historical.)*

```
FAST PHYSICAL LOOP
  Zmod Scope 1410 ×2 + ESP32/CAN-FD → Eclypse FPGA → S/PDIF → existing DAC/amp/sub

SLOW MODEL LOOP
  Eclypse ↔ FT601 ↔ ProDesk ↔ MetaField ↔ setpoints → Eclypse
```

Linux is **not** in the deterministic sample path.

## Decision record

**[docs/ADR-001-eclypse-z7-instrumentation.md](docs/ADR-001-eclypse-z7-instrumentation.md)** —  
Pivot from Zybo + Pmods → **Eclypse Z7 + 2× Zmod Scope 1410**; Zmod AWG 1411 deferred.

## Docs

| Doc | Contents |
|-----|----------|
| [INTEGRATION.md](INTEGRATION.md) | Full system architecture (update platform to Eclypse per ADR-001) |
| [docs/ADR-001-…](docs/ADR-001-eclypse-z7-instrumentation.md) | **Current hardware decision** |
| [MILESTONES.md](MILESTONES.md) | Phased pass criteria |
| [protocols/ft601_frames_v0.md](protocols/ft601_frames_v0.md) | Host FIFO framing |
| [host/phase1_ft601/](host/phase1_ft601/) | Stream verifier |
| [SPIDF_M0.md](SPIDF_M0.md) | S/PDIF bit-perfect optical link |
| [INTERFACES.md](INTERFACES.md) | Field Bus / FT601 / MetaField boundary |

## Immediate goal

Synchronized Zmod acquisition → FT601 → MetaField → S/PDIF stimulus → existing DAC/amp/sub → measure → model.  
First **MetaField ↔ FPGA ↔ physical world** closed loop.

## Sibling repos

- [field-bus](https://github.com/TheBabelDragon/field-bus)
- [optical-body-s3](https://github.com/TheBabelDragon/optical-body-s3)
- [hall-node-s3](https://github.com/TheBabelDragon/hall-node-s3)
- [metafield](https://github.com/TheBabelDragon/metafield)

---

*Part of the MetaField physical-field substrate.*
