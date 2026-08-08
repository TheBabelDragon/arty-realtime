# arty-realtime

**Eclypse Z7 real-time boundary** for MetaField physical experiments  
*(repo name is historical.)*

```
FAST PHYSICAL LOOP
  Zmod 1410 ×2 + ESP32/CAN-FD → Eclypse PL → (S/PDIF → DAC/amp/sub)

HOST LINK (initial)
  Eclypse PS ↔ Gigabit Ethernet ↔ ProDesk / MetaField
  Control: TCP · Data: UDP · timestamps mandatory
```

**FT601 is deferred** — see ADR-002.

## Decision records

| ADR | Decision |
|-----|----------|
| [ADR-001](docs/ADR-001-eclypse-z7-instrumentation.md) | Eclypse Z7 + 2× Zmod Scope 1410; Pmods / 1411 deferred |
| [ADR-002](docs/ADR-002-ethernet-not-ft601.md) | **Ethernet not FT601**; TCP control + UDP data; FT601 only if measured bottleneck |

## Docs

| Doc | Contents |
|-----|----------|
| [INTEGRATION.md](INTEGRATION.md) | System architecture |
| [protocols/ethernet_frames_v0.md](protocols/ethernet_frames_v0.md) | **Primary** host framing |
| [host/phase1_ethernet/](host/phase1_ethernet/) | UDP stream verifier |
| [MILESTONES.md](MILESTONES.md) | Phased pass criteria |
| [protocols/ft601_frames_v0.md](protocols/ft601_frames_v0.md) | Optional / future only |

## Immediate goal

Eclypse → Ethernet → MetaField, then Zmod acquisition, CAN sync, S/PDIF stimulus, closed loop.  
Add USB3 FIFO only if Ethernet is proven limiting.

## Sibling repos

- [field-bus](https://github.com/TheBabelDragon/field-bus)
- [optical-body-s3](https://github.com/TheBabelDragon/optical-body-s3)
- [hall-node-s3](https://github.com/TheBabelDragon/hall-node-s3)
- [metafield](https://github.com/TheBabelDragon/metafield)
