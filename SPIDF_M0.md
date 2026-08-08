# M0 — S/PDIF TX → optical → RX → bit-perfect

## Intent

Prove the **digital audio highway** before the amp, Hall array, or MetaField enter the story.

## Block diagram

```
┌─────────────────────────────────────────┐
│                 Arty A7                 │
│                                         │
│  PCM source ──► S/PDIF encoder ──► TX pins / optical TX
│                      │                    │
│                      │              TOSLINK cable
│                      │                    │
│  comparator ◄── S/PDIF decoder ◄── RX pins / optical RX
│       │
│    mismatch cnt / LOCK LED
└─────────────────────────────────────────┘
```

Use a short optical loopback cable first (TX module → RX module). No amplifier.

## Suggested parameters (start)

| Parameter | Initial value |
|-----------|----------------|
| Sample rate | 48 kHz |
| Sample width | 16-bit (upgrade to 24-bit after lock) |
| Channels | 2 (stereo, same tone both) |
| Test signal | 1 kHz sine **or** walking bit / PRBS packed as PCM |
| Wire format | S/PDIF biphase-mark, consumer subframe |

Exact pinout depends on PMOD optical modules / FMC — document in a `boards/` note when hardware is chosen.

## Pass / fail

| Check | Pass |
|-------|------|
| RX PLL / bit lock | Stable lock LED |
| Sample match | 0 mismatches for ≥ 10 s continuous |
| Rate | Reported rate = commanded rate |
| Restart | Survives reset and re-locks |

## Deliverables

1. Vivado (or open-tool) project skeleton in this repo under `fpga/m0_spdif/` (when started)
2. Short `lab/m0_results.md` with mismatch count and scope/photo optional
3. Pin constraints file for the actual optical PMOD

## Explicit non-goals

- Volume control, DSP, filters
- CAN / Field Bus
- FT601
- “Sounds good on the sub”

When M0 passes, the highway exists. Then M1 inserts the amp.
