# Phase 1 — FPGA side (Zybo Z7-20 + FT601)

## Goal

Emit continuous `TEST_COUNTER` frames (see `protocols/ft601_frames_v0.md`) into the FT601 32-bit FIFO.

## Suggested blocks

1. Free-running timestamp counter  
2. Frame builder (magic, version, type, seq, payload)  
3. FT601 master / FIFO writer (per Digilent + FTDI reference)  
4. Optional LEDs: link active, frame pulse  

## Layout (fill when Vivado project exists)

```
phase1_ft601/
├── README.md
├── constraints/
├── rtl/
├── bd/          # optional block design
└── notes.md
```

## Pass

Host `verify_stream.py` reports PASS for ≥10 s of capture.

Do not start Phase 3 (CAN) until this is checked off in `lab/phase1_ft601.md`.
