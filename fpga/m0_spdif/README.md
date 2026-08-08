# M0 — S/PDIF loopback (FPGA project home)

See [../../SPIDF_M0.md](../../SPIDF_M0.md) for pass criteria.

## Layout (fill in when Vivado / open-tool project exists)

```
m0_spdif/
├── README.md          (this file)
├── constraints/
│   └── arty_a7_spdif.xdc   # pin map for optical TX/RX PMOD
├── rtl/
│   └── (encoder, decoder, tone gen, compare)
├── sim/
│   └── (optional testbench)
└── notes.md           # crystal, PMOD part numbers, gotchas
```

## Build rule

No amp. No CAN. No FT601.  
Tone → encode → optical → decode → **bit-perfect** for ≥10 s.

When the project builds, link the bitstream path here and check off `lab/m0_results.md`.
