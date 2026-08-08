# Phase 1 — Host verification

## Frame format

See [../../protocols/ft601_frames_v0.md](../../protocols/ft601_frames_v0.md).

## Tool

```bash
python3 verify_stream.py capture.bin
# or pipe a dump:
python3 verify_stream.py -
```

**Pass:** contiguous `sequence`, `counter == sequence` for `TEST_COUNTER` frames, exit code 0.

## FTDI / device access

Exact device path depends on FT601 driver (D3XX / libftd3xx / vendor tools).  
Until that is wired, dump a binary capture from the vendor utility and run this verifier offline.

## Lab note

Record results in [../../lab/phase1_ft601.md](../../lab/phase1_ft601.md).
