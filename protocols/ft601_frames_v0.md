# FT601 host frames v0

Minimal framing for Phase 1: FPGA test stream → FT601 → Linux verification.

Byte order: **little-endian**.  
Transport: FT601 32-bit FIFO (host sees a byte stream; pack/unpack on 4-byte boundaries when possible).

## Magic

```
0x46 0x54 0x36 0x30   // 'FT60'
```

## Header (16 bytes)

| Offset | Size | Field |
|--------|------|--------|
| 0 | 4 | magic `FT60` |
| 4 | 2 | version (`1`) |
| 6 | 2 | msg_type |
| 8 | 4 | sequence |
| 12 | 4 | payload_len (bytes after header) |

## msg_type

| Value | Name | Phase |
|-------|------|--------|
| 0x0001 | `TEST_COUNTER` | 1 |
| 0x0002 | `STATUS` | 2+ |
| 0x0010 | `FIELD_FRAME` | 4+ |
| 0x0020 | `PCM_MARK` | 5+ |
| 0x00F0 | `LOG` | any |

## TEST_COUNTER payload (16 bytes)

| Offset | Size | Field |
|--------|------|--------|
| 0 | 8 | `timestamp_ticks` (FPGA free-running counter) |
| 8 | 4 | `counter` (monotonic) |
| 12 | 4 | `reserved` (0) |

**Integrity:** host checks `sequence` contiguous and `counter == sequence` (or document offset once).

## Downlink (host → FPGA) v0

Same header. Types:

| Value | Name |
|-------|------|
| 0x8001 | `PING` |
| 0x8002 | `SET_MODE` |

Payload optional; Phase 1 may TX-only from FPGA.

## Notes

- Keep total frame size multiple of 4 when feeding 32-bit FIFO.
- Version bump if header layout changes; do not reuse type numbers with different meanings.
