# arty-realtime

**Zybo Z7-20 real-time boundary** for MetaField physical experiments  
*(repo name is historical; platform target is **Zybo Z7-20**, not Arty-only.)*

```
FAST PHYSICAL LOOP
  sensors / Hall / optical → ESP32 → CAN-FD → Zybo FPGA → S/PDIF or DA4 → amp / actuators

SLOW MODEL LOOP
  Zybo ↔ FT601 ↔ ProDesk ↔ MetaField ↔ setpoints → Zybo
```

Linux is **not** in the deterministic sample path.

## Start here

| Doc | Contents |
|-----|----------|
| **[INTEGRATION.md](INTEGRATION.md)** | **Full architecture** (roles, Zybo ARM/FPGA, FT601, CAN, Hall/sub, S/PDIF, phases) |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Fast/slow loops (summary) |
| [CLOCKS.md](CLOCKS.md) | Sample clock vs Field Bus TIME_SYNC |
| [MILESTONES.md](MILESTONES.md) | Phased pass criteria |
| [SPIDF_M0.md](SPIDF_M0.md) | S/PDIF bit-perfect optical link |
| [INTERFACES.md](INTERFACES.md) | Field Bus, FT601 sketch, MetaField boundary |

## Immediate milestone

```
Zybo Z7-20 → FPGA test stream → FT601 → USB3 → ProDesk → verify
```

Then ESP32 CAN-FD, Hall array, S/PDIF, amp, MetaField adapter — in that order.

## Sibling repos

- [field-bus](https://github.com/TheBabelDragon/field-bus) — CAN-FD protocol
- [optical-body-s3](https://github.com/TheBabelDragon/optical-body-s3) — optical edge node
- [metafield](https://github.com/TheBabelDragon/metafield) — world model / simulation

---

*Part of the MetaField physical-field substrate.*
