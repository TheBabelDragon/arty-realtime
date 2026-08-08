# Phase 1 — Eclypse PS Ethernet gateway (no Zmod required yet)

## Goal

Zynq **PS** emits UDP `MFE0` / `TEST_COUNTER` frames and answers TCP control lines.

PL / Zmod not required for Phase 1 pass.

## Suggested minimal userspace (Linux on PS)

1. TCP server on port **7600** — parse `GET_STATUS`, `START_CAPTURE`, …; reply `OK` / `ERR`  
2. UDP sender to host:7601 — `pack_test_counter(seq, timestamp)` at a fixed rate  
3. Free-running monotonic counter for `timestamp_ticks`

When Phase 2 starts, replace test payload with DMA-backed ADC frames; keep the same header.

## Pass

Host:

```bash
python3 host/phase1_ethernet/verify_udp_stream.py --seconds 10
```

→ **PASS**

Optional: `control_client.py … GET_STATUS` → `OK`.
