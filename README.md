# kymocore for Python

Send measurements from a Python script (Raspberry Pi, test bench, PC simulation)
to [KymoStudio](https://kymotrace.de) with the same binary protocol as the
KymoCore firmware library ([PROTOCOL.md](https://github.com/CodeName-666/kymocore/blob/main/PROTOCOL.md), v6.2).
Firmware and PC script share one KymoStudio time axis.

```bash
pip install kymocore            # UDP, TCP
pip install kymocore[serial]    # + serial / USB CDC (pyserial)
pip install kymocore[mqtt]      # + MQTT (paho-mqtt)
```

```python
import math, time
from kymocore import Sender

with Sender.udp('127.0.0.1', 5025) as s:     # KymoStudio: UDP source on port 5025
    for i in range(1000):
        s.send(0, math.sin(i / 20))            # channel 0, value
        s.send(1, math.cos(i / 20), x=i)       # with X for XY charts
        time.sleep(.01)
```

| Transport | Call | KymoStudio source |
|---|---|---|
| UDP | `Sender.udp(host, port)` | UDP, listens on `port` |
| TCP | `Sender.tcp_server(port)` | Telnet/TCP, connects to this machine and `port` |
| Serial | `Sender.serial('COM4', 115200)` | Serial |
| MQTT | `Sender.mqtt(broker, topic)` | MQTT, `topic` among its receive topics |

Each value carries the time since the sender started: microseconds by default
(`timestamps='ms'` for runs over 71 minutes without wrap, `None` to let
KymoStudio stamp on arrival). `crc=True` adds the CRC-8 checksum.
Channel IDs are 0–255; NaN and infinity raise `ValueError`.

`kymocore.frame(id, y, x=None, z=None, t=None, us=False, crc=False)` returns the
raw frame bytes for your own transport.

License: MIT.
