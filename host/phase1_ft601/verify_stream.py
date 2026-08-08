#!/usr/bin/env python3
"""
Phase 1 — verify FT601 test stream from Zybo.

Reads a byte stream (file or stdin). Expects FT60 framed TEST_COUNTER messages.

Usage:
  python verify_stream.py capture.bin
  cat /dev/ft601... | python verify_stream.py -

When FTDI drivers expose a device node or you dump via their tools, point this at the dump.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

MAGIC = b"FT60"
HEADER_FMT = "<4sHHI I"  # magic, version, msg_type, sequence, payload_len
HEADER_SIZE = 16
TEST_COUNTER = 0x0001
TEST_PAYLOAD_FMT = "<QII"  # timestamp_ticks, counter, reserved
TEST_PAYLOAD_SIZE = 16


def read_exact(f, n: int) -> bytes | None:
    buf = b""
    while len(buf) < n:
        chunk = f.read(n - len(buf))
        if not chunk:
            return None if not buf else buf  # short
        buf += chunk
    return buf


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify Phase-1 FT601 TEST_COUNTER stream")
    ap.add_argument("source", help="capture file or - for stdin")
    ap.add_argument("--max-frames", type=int, default=0, help="stop after N frames (0=all)")
    args = ap.parse_args()

    f = sys.stdin.buffer if args.source == "-" else Path(args.source).open("rb")

    frames = 0
    mismatches = 0
    gaps = 0
    last_seq: int | None = None
    sync_skips = 0

    try:
        while True:
            if args.max_frames and frames >= args.max_frames:
                break

            # Resync on magic
            window = read_exact(f, 4)
            if window is None or len(window) < 4:
                break
            if window != MAGIC:
                # slide one byte
                rest = window[1:]
                b = f.read(1)
                if not b:
                    break
                # inefficient but fine for lab dumps
                f.seek(f.tell() - 3) if f.seekable() else None
                sync_skips += 1
                # simpler path for non-seekable: require aligned stream
                if not hasattr(f, "seek") or not f.seekable():
                    # consume until magic found
                    buf = window + b
                    while True:
                        idx = buf.find(MAGIC)
                        if idx >= 0:
                            buf = buf[idx:]
                            while len(buf) < 4:
                                c = f.read(1)
                                if not c:
                                    print("EOF while syncing")
                                    return 1
                                buf += c
                            window = buf[:4]
                            extra = buf[4:]
                            break
                        c = f.read(1)
                        if not c:
                            print("EOF while syncing")
                            return 1
                        buf = buf[1:] + c
                    hdr_rest = read_exact(f, HEADER_SIZE - 4)
                    if extra:
                        # push extra back not supported; require aligned captures for non-seekable
                        pass
                    if hdr_rest is None or len(hdr_rest) < HEADER_SIZE - 4:
                        break
                    header = window + hdr_rest
                else:
                    continue
            else:
                hdr_rest = read_exact(f, HEADER_SIZE - 4)
                if hdr_rest is None or len(hdr_rest) < HEADER_SIZE - 4:
                    break
                header = window + hdr_rest

            magic, version, msg_type, sequence, payload_len = struct.unpack(
                "<4sHHII", header
            )
            if magic != MAGIC:
                sync_skips += 1
                continue
            if version != 1:
                print(f"bad version {version} seq={sequence}")
                mismatches += 1

            payload = read_exact(f, payload_len) if payload_len else b""
            if payload is None or len(payload) < payload_len:
                print("truncated payload")
                break

            if last_seq is not None and sequence != (last_seq + 1) & 0xFFFFFFFF:
                gaps += 1
                print(f"seq gap: {last_seq} -> {sequence}")
            last_seq = sequence

            if msg_type == TEST_COUNTER:
                if payload_len < TEST_PAYLOAD_SIZE:
                    print(f"short TEST_COUNTER payload seq={sequence}")
                    mismatches += 1
                else:
                    ts, counter, _res = struct.unpack(
                        TEST_PAYLOAD_FMT, payload[:TEST_PAYLOAD_SIZE]
                    )
                    if counter != sequence:
                        mismatches += 1
                        print(
                            f"counter mismatch seq={sequence} counter={counter} ts={ts}"
                        )
            frames += 1
            if frames % 1000 == 0:
                print(f"... {frames} frames ok gaps={gaps} mismatches={mismatches}")
    finally:
        if f is not sys.stdin.buffer:
            f.close()

    print(
        f"done frames={frames} gaps={gaps} mismatches={mismatches} sync_skips≈{sync_skips}"
    )
    if frames == 0:
        return 2
    if gaps or mismatches:
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
