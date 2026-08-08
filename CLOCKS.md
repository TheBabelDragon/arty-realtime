# Clocks and time

## Domains

| Domain | Owner | Meaning |
|--------|--------|--------|
| **Audio / sample clock** | Arty A7 (S/PDIF master) | PCM sample index, 44.1 / 48 / 96 kHz domain |
| **Field Bus network time** | Arty A7 as TIME_MASTER (preferred) | `TIME_SYNC` on CAN-FD; ESP32 stamps observations |
| **Host wall time** | ProDesk | Logging, files, human correlation only |

MetaField may keep its own logical step counter; it must **not** pretend to be the audio sample clock.

---

## Ownership rules

1. **A7 generates S/PDIF** → A7 is the sample-clock master for that link.  
2. **A7 broadcasts Field Bus `TIME_SYNC`** so Hall / optical nodes share one network timebase.  
3. Host may *echo* or *record* times; it does not drive the fast loop’s notion of “now.”  
4. Correlation packet (A7 → host) should carry:
   - `sample_index` (or audio time µs)
   - `network_time_us` (Field Bus)
   - optional host RX timestamp (for delay measurement only)

---

## Why this matters

```
commanded PCM sample k
        ↕
magnetic field snapshot (Hall, stamped with network_time)
        ↕
inferred physical state
```

Without a single story for *k* vs network time, MetaField cannot learn the electromechanical map.

---

## Milestone expectation

- **M0:** sample clock exists inside A7 only (TX/RX loopback).  
- **M2+:** `TIME_SYNC` from A7 on Field Bus; ESP32 observations carry network time.  
- **M4+:** host receives paired `(sample_index, field_state)` for model fitting.
