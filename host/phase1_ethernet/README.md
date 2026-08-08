# Phase 1 — Ethernet transport verify

Per ADR-002: **no FT601 required**.

```bash
python3 verify_udp_stream.py --port 7601 --seconds 10
```

Eclypse PS should emit `MFE0` UDP frames (`TEST_COUNTER` until Zmod is online).

Lab sheet: [../../lab/phase1_ethernet.md](../../lab/phase1_ethernet.md)
