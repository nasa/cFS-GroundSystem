#
#  GSC-18128-1, "Core Flight Executive Version 6.7"
#
#  Copyright (c) 2006-2019 United States Government as represented by
#  the Administrator of the National Aeronautics and Space Administration.
#  All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#!/usr/bin/env python3
#

import socket
from struct import unpack
from time import sleep

import zmq
from PyQt5.QtCore import QThread, pyqtSignal

# Receive port where the CFS TO_Lab app sends the telemetry packets
udpRecvPort = 1235


#
# Receive telemetry packets, apply the appropriate header
# and publish the message with zeroMQ
#
class RoutingService(QThread):
    # Signal to update the spacecraft combo box (list) on main window GUI
    signalUpdateIpList = pyqtSignal(str, bytes)

    def __init__(self):
        super().__init__()

        # Init lists
        self.ipAddressesList = ["All"]
        self.spacecraftNames = ["All"]
        self.specialPktId = []
        self.specialPktName = []

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Init zeroMQ
        self.context = zmq.Context()
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind("ipc:///tmp/GroundSystem")

    # Run thread
    def run(self):
        # Init udp socket
        self.sock.bind(('', udpRecvPort))

        print('Attempting to wait for UDP messages')

        socketErrorCount = 0
        while socketErrorCount < 5:

            # Wait for UDP messages
            while True:
                try:
                    # Receive message
                    datagram, host = self.sock.recvfrom(
                        4096)  # buffer size is 1024 bytes

                    # Ignore datagram if it is not long enough (doesnt contain tlm header?)
                    if len(datagram) < 6:
                        continue

                    # Read host address
                    hostIpAddress = host[0]

                    #
                    # Add Host to the list if not already in list
                    #
                    if hostIpAddress not in self.ipAddressesList:
                        ## MAKE SURE THERE'S NO SPACE BETWEEN "Spacecraft"
                        ## AND THE FIRST CURLY BRACE!!!
                        hostName = f'Spacecraft{len(self.spacecraftNames)}'
                        my_hostName_as_bytes = hostName.encode()
                        print("Detected", hostName, "at", hostIpAddress)
                        self.ipAddressesList.append(hostIpAddress)
                        self.spacecraftNames.append(my_hostName_as_bytes)
                        self.signalUpdateIpList.emit(hostIpAddress,
                                                     my_hostName_as_bytes)

                    # Forward the message using zeroMQ
                    name = self.spacecraftNames[self.ipAddressesList.index(
                        hostIpAddress)]
                    self.forwardMessage(datagram, name)

                # Handle errors
                except socket.error:
                    print('Ignored socket error for attempt', socketErrorCount)
                    socketErrorCount += 1
                    sleep(1)

    # Apply header using hostname and packet id and send msg using zeroMQ
    def forwardMessage(self, datagram, hostName):
        # Forward message to channel GroundSystem.<Hostname>.<pktId>
        pktId = self.getPktId(datagram)
        my_decoded_hostName = hostName.decode()
        header = f"GroundSystem.{my_decoded_hostName}.TelemetryPackets.{pktId}"
        my_header_as_bytes = header.encode()
        self.publisher.send_multipart([my_header_as_bytes, datagram])
        # print(header)

    # Read the packet id from the telemetry packet
    @staticmethod
    def getPktId(datagram):
        # Read the telemetry header
        streamId = unpack(">H", datagram[:2])
        return hex(streamId[0])

    # Close ZMQ vars
    def stop(self):
        self.sock.close()
        self.context.destroy()
