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

<h3 align="center">kymocore für Python · Messwerte aus deinem Skript, live auf dem Bildschirm</h3>

<p align="center">
  Reiner Python-Sender für das Kymotrace-Protokoll – das PC-Gegenstück zu <b>KymoCore</b>.
</p>

<p align="center">
  <img alt="Version 0.1.0" src="https://img.shields.io/badge/version-0.1.0-7C5CFF">
  <img alt="Lizenz MIT" src="https://img.shields.io/badge/Lizenz-MIT-15123A">
  <img alt="Python 3.9+" src="https://img.shields.io/badge/Python-3.9%2B-A78BFA">
  <img alt="Transporte" src="https://img.shields.io/badge/UDP%20%C2%B7%20TCP%20%C2%B7%20Seriell%20%C2%B7%20MQTT-FDE047">
</p>

---

## Worum geht es?

Nicht jedes Signal kommt aus einem Mikrocontroller. Ein Raspberry Pi liest
Sensoren, ein Prüfstandsskript steuert ein Netzteil, eine Simulation rechnet ein
Streckenmodell. Wer diese Werte ausgibt oder in CSV-Dateien schreibt, sieht sie
erst **hinterher**.

**kymocore** schickt sie an [KymoStudio](https://kymotrace.de/de/#download),
während sie entstehen, mit denselben kompakten Binär-Frames (**9 bis 21 Byte**)
wie die Firmware-Library [KymoCore](https://github.com/KymoTrace/kymocore).
Firmware und PC-Skript erscheinen nebeneinander in einer KymoStudio-Arbeitsfläche:
als Kurven, XY-Spuren oder in 3D.

<p align="center">
  <img src="https://raw.githubusercontent.com/KymoTrace/kymocore/main/docs/images/kymostudio-workbench.png" alt="KymoStudio zeigt Messwerte live als Zeitverlauf und XY-Diagramm" width="900">
  <br><sub>Live-Daten in KymoStudio: drei Signale über die Zeit, zwei davon als XY-Spur.</sub>
</p>

## Was kymocore kann

| | |
|---|---|
| **Ein Aufruf pro Wert** | `send(kanal, wert)`, optional mit `x=` und `z=` für XY- und XYZ-Diagramme. Bis zu 256 Kanäle. |
| **Zeitstempel inklusive** | Jeder Wert trägt die Zeit seit dem Start des Senders, in Mikro- oder Millisekunden, von einer monotonen Uhr. |
| **Vier Transporte** | UDP, TCP, Seriell/USB und MQTT. Die vorhandenen Quellen in KymoStudio empfangen sie unverändert. |
| **Keine Abhängigkeiten** | Der Kern nutzt nur die Standardbibliothek. `pyserial` und `paho-mqtt` sind optionale Extras. |
| **Dasselbe Protokoll wie die Firmware** | Geprüft gegen die Golden Vectors aus [PROTOCOL.md](https://github.com/KymoTrace/kymocore/blob/main/PROTOCOL.md) v6.2, optionale CRC-8-Prüfsumme. |
| **Auch rohe Frames** | `frame()` liefert die Bytes für einen eigenen Transport. |

## Wofür man es einsetzt

- **Raspberry Pi und Einplatinenrechner:** über I²C, SPI oder GPIO gelesene Sensorwerte live plotten.
- **Prüfstände und HIL-Aufbauten:** Sollwerte des Skripts neben den Messwerten des Prüflings zeigen.
- **Simulationen:** ein Streckenmodell oder eine Reglersimulation mit denselben Diagrammen wie auf echter Hardware verfolgen.
- **Daten aus anderen Programmen:** Werte von Messgeräten, Logs oder APIs an KymoStudio weiterreichen.

## Schnellstart

```bash
pip install kymocore            # UDP und TCP
pip install kymocore[serial]    # + Seriell / USB CDC (pyserial)
pip install kymocore[mqtt]      # + MQTT (paho-mqtt)
```

### Vollständiges Beispiel

Das folgende Skript sendet zehn Sekunden lang alle 10 ms einen Sinus auf Kanal 0
und einen Kosinus mit X-Koordinate auf Kanal 1.

```python
import math
import time

from kymocore import Sender

with Sender.udp('127.0.0.1', 5025) as sender:
    for i in range(1000):
        sender.send(0, math.sin(i / 20))           # Kanal 0, Wert
        sender.send(1, math.cos(i / 20), x=i)      # Kanal 1, XY-Punkt
        time.sleep(.01)
```

In KymoStudio eine **UDP**-Quelle auf Port 5025 anlegen, starten und Kanal 0
einem Diagramm zuweisen.

## Transporte

| Transport | Aufruf | Quelle in KymoStudio |
|---|---|---|
| UDP | `Sender.udp(host, port)` | UDP, lauscht auf `port` |
| TCP | `Sender.tcp_server(port)` | Telnet/TCP, verbindet sich mit diesem Rechner und `port` |
| Seriell | `Sender.serial('COM4', 115200)` | Seriell, gleiche Baudrate |
| MQTT | `Sender.mqtt(broker, topic)` | MQTT, `topic` unter den Empfangs-Topics |

KymoStudio verbindet sich mit einem TCP-Gerät, deshalb lauscht `tcp_server` und
sendet an alle verbundenen Clients. Werte ohne verbundenen Client gehen verloren,
wie bei einem Gerät. MQTT veröffentlicht eine Nachricht pro Wert.

## Optionen

| Option | Standard | Bedeutung |
|---|---|---|
| `timestamps='us'` | ja | Mikrosekunden; Überlauf nach 71,6 Minuten, KymoStudio führt die Zeitachse weiter |
| `timestamps='ms'` | | Millisekunden; Überlauf nach 49,7 Tagen |
| `timestamps=None` | | Kein Zeitstempel; KymoStudio stempelt beim Empfang |
| `crc=True` | aus | Hängt an jeden Frame die CRC-8/ATM-Prüfsumme an |

Kanal-IDs außerhalb von 0–255 sowie NaN oder unendliche Werte lösen `ValueError` aus.
Mikrosekunden-Zeitstempel brauchen KymoStudio 2.5 oder neuer.

## Teil von Kymotrace

| Projekt | Rolle |
|---|---|
| [KymoCore](https://github.com/KymoTrace/kymocore) | Firmware-Library: Messwerte auf dem Mikrocontroller erfassen und senden |
| **[kymocore für Python](https://github.com/KymoTrace/kymocore-python)** | dieses Paket: Messwerte aus Python senden |
| [KymoProbe](https://github.com/KymoTrace/kymoprobe) | Firmware- und Hardware-Beispiele für ESP32, Arduino und STM32 |
| [KymoStudio](https://kymotrace.de/de/#download) | Desktop-App: empfangen, anzeigen, analysieren, exportieren |

## Dokumentation

- **[Protokoll](https://github.com/KymoTrace/kymocore/blob/main/PROTOCOL.md):** Byte-Layout, CRC, Beispiel-Frames (Englisch)
- **[Website](https://kymotrace.de/de/):** KymoStudio-Download, Anleitungen und Funktionen

## Lizenz

Copyright (c) 2026 Christof Seidel. kymocore für Python steht unter der
[MIT-Lizenz](https://github.com/KymoTrace/kymocore-python/blob/main/LICENSE):
frei für jede Nutzung, auch in kommerziellen Projekten, ohne eigenen Quellcode
offenlegen zu müssen.
