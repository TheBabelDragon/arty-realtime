#!/usr/bin/env python3
"""
Phase 1 — TCP control-plane client for Eclypse PS.

Lab defaults (protocols/ethernet_frames_v0.md):
  TCP control port 7600

Usage:
  python control_client.py 192.168.1.50 GET_STATUS
  python control_client.py 192.168.1.50 SET_SAMPLE_RATE 1000000
  python control_client.py 192.168.1.50 START_CAPTURE
"""

from __future__ import annotations

import argparse
import socket
import sys

DEFAULT_PORT = 7600


def send_command(host: str, port: int, line: str, timeout: float = 2.0) -> str:
    payload = (line.strip() + "\n").encode("utf-8")
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.sendall(payload)
        sock.shutdown(socket.SHUT_WR)
        chunks: list[bytes] = []
        while True:
            data = sock.recv(4096)
            if not data:
                break
            chunks.append(data)
    return b"".join(chunks).decode("utf-8", errors="replace").strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Eclypse TCP control client")
    ap.add_argument("host", help="Eclypse PS IP")
    ap.add_argument("command", nargs="+", help="e.g. GET_STATUS or SET_SAMPLE_RATE 1e6")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args()

    line = " ".join(args.command)
    try:
        reply = send_command(args.host, args.port, line)
    except OSError as e:
        print(f"ERR connect: {e}", file=sys.stderr)
        return 1

    print(reply if reply else "(empty reply)")
    if reply.upper().startswith("ERR"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
