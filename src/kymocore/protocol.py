"""Kymotrace compact binary protocol v6.2 data frames (KymoCore PROTOCOL.md)."""
import math
import struct

SYNC = b'\xa5\x5a'


def crc8(data: bytes) -> int:
    """CRC-8/ATM: polynomial 0x07, init 0, no reflection, no xor-out."""
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


def frame(id: int, y: float, x: float = None, z: float = None, t: int = None, *,
          us: bool = False, crc: bool = False) -> bytes:
    """One data frame. ``t`` counts ms (or µs with ``us``) since the sender started."""
    if not 0 <= id <= 255:
        raise ValueError(f'channel id {id} outside 0..255')
    values = [v for v in (x, y, z) if v is not None]
    if not all(math.isfinite(v) for v in values):
        raise ValueError('NaN and infinity cannot be sent')
    if us and t is None:
        raise ValueError('microseconds need a timestamp')
    descriptor = (0x40 | (0x08 if x is not None else 0) | (0x04 if z is not None else 0)
                  | (0x02 if t is not None else 0) | (0x10 if us else 0) | (0 if crc else 0x01))
    body = bytes([descriptor, id]) + struct.pack(f'<{len(values)}f', *values)
    if t is not None:
        body += struct.pack('<I', t & 0xFFFFFFFF)  # wraps; KymoStudio continues the axis
    return SYNC + body + bytes([crc8(body) if crc else 0])
