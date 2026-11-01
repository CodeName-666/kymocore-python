import os
import socket
import time
from pathlib import Path

import pytest

from kymocore import Sender, frame, transport

# PROTOCOL.md "Golden vectors"
GOLDEN = [
    (dict(id=7, y=1.0), 'a5 5a 41 07 00 00 80 3f 00'),
    (dict(id=3, x=1.25, y=-2.5, z=9.0, t=1234), 'a5 5a 4f 03 00 00 a0 3f 00 00 20 c0 00 00 10 41 d2 04 00 00 00'),
    (dict(id=3, y=-2.5, t=1234567, us=True), 'a5 5a 53 03 00 00 20 c0 87 d6 12 00 00'),
    (dict(id=7, y=1.0, crc=True), 'a5 5a 40 07 00 00 80 3f 54'),
    (dict(id=3, x=1.25, y=-2.5, z=9.0, t=1234, crc=True), 'a5 5a 4e 03 00 00 a0 3f 00 00 20 c0 00 00 10 41 d2 04 00 00 89'),
    (dict(id=3, y=-2.5, t=1234567, us=True, crc=True), 'a5 5a 52 03 00 00 20 c0 87 d6 12 00 97'),
]


@pytest.mark.parametrize('point, expected', GOLDEN)
def test_frames_match_the_golden_vectors(point, expected):
    assert frame(**point).hex(' ') == expected


@pytest.mark.parametrize('point', [dict(id=256, y=1.), dict(id=-1, y=1.), dict(id=0, y=float('nan')),
                                   dict(id=0, y=1., x=float('inf')), dict(id=0, y=1., us=True)])
def test_invalid_points_are_refused(point):
    with pytest.raises(ValueError):
        frame(**point)


class Sink:
    def __init__(self):
        self.data = []

    def write(self, data):
        self.data.append(data)

    def close(self):
        pass


def test_sender_stamps_monotonic_microseconds_and_milliseconds():
    sink = Sink()
    Sender(sink).send(1, 2.)
    assert sink.data[0][2] == 0x53
    Sender(sink, timestamps='ms', crc=True).send(1, 2.)
    assert sink.data[1][2] == 0x42
    Sender(sink, timestamps=None).send(1, 2., x=3.)
    assert sink.data[2][2] == 0x49 and len(sink.data[2]) == 13
    with pytest.raises(ValueError):
        Sender(sink, timestamps='s')


def test_udp_reaches_a_listening_socket():
    rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rx.bind(('127.0.0.1', 0))
    rx.settimeout(2)
    with Sender.udp('127.0.0.1', rx.getsockname()[1], timestamps=None) as s:
        s.send(7, 1.)
    assert rx.recv(64) == frame(7, 1.)
    rx.close()


def test_tcp_server_feeds_a_connecting_client_and_survives_its_disconnect():
    sink = transport.TcpServer(0, '127.0.0.1')
    port = sink._server.getsockname()[1]
    sink.write(b'dropped')
    client = socket.create_connection(('127.0.0.1', port), timeout=2)
    time.sleep(.05)
    sink.write(frame(7, 1.))
    assert client.recv(64) == frame(7, 1.)
    client.close()
    for _ in range(3):  # the second write after a close fails and drops the client
        sink.write(frame(7, 1.))
        time.sleep(.05)
    assert sink._clients == []
    sink.close()


def test_mqtt_publishes_each_frame_to_the_topic(monkeypatch):
    import paho.mqtt.client as mqtt
    calls = []

    class Client:
        def __init__(self, api, client_id):
            calls.append(('init', client_id))

        def username_pw_set(self, user, password):
            calls.append(('auth', user, password))

        def connect(self, host, port):
            calls.append(('connect', host, port))

        def loop_start(self):
            calls.append(('loop',))

        def publish(self, topic, data, qos):
            calls.append(('publish', topic, data, qos))

        def loop_stop(self):
            calls.append(('stop',))

        def disconnect(self):
            calls.append(('disconnect',))

    monkeypatch.setattr(mqtt, 'Client', Client)
    with Sender.mqtt('broker', 'lab/kymo', qos=1, username='u', password='p', timestamps=None) as s:
        s.send(7, 1.)
    assert calls == [('init', ''), ('auth', 'u', 'p'), ('connect', 'broker', 1883), ('loop',),
                     ('publish', 'lab/kymo', frame(7, 1.), 1), ('stop',), ('disconnect',)]


STUDIO = Path(os.environ.get('KYMOSTUDIO', Path(__file__).parents[2] / 'KymoStudio')) / 'python'


@pytest.mark.skipif(not (STUDIO / 'Receiver' / 'binary_protocol.py').exists(), reason='KymoStudio checkout not found')
def test_kymostudio_decoder_reads_the_stream(monkeypatch):
    monkeypatch.syspath_prepend(str(STUDIO))
    from Receiver.binary_protocol import ProtocolStreamDecoder, decode_data_frame
    sink = Sink()
    s = Sender(sink)
    for i in range(5):
        s.send(i, i / 2, x=-i, z=i * 3.)
    frames = ProtocolStreamDecoder().feed(b''.join(sink.data))
    points = [decode_data_frame(f) for f in frames]
    assert [(p.id, p.value, p.x, p.z_value) for p in points] == [(i, i / 2, -i, i * 3.) for i in range(5)]
    assert all(b.timestamp >= a.timestamp for a, b in zip(points, points[1:]))
