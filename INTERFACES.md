# Interface contracts

## 1. Field Bus (A7 ↔ ESP32 nodes)

**Spec:** [TheBabelDragon/field-bus](https://github.com/TheBabelDragon/field-bus)

| Direction | Messages (initial) |
|-----------|---------------------|
| A7 → nodes | `TIME_SYNC`, commands (`CONFIG_SET`, later excitation-related) |
| Nodes → A7 | `NODE_HELLO`, `NODE_STATUS`, sensor telemetry / Hall frames, optical observations (compact) |

A7 should set capability / role as **TIME_MASTER** when it owns network time.

Node ID suggestions remain:

| ID | Role |
|----|------|
| 0x01 | Host / coordinator (PC via SH-C31G **or** A7 logical host) |
| 0x02 | Optical |
| 0x03 | Sensor / Hall |
| … | … |

Until A7 CAN-FD is up, SH-C31G may act as monitor-only on the same bus.

---

## 2. S/PDIF (A7 ↔ amp / optical audio)

| Direction | Content |
|-----------|---------|
| TX | PCM samples + embedded clock (A7 master) |
| RX | Optional monitor / loopback / external source |

No MetaField headers on the optical fiber — pure S/PDIF.

---

## 3. FT601 (A7 ↔ ProDesk / MetaField)

Bulk USB3 FIFO. Exact frame layout will version; **v0 sketch:**

### Host ← A7 (uplink)

```
uint32  magic       // e.g. 'ARTF'
uint16  version     // 1
uint16  msg_type    // STATUS / FIELD_FRAME / PCM_MARK / LOG
uint32  sample_index
uint32  network_time_us
uint16  payload_len
uint8   payload[]
```

### Host → A7 (downlink)

```
uint32  magic
uint16  version
uint16  msg_type    // SETPOINT / MODE / TONE_PARAM / SYNC_POLICY
uint32  seq
uint16  payload_len
uint8   payload[]
```

Refine when FT601 bring-up starts; do not block M0 on this.

---

## 4. What MetaField sees

MetaField should depend on:

- **measured state** (field distribution, optional optical summaries)
- **time indices** (`sample_index`, `network_time_us`)
- **commands it issued** (setpoints)

It should **not** depend on:

- ESP32 GPIO maps
- S/PDIF biphase details
- CAN arbitration bitfields

Those stay below the FT601 contract.

---

## 5. Stability rule

New experimental hardware attaches **south** of the A7 (Field Bus or direct FPGA I/O).  
Northbound FT601 message *types* may grow; existing types stay backward compatible when possible.
