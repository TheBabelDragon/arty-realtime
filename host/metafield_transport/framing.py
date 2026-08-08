"""MFE0 data-plane framing (see protocols/ethernet_frames_v0.md)."""

from __future__ import annotations

import struct
from dataclasses import dataclass

MAGIC = 0x4D464530  # MFE0
VERSION = 1
HEADER_FMT = "<IHH IQ H H I I H H"
HEADER_SIZE = 36

MSG_TEST_COUNTER = 0x0001
MSG_ADC_RAW = 0x0010
MSG_ADC_FEATURE = 0x0011
MSG_COMMAND = 0x0030

PAYLOAD_INT16 = 1
PAYLOAD_FLOAT32_FEATURES = 2


@dataclass
class DataFrame:
    sequence: int
    timestamp_ticks: int
    source_id: int
    channel: int
    sample_rate_hz: int
    sample_count: int
    msg_type: int
    payload_type: int
    flags: int
    payload: bytes

    @property
    def is_test(self) -> bool:
        return self.msg_type == MSG_TEST_COUNTER


def parse_frame(data: bytes) -> DataFrame | None:
    if len(data) < HEADER_SIZE:
        return None
    magic, ver, msg_type, seq, ts, src, ch, rate, count, ptype, flags = struct.unpack(
        HEADER_FMT, data[:HEADER_SIZE]
    )
    if magic != MAGIC or ver != VERSION:
        return None
    return DataFrame(
        sequence=seq,
        timestamp_ticks=ts,
        source_id=src,
        channel=ch,
        sample_rate_hz=rate,
        sample_count=count,
        msg_type=msg_type,
        payload_type=ptype,
        flags=flags,
        payload=data[HEADER_SIZE:],
    )


def pack_header(
    *,
    msg_type: int,
    sequence: int,
    timestamp_ticks: int,
    source_id: int = 0,
    channel: int = 0,
    sample_rate_hz: int = 0,
    sample_count: int = 0,
    payload_type: int = 0,
    flags: int = 0,
) -> bytes:
    return struct.pack(
        HEADER_FMT,
        MAGIC,
        VERSION,
        msg_type,
        sequence & 0xFFFFFFFF,
        timestamp_ticks & 0xFFFFFFFFFFFFFFFF,
        source_id & 0xFFFF,
        channel & 0xFFFF,
        sample_rate_hz & 0xFFFFFFFF,
        sample_count & 0xFFFFFFFF,
        payload_type & 0xFFFF,
        flags & 0xFFFF,
    )


def pack_test_counter(sequence: int, timestamp_ticks: int) -> bytes:
    body = struct.pack("<QII", timestamp_ticks, sequence & 0xFFFFFFFF, 0)
    hdr = pack_header(
        msg_type=MSG_TEST_COUNTER,
        sequence=sequence,
        timestamp_ticks=timestamp_ticks,
        sample_count=1,
        payload_type=PAYLOAD_INT16,
    )
    return hdr + body
