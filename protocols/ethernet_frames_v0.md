# Eclypse ↔ MetaField Ethernet frames v0

Per [ADR-002](../docs/ADR-002-ethernet-not-ft601.md).

## Planes

| Plane | Transport | Use |
|-------|-----------|-----|
| Control | **TCP** | SET_*, START/STOP, GET_STATUS |
| Data | **UDP** | acquisition frames, feature frames, command/waveform payloads |

Default ports (lab defaults — change in config):

- TCP control: `7600`
- UDP data uplink (Eclypse → host): `7601`
- UDP data downlink (host → Eclypse): `7602`

## Data-plane frame (little-endian)

| Offset | Size | Field |
|--------|------|--------|
| 0 | 4 | magic `0x4D464530` (`MFE0`) |
| 4 | 2 | version (`1`) |
| 6 | 2 | msg_type |
| 8 | 4 | sequence |
| 12 | 8 | timestamp_ticks (acquisition clock) |
| 20 | 2 | source_id |
| 22 | 2 | channel |
| 24 | 4 | sample_rate_hz |
| 28 | 4 | sample_count |
| 32 | 2 | payload_type |
| 34 | 2 | flags |
| 36 | N | payload |

### msg_type (data plane)

| Value | Name |
|-------|------|
| 0x0001 | `TEST_COUNTER` |
| 0x0010 | `ADC_RAW` |
| 0x0011 | `ADC_FEATURE` |
| 0x0012 | `ADC_HYBRID` |
| 0x0020 | `HALL_SUMMARY` |
| 0x0030 | `COMMAND` |
| 0x0031 | `WAVEFORM_MARK` |

### payload_type

| Value | Name |
|-------|------|
| 1 | `INT16_SAMPLES` |
| 2 | `FLOAT32_FEATURES` |
| 3 | `MIXED` |

**Integrity:** host checks `sequence` continuity; correlation uses `timestamp_ticks`, never socket RX time alone.

## Control plane (TCP)

Text or binary later; v0 may use simple line commands:

```
SET_SAMPLE_RATE 1000000
SET_CHANNELS 0,1,2,3
SET_MODE FEATURE
START_CAPTURE
STOP_CAPTURE
GET_STATUS
```

Replies: `OK …` / `ERR …`.

## TEST_COUNTER payload (Phase 1)

8-byte timestamp + 4-byte counter + 4 reserved — same spirit as old FT601 test; proves PS↔host path before Zmod.
