"""
Eclypse host handle — control (TCP) + data (UDP).

Does not require the board to be online to import; methods fail cleanly on connect errors.
"""

from __future__ import annotations

import socket
from typing import Iterable

from .framing import DataFrame, parse_frame


class Eclypse:
    def __init__(
        self,
        host: str,
        control_port: int = 7600,
        data_port: int = 7601,
        command_port: int = 7602,
        timeout: float = 2.0,
    ):
        self.host = host
        self.control_port = control_port
        self.data_port = data_port
        self.command_port = command_port
        self.timeout = timeout
        self._data_sock: socket.socket | None = None

    def configure(
        self,
        sample_rate: int | None = None,
        channels: Iterable[int] | None = None,
        mode: str | None = None,
    ) -> str:
        replies = []
        if sample_rate is not None:
            replies.append(self.command(f"SET_SAMPLE_RATE {int(sample_rate)}"))
        if channels is not None:
            ch = ",".join(str(int(c)) for c in channels)
            replies.append(self.command(f"SET_CHANNELS {ch}"))
        if mode is not None:
            replies.append(self.command(f"SET_MODE {mode}"))
        return "\n".join(replies)

    def start(self) -> str:
        return self.command("START_CAPTURE")

    def stop(self) -> str:
        return self.command("STOP_CAPTURE")

    def status(self) -> str:
        return self.command("GET_STATUS")

    def command(self, line: str) -> str:
        payload = (line.strip() + "\n").encode("utf-8")
        with socket.create_connection(
            (self.host, self.control_port), timeout=self.timeout
        ) as sock:
            sock.sendall(payload)
            sock.shutdown(socket.SHUT_WR)
            chunks: list[bytes] = []
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data)
        return b"".join(chunks).decode("utf-8", errors="replace").strip()

    def bind_data(self, bind: str = "0.0.0.0") -> None:
        if self._data_sock:
            self._data_sock.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((bind, self.data_port))
        s.settimeout(self.timeout)
        self._data_sock = s

    def read(self, max_bytes: int = 65535) -> DataFrame | None:
        if not self._data_sock:
            self.bind_data()
        assert self._data_sock is not None
        try:
            data, _addr = self._data_sock.recvfrom(max_bytes)
        except socket.timeout:
            return None
        return parse_frame(data)

    def close(self) -> None:
        if self._data_sock:
            self._data_sock.close()
            self._data_sock = None
