#!/usr/bin/env python3

#
#  NASA Docket No. GSC-19,200-1, and identified as "cFS Draco"
#
#  Copyright (c) 2023 United States Government as represented by the
#  Administrator of the National Aeronautics and Space Administration.
#  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

"""Exercise telemetry forwarding and its cumulative socket-error limit."""

import socket
import unittest
from collections import deque
from contextlib import closing
from unittest.mock import Mock, call, patch

import RoutingService as routing


class ScriptedSocket:
    """End unexpected additional reads with an assertion rather than a hang."""

    def __init__(self, events):
        self.events = deque(events)
        self.bind = Mock()
        self.calls = 0

    def recvfrom(self, size):
        self.calls += 1
        if size != 4096:
            raise AssertionError("Changed telemetry buffer size")
        if not self.events:
            raise AssertionError("Receive continued past the socket-error limit")
        event = self.events.popleft()
        if isinstance(event, Exception):
            raise event
        return event


def packet(value=b"data", host="127.0.0.1"):
    return (b"\x08\x01\xc0\x00\x00\x03" + value, (host, 32100))


class TestRoutingService(unittest.TestCase):
    def setUp(self):
        socket_patch = patch.object(routing.socket, "socket")
        context_patch = patch.object(routing.zmq, "Context")
        self.addCleanup(socket_patch.stop)
        self.addCleanup(context_patch.stop)
        socket_patch.start()
        self.context = context_patch.start().return_value
        self.service = routing.RoutingService()
        self.addCleanup(self.service.stop)
        self.published = self.context.socket.return_value.send_multipart
        self.detected = []
        self.service.signal_update_ip_list.connect(
            lambda host, name: self.detected.append((host, name))
        )
        self.sleep_patch = patch.object(routing, "sleep")
        self.sleep = self.sleep_patch.start()
        self.addCleanup(self.sleep_patch.stop)

    def run_events(self, events):
        sock = ScriptedSocket(events)
        sock.close = Mock()
        self.service.sock = sock
        self.service.run()
        sock.bind.assert_called_once_with(("", routing.udp_recv_port))
        return sock

    def test_repeated_errors_exit_after_five_attempts(self):
        sock = self.run_events([OSError("unavailable") for _ in range(5)])
        self.assertEqual(sock.calls, 5)
        self.assertEqual(self.sleep.call_args_list, [call(1)] * 5)
        self.published.assert_not_called()
        self.assertEqual(self.detected, [])

    def test_packets_between_errors_keep_the_cumulative_error_limit(self):
        first = packet()
        second = packet(b"next")
        events = [OSError("one"), first, OSError("two"), second]
        events += [OSError("remaining") for _ in range(3)]
        sock = self.run_events(events)
        self.assertEqual(sock.calls, 7)
        self.assertEqual(self.sleep.call_count, 5)
        self.assertEqual(self.detected, [("127.0.0.1", b"Spacecraft1")])
        self.assertEqual(
            self.published.call_args_list,
            [
                call([b"GroundSystem.Spacecraft1.TelemetryPackets.0x801", first[0]]),
                call([b"GroundSystem.Spacecraft1.TelemetryPackets.0x801", second[0]]),
            ],
        )

    def test_short_packets_are_ignored_and_do_not_consume_error_attempts(self):
        events = [(b"", ("127.0.0.1", 1234)), (b"short", ("127.0.0.1", 1234))]
        events += [OSError("receive failed") for _ in range(5)]
        sock = self.run_events(events)
        self.assertEqual(sock.calls, 7)
        self.assertEqual(self.sleep.call_count, 5)
        self.assertEqual(self.detected, [])
        self.published.assert_not_called()

    def test_multiple_hosts_retain_their_names_and_packet_topics(self):
        events = [
            packet(host="127.0.0.1"),
            packet(host="127.0.0.2"),
            packet(host="127.0.0.1"),
        ]
        self.run_events(events + [OSError("stop") for _ in range(5)])
        self.assertEqual(
            self.detected,
            [("127.0.0.1", b"Spacecraft1"), ("127.0.0.2", b"Spacecraft2")],
        )
        self.assertEqual(
            [c.args[0][0] for c in self.published.call_args_list],
            [
                b"GroundSystem.Spacecraft1.TelemetryPackets.0x801",
                b"GroundSystem.Spacecraft2.TelemetryPackets.0x801",
                b"GroundSystem.Spacecraft1.TelemetryPackets.0x801",
            ],
        )

    def test_bind_failure_still_propagates(self):
        self.service.sock.bind.side_effect = OSError("address unavailable")
        with self.assertRaisesRegex(OSError, "address unavailable"):
            self.service.run()
        self.service.sock.recvfrom.assert_not_called()
        self.sleep.assert_not_called()

    def test_non_socket_failure_still_propagates(self):
        with self.assertRaisesRegex(ValueError, "unexpected input"):
            self.run_events([ValueError("unexpected input")])
        self.sleep.assert_not_called()

    def test_real_udp_receive_on_ephemeral_loopback_port(self):
        # Exercise real datagram receive without fixed ports or a background thread.
        with closing(socket.SocketType(socket.AF_INET, socket.SOCK_DGRAM)) as udp:
            udp.bind(("127.0.0.1", 0))
            udp.settimeout(0.01)
            with closing(
                socket.SocketType(socket.AF_INET, socket.SOCK_DGRAM)
            ) as sender:
                sender.sendto(packet()[0], udp.getsockname())
            sock = ScriptedSocket([])
            sock.close = Mock()
            sock.bind = Mock()  # the real socket is already bound above
            calls = 0

            def receive(size):
                nonlocal calls
                calls += 1
                if calls > 6:
                    raise AssertionError("Exceeded five timeouts after the packet")
                return udp.recvfrom(size)

            sock.recvfrom = receive
            self.service.sock = sock
            self.service.run()
            self.assertEqual(calls, 6)
            self.assertEqual(self.sleep.call_count, 5)
            self.published.assert_called_once_with(
                [b"GroundSystem.Spacecraft1.TelemetryPackets.0x801", packet()[0]]
            )


if __name__ == "__main__":
    unittest.main()
