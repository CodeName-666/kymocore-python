<p align="center">
  <a href="https://github.com/KymoTrace/kymocore-python/blob/main/README.md"><img alt="English" src="https://img.shields.io/badge/%F0%9F%8C%90-English-15123A"></a>
  <a href="https://github.com/KymoTrace/kymocore-python/blob/main/README.de.md"><img alt="Deutsch" src="https://img.shields.io/badge/%F0%9F%8C%90-Deutsch-A78BFA"></a>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/KymoTrace/kymocore/main/docs/images/kymotrace-logo-dark.svg">
    <img src="https://raw.githubusercontent.com/KymoTrace/kymocore/main/docs/images/kymotrace-logo-light.svg" alt="Kymotrace – Embedded Telemetry" width="480">
  </picture>
</p>

<h3 align="center">kymocore for Python · Measurements from your script, live on screen</h3>

<p align="center">
  Pure Python sender for the Kymotrace protocol – the PC counterpart of <b>KymoCore</b>.
</p>

<p align="center">
  <img alt="Version 0.1.0" src="https://img.shields.io/badge/version-0.1.0-7C5CFF">
  <img alt="License MIT" src="https://img.shields.io/badge/License-MIT-15123A">
  <img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-A78BFA">
  <img alt="Transports" src="https://img.shields.io/badge/UDP%20%C2%B7%20TCP%20%C2%B7%20Serial%20%C2%B7%20MQTT-FDE047">
</p>

---

## What is it about?

Not every signal comes from a microcontroller. A Raspberry Pi reads sensors,
a test bench script drives a power supply, a simulation computes a plant model.
Printing those values or writing CSV files means looking at them **afterwards**.

**kymocore** sends them to [KymoStudio](https://kymotrace.de/download.html) while
they happen, with the same compact binary frames (**9 to 21 bytes**) that the
[KymoCore](https://github.com/KymoTrace/kymocore) firmware library uses. Firmware
and PC script appear side by side in one KymoStudio workbench: as curves,
XY traces or in 3D.

<p align="center">
  <img src="https://raw.githubusercontent.com/KymoTrace/kymocore/main/docs/images/kymostudio-workbench.png" alt="KymoStudio showing measurements live as a time series and an XY chart" width="900">
  <br><sub>Live data in KymoStudio: three signals over time, two as XY traces.</sub>
</p>

## What kymocore can do

| | |
|---|---|
| **One call per value** | `send(channel, value)`, optionally with `x=` and `z=` for XY and XYZ charts. Up to 256 channels. |
| **Timestamps included** | Each value carries the time since the sender started, in microseconds or milliseconds, from a monotonic clock. |
| **Four transports** | UDP, TCP, serial/USB and MQTT. KymoStudio's existing sources receive them unchanged. |
| **No dependencies** | The core uses only the standard library. `pyserial` and `paho-mqtt` are optional extras. |
| **Same protocol as the firmware** | Tested against the golden vectors of [PROTOCOL.md](https://github.com/KymoTrace/kymocore/blob/main/PROTOCOL.md) v6.2, optional CRC-8 checksum. |
| **Raw frames too** | `frame()` returns the bytes for a transport of your own. |

## What it is used for

- **Raspberry Pi and single-board computers:** plot sensor values read via I²C, SPI or GPIO live.
- **Test benches and HIL setups:** show the script's setpoints next to the measurements of the device under test.
- **Simulations:** watch a plant model or controller simulation run, with the same charts as on real hardware.
- **Data from other programs:** forward values from instruments, logs or APIs to KymoStudio.

## Quick start

```bash
pip install kymocore            # UDP and TCP
pip install kymocore[serial]    # + serial / USB CDC (pyserial)
pip install kymocore[mqtt]      # + MQTT (paho-mqtt)
```

### Complete example

The following script sends a sine wave on channel 0 and a cosine with an X
coordinate on channel 1, every 10 ms for ten seconds.

```python
import math
import time

from kymocore import Sender

with Sender.udp('127.0.0.1', 5025) as sender:
    for i in range(1000):
        sender.send(0, math.sin(i / 20))           # channel 0, value
        sender.send(1, math.cos(i / 20), x=i)      # channel 1, XY point
        time.sleep(.01)
```

In KymoStudio, add a **UDP** source on port 5025, start it and assign
channel 0 to a chart.

## Transports

| Transport | Call | KymoStudio source |
|---|---|---|
| UDP | `Sender.udp(host, port)` | UDP, listens on `port` |
| TCP | `Sender.tcp_server(port)` | Telnet/TCP, connects to this machine and `port` |
| Serial | `Sender.serial('COM4', 115200)` | Serial, same baud rate |
| MQTT | `Sender.mqtt(broker, topic)` | MQTT, `topic` among its receive topics |

KymoStudio connects to a TCP device, so `tcp_server` listens and sends to every
connected client. Values sent while no client is connected are dropped, as on a
device. MQTT publishes one message per value.

## Options

| Option | Default | Meaning |
|---|---|---|
| `timestamps='us'` | yes | Microseconds; wraps after 71.6 minutes, KymoStudio continues the time axis |
| `timestamps='ms'` | | Milliseconds; wraps after 49.7 days |
| `timestamps=None` | | No timestamp; KymoStudio stamps on arrival |
| `crc=True` | off | Adds the CRC-8/ATM checksum to every frame |

Channel IDs outside 0–255 and NaN or infinite values raise `ValueError`.
Microsecond timestamps need KymoStudio 2.5 or newer.

## Part of Kymotrace

| Project | Role |
|---|---|
| [KymoCore](https://github.com/KymoTrace/kymocore) | firmware library: capture and send measurements on the microcontroller |
| **[kymocore for Python](https://github.com/KymoTrace/kymocore-python)** | this package: send measurements from Python |
| [KymoProbe](https://github.com/KymoTrace/kymoprobe) | firmware and hardware examples for ESP32, Arduino and STM32 |
| [KymoStudio](https://kymotrace.de/download.html) | desktop app: receive, display, analyse, export |

## Documentation

- **[Protocol](https://github.com/KymoTrace/kymocore/blob/main/PROTOCOL.md):** byte layout, CRC, example frames
- **[Website](https://kymotrace.de):** KymoStudio download, guides and features

## License

Copyright (c) 2026 Christof Seidel. kymocore for Python is licensed under the
[MIT license](https://github.com/KymoTrace/kymocore-python/blob/main/LICENSE):
free for any use, including commercial projects, without disclosing your own
source code.
