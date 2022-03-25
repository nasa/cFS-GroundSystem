#!/usr/bin/env python3

#
#  NASA Docket No. GSC-18,719-1, and identified as “core Flight System: Bootes”
#
#  Copyright (c) 2020 United States Government as represented by the
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

import socket
from struct import unpack
from time import sleep

import zmq
from PyQt5.QtCore import QThread, pyqtSignal

# Receive port where the CFS TO_Lab app sends the telemetry packets
udp_recv_port = 1235


#
# Receive telemetry packets, apply the appropriate header
# and publish the message with zeroMQ
#
class RoutingService(QThread):
    # Signal to update the spacecraft combo box (list) on main window GUI
    signal_update_ip_list = pyqtSignal(str, bytes)

    def __init__(self):
        super().__init__()

        # Init lists
        self.ip_addresses_list = ["All"]
        self.spacecraft_names = ["All"]
        self.special_pkt_id = []
        self.special_pkt_name = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Init zeroMQ
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind("ipc:///tmp/GroundSystem")

    # Run thread
    def run(self):
        # Init udp socket
        self.sock.bind(('', udp_recv_port))

        print('Attempting to wait for UDP messages')

        socket_error_count = 0
        while socket_error_count < 5:

            # Wait for UDP messages
            while True:
                try:
                    # Receive message
                    datagram, host = self.sock.recvfrom(
                        4096)  # buffer size is 1024 bytes

                    # Ignore datagram if it is not long enough (doesn't contain tlm header?)
                    if len(datagram) < 6:
                        continue

                    # Read host address
                    host_ip_address = host[0]

                    #
                    # Add Host to the list if not already in list
                    #
                    if host_ip_address not in self.ip_addresses_list:
                        ## MAKE SURE THERE'S NO SPACE BETWEEN "Spacecraft"
                        ## AND THE FIRST CURLY BRACE!!!
                        hostname = f'Spacecraft{len(self.spacecraft_names)}'
                        my_hostname_as_bytes = hostname.encode()
                        print("Detected", hostname, "at", host_ip_address)
                        self.ip_addresses_list.append(host_ip_address)
                        self.spacecraft_names.append(my_hostname_as_bytes)
                        self.signal_update_ip_list.emit(host_ip_address,
                                                        my_hostname_as_bytes)

                    # Forward the message using zeroMQ
                    name = self.spacecraft_names[self.ip_addresses_list.index(
                        host_ip_address)]
                    self.forwardMessage(datagram, name)

                # Handle errors
                except socket.error:
                    print('Ignored socket error for attempt', socket_error_count)
                    socket_error_count += 1
                    sleep(1)

    # Apply header using hostname and packet id and send msg using zeroMQ
    def forwardMessage(self, datagram, hostName):
        # Forward message to channel GroundSystem.<hostname>.<pkt_id>
        pkt_id = self.get_pkt_id(datagram)
        my_decoded_hostname = hostName.decode()
        header = f"GroundSystem.{my_decoded_hostname}.TelemetryPackets.{pkt_id}"
        my_header_as_bytes = header.encode()
        self.publisher.send_multipart([my_header_as_bytes, datagram])
        # print(header)

    # Read the packet id from the telemetry packet
    @staticmethod
    def get_pkt_id(datagram):
        # Read the telemetry header
        stream_id = unpack(">H", datagram[:2])
        return hex(stream_id[0])

    # Close ZMQ vars
    def stop(self):
        self.sock.close()
        self.context.destroy()
