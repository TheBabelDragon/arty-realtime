# Phase 1 — Ethernet transport (Eclypse ↔ host)

Per [ADR-002](../../docs/ADR-002-ethernet-not-ft601.md).

## Tools

| Script | Role |
|--------|------|
| `verify_udp_stream.py` | Listen UDP:7601, check `MFE0` sequence integrity |
| `control_client.py` | TCP:7600 one-shot commands |

```bash
# data plane (board emitting TEST_COUNTER)
python3 verify_udp_stream.py --port 7601 --seconds 10

# control plane (board running a line-protocol daemon)
python3 control_client.py 192.168.1.50 GET_STATUS
python3 control_client.py 192.168.1.50 SET_SAMPLE_RATE 1000000
python3 control_client.py 192.168.1.50 START_CAPTURE
```

## Higher-level API

See [../metafield_transport/](../metafield_transport/) (`Eclypse` class).

## Lab

[../../lab/phase1_ethernet.md](../../lab/phase1_ethernet.md)
