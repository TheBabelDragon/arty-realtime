# Architecture

## Two loops

### Fast physical loop (FPGA owns latency)

```
commanded audio / control
        │
        ▼
   Arty A7  ──S/PDIF TX──► TOSLINK ──► amplifier ──► sub
        ▲
        │
   Field Bus (CAN-FD)
        ▲
        │
   ESP32 + Hall ×10 (and later optical / other nodes)
        ▲
        │
   magnetic (or optical) reality
```

Target: deterministic path from measurement-related decisions to actuation.  
**No Linux scheduler in this path.**

### Slow model loop (ProDesk owns intelligence)

```
Arty A7
   │  FT601 (USB3 FIFO)
   ▼
ProDesk
   │
   ▼
MetaField  (state, geometry, HMC, memory, predicted response)
   │
   ▼
setpoints / mode / excitation plans
   │  FT601
   ▼
Arty A7
```

MetaField updates the *model* and high-level policy.  
It does not bit-bang S/PDIF sample clocks.

---

## Design rules

1. **Southbound edge language is Field Bus** ([field-bus](https://github.com/TheBabelDragon/field-bus)).  
   Hall node, optical node, future nodes — same HELLO / STATUS / TIME_SYNC / telemetry / commands.

2. **Northbound host language is FT601 frames** (see INTERFACES.md).  
   MetaField never speaks raw CAN or raw S/PDIF.

3. **Audio highway is S/PDIF** on the A7.  
   First prove TX→optical→RX bit-perfect, then insert the amp.

4. **Two clocks, one correlation story** (see CLOCKS.md).  
   Sample index / audio time vs network time must be reconcilable.

5. **Incremental hardware.**  
   Do not build “the entire audio driver.” Ship M0 before M1.

---

## What runs where

| Function | Where |
|----------|--------|
| S/PDIF encode / decode | Arty A7 |
| PCM tone / buffer / light DSP | Arty A7 |
| CAN-FD Field Bus master (or bridge) | Arty A7 |
| Hall sampling | ESP32 node |
| Optical body sense / lasers | ESP32 node |
| Geometry, HMC, FieldMemory, prediction | MetaField on ProDesk |
| Logging / visualization | ProDesk |

---

## Explicit non-goals (for now)

- Running full MetaField *on* the FPGA
- Replacing Field Bus with a one-off binary protocol per experiment
- Playing host WAV files as the primary closed-loop source once the A7 path exists
