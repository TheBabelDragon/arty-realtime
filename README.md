# arty-realtime

**Arty A7 as the hardware real-time boundary** for MetaField physical experiments.

```
FAST PHYSICAL LOOP
  Hall ×10 → ESP32 → CAN-FD → Arty A7 → S/PDIF / TOSLINK → amp → sub

SLOW MODEL LOOP
  Arty ↔ FT601 ↔ ProDesk ↔ MetaField ↔ setpoints → Arty
```

Linux is **not** in the sample path.

## Docs

| File | Contents |
|------|----------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Fast/slow loops, block diagram, design rules |
| [CLOCKS.md](CLOCKS.md) | Who owns sample time vs Field Bus TIME_SYNC |
| [MILESTONES.md](MILESTONES.md) | M0…M5 acceptance criteria |
| [SPIDF_M0.md](SPIDF_M0.md) | First project: tone → encode → optical → decode → bit-perfect |
| [INTERFACES.md](INTERFACES.md) | FT601 ↔ MetaField, Field Bus southbound, S/PDIF |

## Sibling repos

- [field-bus](https://github.com/TheBabelDragon/field-bus) — CAN-FD protocol (ESP32 ↔ A7)
- [optical-body-s3](https://github.com/TheBabelDragon/optical-body-s3) — optical node (same Field Bus)
- [metafield](https://github.com/TheBabelDragon/metafield) — slow model / memory / geometry

## Hardware target

| Piece | Role |
|-------|------|
| Digilent **Arty A7** | Real-time hub |
| **FT601Q-B** (or similar) | USB3 FIFO to ProDesk |
| **MCP2518FD** + ESP32 nodes | Field Bus edge (Hall, optical, …) |
| **SH-C31G** | Optional PC-side CAN-FD monitor |
| TOSLINK TX/RX | S/PDIF optical audio |

---

*Part of the MetaField physical-field substrate.*
