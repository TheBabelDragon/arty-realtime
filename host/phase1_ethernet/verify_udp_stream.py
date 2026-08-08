#!/usr/bin/env python3
"""
Phase 1 — verify Eclypse UDP data-plane TEST_COUNTER (or MFE0 frames).

Usage:
  python verify_udp_stream.py --port 7601 --seconds 10
"""

from __future__ import annotations

import argparse
import socket
import struct
import time

MAGIC = 0x4D464530  # MFE0
HEADER_FMT = "<IHH IQ H H I I H H"
# magic, ver, msg_type, seq, ts, source, channel, rate, count, payload_type, flags
HEADER_SIZE = 36
TEST_COUNTER = 0x0001


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=7601)
    ap.add_argument("--seconds", type=float, default=10.0)
    ap.add_argument("--bind", default="0.0.0.0")
    args = ap.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.bind, args.port))
    sock.settimeout(1.0)

    frames = 0
    gaps = 0
    bad = 0
    last_seq: int | None = None
    t_end = time.time() + args.seconds

    print(f"listening UDP {args.bind}:{args.port} for {args.seconds}s…")

    while time.time() < t_end:
        try:
            data, addr = sock.recvfrom(65535)
        except socket.timeout:
            continue

        if len(data) < HEADER_SIZE:
            bad += 1
            continue

        magic, ver, msg_type, seq, ts, src, ch, rate, count, ptype, flags = struct.unpack(
            HEADER_FMT, data[:HEADER_SIZE]
        )
        if magic != MAGIC or ver != 1:
            bad += 1
            continue

        if last_seq is not None and seq != (last_seq + 1) & 0xFFFFFFFF:
            gaps += 1
            print(f"gap {last_seq} -> {seq} from {addr}")
        last_seq = seq
        frames += 1

        if msg_type == TEST_COUNTER and len(data) >= HEADER_SIZE + 16:
            ts2, counter, _ = struct.unpack("<QII", data[HEADER_SIZE : HEADER_SIZE + 16])
            if counter != seq:
                bad += 1
                print(f"counter mismatch seq={seq} counter={counter}")

        if frames % 500 == 0:
            print(f"… frames={frames} gaps={gaps} bad={bad}")

    sock.close()
    print(f"done frames={frames} gaps={gaps} bad={bad}")
    if frames == 0:
        return 2
    if gaps or bad:
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
