"""Send measurements from Python to KymoStudio (Kymotrace binary protocol v6.2)."""
import time

from . import transport
from .protocol import crc8, frame

__all__ = ['Sender', 'frame', 'crc8', 'transport']
__version__ = '0.1.0'


class Sender:
    """Stamps each value with the time since the sender started and writes one frame.

    ``timestamps``: 'us' (wraps after 71.6 min), 'ms' (wraps after 49.7 days) or None.
    Use one unit per connection; KymoStudio treats a change as a clock restart.
    """

    def __init__(self, sink, *, timestamps: str = 'us', crc: bool = False):
        if timestamps not in ('us', 'ms', None):
            raise ValueError("timestamps must be 'us', 'ms' or None")
        self._sink, self._timestamps, self._crc = sink, timestamps, crc
        self._start = time.monotonic_ns()

    @classmethod
    def udp(cls, host, port, **kwargs):
        return cls(transport.Udp(host, port), **kwargs)

    @classmethod
    def tcp_server(cls, port, host='0.0.0.0', **kwargs):
        return cls(transport.TcpServer(port, host), **kwargs)

    @classmethod
    def serial(cls, port, baudrate=115200, **kwargs):
        return cls(transport.Serial(port, baudrate), **kwargs)

    @classmethod
    def mqtt(cls, host, topic, port=1883, *, qos=0, username=None, password=None, client_id='', **kwargs):
        return cls(transport.Mqtt(host, topic, port, qos=qos, username=username,
                                  password=password, client_id=client_id), **kwargs)

    def send(self, id: int, y: float, *, x: float = None, z: float = None):
        t = None
        if self._timestamps:
            t = (time.monotonic_ns() - self._start) // (1000 if self._timestamps == 'us' else 1_000_000)
        self._sink.write(frame(id, y, x, z, t, us=self._timestamps == 'us', crc=self._crc))

    def close(self):
        self._sink.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
