# Phase 1 — Zynq PS gateway sketches

Runs on **Eclypse Z7 processing system** (Linux userspace). No PL / Zmod required.

| Path | Language | Role |
|------|----------|------|
| `gateway.py` | Python 3 | Fastest bring-up on PetaLinux / Ubuntu-rootfs |
| `gateway.c` | C | Lightweight; same protocol |

## Protocol

- **TCP :7600** — line commands (`GET_STATUS`, `START_CAPTURE`, …) → `OK` / `ERR`  
- **UDP → host:7601** — `MFE0` frames, `TEST_COUNTER` while capturing  

See [protocols/ethernet_frames_v0.md](../../../protocols/ethernet_frames_v0.md).

## Host verify

```bash
# on ProDesk
python3 host/phase1_ethernet/verify_udp_stream.py --seconds 10
python3 host/phase1_ethernet/control_client.py <eclypse-ip> GET_STATUS
python3 host/phase1_ethernet/control_client.py <eclypse-ip> START_CAPTURE
```

## Config

Environment / argv:

| Name | Default | Meaning |
|------|---------|--------|
| `MF_HOST` | `192.168.1.10` | ProDesk IP (UDP destination) |
| `MF_DATA_PORT` | `7601` | UDP data port on host |
| `MF_CTRL_PORT` | `7600` | TCP listen port on Eclypse |
| `MF_RATE_HZ` | `1000` | TEST_COUNTER packets per second |

## Later (Phase 2)

Replace `emit_test_counter()` with DMA-filled ADC buffers; keep the same header.
