"""Byte sinks for KymoStudio's sources. Each has write(data) and close()."""
import socket


class Udp:
    """KymoStudio's UDP source listens; datagrams go to its address."""

    def __init__(self, host: str, port: int):
        self._address = (host, port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def write(self, data: bytes):
        self._sock.sendto(data, self._address)

    def close(self):
        self._sock.close()


class TcpServer:
    """KymoStudio's Telnet/TCP source connects like to a device, so this side listens.

    Frames go to every connected client; without one they are dropped, as on a device.
    """

    def __init__(self, port: int, host: str = '0.0.0.0'):
        self._server = socket.create_server((host, port))
        self._server.setblocking(False)
        self._clients = []

    def write(self, data: bytes):
        try:
            while True:
                client, _ = self._server.accept()
                client.setblocking(True)
                self._clients.append(client)
        except BlockingIOError:
            pass
        for client in self._clients[:]:
            try:
                client.sendall(data)
            except OSError:
                client.close()
                self._clients.remove(client)

    def close(self):
        for client in self._clients:
            client.close()
        self._server.close()


class Serial:
    """Serial port or USB CDC; needs ``pip install kymocore[serial]``."""

    def __init__(self, port: str, baudrate: int = 115200):
        import serial
        self._port = serial.Serial(port, baudrate)

    def write(self, data: bytes):
        self._port.write(data)

    def close(self):
        self._port.close()


class Mqtt:
    """Publishes frames to a topic of KymoStudio's MQTT source (its receive topics).

    Needs ``pip install kymocore[mqtt]``. One message per frame; KymoStudio also
    accepts several concatenated frames in one payload.
    """

    def __init__(self, host: str, topic: str, port: int = 1883, *, qos: int = 0,
                 username: str = None, password: str = None, client_id: str = ''):
        import paho.mqtt.client as mqtt
        self._topic, self._qos = topic, qos
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        if username:
            self._client.username_pw_set(username, password)
        self._client.connect(host, port)
        self._client.loop_start()  # paho reconnects by itself while the loop runs

    def write(self, data: bytes):
        self._client.publish(self._topic, data, qos=self._qos)

    def close(self):
        self._client.loop_stop()
        self._client.disconnect()
