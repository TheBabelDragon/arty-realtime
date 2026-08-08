#!/usr/bin/env python3
"""
Eclypse Z7 PS Phase-1 gateway (Python).

- TCP control server on 7600
- UDP TEST_COUNTER stream to MetaField host while capturing

Run on the board:
  export MF_HOST=192.168.1.10
  python3 gateway.py
"""

from __future__ import annotations

import os
import socket
import struct
import threading
import time

MAGIC = 0x4D464530  # MFE0
VERSION = 1
HEADER_FMT = "<IHH IQ H H I I H H"
MSG_TEST_COUNTER = 0x0001

HOST = os.environ.get("MF_HOST", "192.168.1.10")
DATA_PORT = int(os.environ.get("MF_DATA_PORT", "7601"))
CTRL_PORT = int(os.environ.get("MF_CTRL_PORT", "7600"))
RATE_HZ = float(os.environ.get("MF_RATE_HZ", "1000"))

_state = {
    "capturing": False,
    "sample_rate": 1_000_000,
    "channels": [0, 1, 2, 3],
    "mode": "RAW",
    "sequence": 0,
    "lock": threading.Lock(),
}


def monotonic_ticks() -> int:
    # Placeholder acquisition clock — replace with PL timer mmap later
    return time.monotonic_ns()


def pack_test_counter(sequence: int, timestamp_ticks: int) -> bytes:
    hdr = struct.pack(
        HEADER_FMT,
        MAGIC,
        VERSION,
        MSG_TEST_COUNTER,
        sequence & 0xFFFFFFFF,
        timestamp_ticks & 0xFFFFFFFFFFFFFFFF,
        0,  # source_id (PS test)
        0,  # channel
        int(_state["sample_rate"]) & 0xFFFFFFFF,
        1,  # sample_count
        1,  # payload_type INT16
        0,  # flags
    )
    body = struct.pack("<QII", timestamp_ticks, sequence & 0xFFFFFFFF, 0)
    return hdr + body


def handle_line(line: str) -> str:
    parts = line.strip().split()
    if not parts:
        return "ERR empty"
    cmd = parts[0].upper()

    with _state["lock"]:
        if cmd == "GET_STATUS":
            return (
                f"OK capturing={int(_state['capturing'])} "
                f"seq={_state['sequence']} "
                f"rate={_state['sample_rate']} "
                f"mode={_state['mode']} "
                f"channels={','.join(map(str, _state['channels']))}"
            )
        if cmd == "START_CAPTURE":
            _state["capturing"] = True
            return "OK START_CAPTURE"
        if cmd == "STOP_CAPTURE":
            _state["capturing"] = False
            return "OK STOP_CAPTURE"
        if cmd == "SET_SAMPLE_RATE" and len(parts) >= 2:
            _state["sample_rate"] = int(float(parts[1]))
            return f"OK sample_rate={_state['sample_rate']}"
        if cmd == "SET_CHANNELS" and len(parts) >= 2:
            _state["channels"] = [int(x) for x in parts[1].split(",") if x != ""]
            return f"OK channels={_state['channels']}"
        if cmd == "SET_MODE" and len(parts) >= 2:
            _state["mode"] = parts[1].upper()
            return f"OK mode={_state['mode']}"
        if cmd == "PING":
            return "OK PONG"

    return f"ERR unknown command: {cmd}"


def control_server() -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", CTRL_PORT))
    srv.listen(4)
    print(f"[ctrl] TCP listening on 0.0.0.0:{CTRL_PORT}")

    while True:
        conn, addr = srv.accept()
        with conn:
            data = b""
            while True:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                data += chunk
                if b"\n" in data:
                    break
            line = data.decode("utf-8", errors="replace").splitlines()[0] if data else ""
            reply = handle_line(line) + "\n"
            conn.sendall(reply.encode("utf-8"))
            print(f"[ctrl] {addr}: {line!r} -> {reply.strip()}")


def data_emitter() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    period = 1.0 / max(RATE_HZ, 1.0)
    print(f"[data] UDP -> {HOST}:{DATA_PORT} at {RATE_HZ} Hz (when capturing)")

    next_t = time.monotonic()
    while True:
        with _state["lock"]:
            capturing = _state["capturing"]
            if capturing:
                seq = _state["sequence"]
                _state["sequence"] = (seq + 1) & 0xFFFFFFFF
            else:
                seq = None

        if seq is not None:
            pkt = pack_test_counter(seq, monotonic_ticks())
            try:
                sock.sendto(pkt, (HOST, DATA_PORT))
            except OSError as e:
                print(f"[data] send error: {e}")

        next_t += period
        sleep = next_t - time.monotonic()
        if sleep > 0:
            time.sleep(sleep)
        else:
            next_t = time.monotonic()


def main() -> None:
    print("MetaField Eclypse PS gateway (Phase 1 Python)")
    print(f"  host={HOST} data_port={DATA_PORT} ctrl_port={CTRL_PORT}")
    threading.Thread(target=control_server, daemon=True).start()
    data_emitter()  # main thread


if __name__ == "__main__":
    main()
