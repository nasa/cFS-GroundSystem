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
# EVS Events page
#
# The EVS Event Message has the following format
#
#
# Packet Header         Start Byte
# uint16  StreamId;     0
# uint16  Sequence;     2
# uint16  Length;       4

# Start byte values after primary header depend
# on header version.
# Add 4 to ALL the values below if header version 2

# Tlm Secondary Header  Start Byte
# uint32  seconds       6
# uint16  subseconds    10

# Packet ID
# char    AppName[20]   12
# uint16  EventID;      32
# uint16  EventType;    34
# uint32  SpacecraftID; 36
# uint32  ProcessorID;  40

# Message
# char    Message[122]; 44
# uint8   Spare1;       166
# uint8   Spare2;       167

import getopt
import mmap
import sys
from pathlib import Path
from struct import unpack

import zmq
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog

from Ui_EventMessageDialog import Ui_EventMessageDialog

ROOTDIR = Path(sys.argv[0]).resolve().parent


class EventMessageTelemetry(QDialog, Ui_EventMessageDialog):
    def __init__(self, aid):
        super().__init__()
        self.setupUi(self)
        self.appId = aid

        self.eventTypes = {
            1: "DEBUG",
            2: "INFORMATION",
            3: "ERROR",
            4: "CRITICAL"
        }

        with open("/tmp/OffsetData", "r+b") as f:
            self.mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)

    def initEMTlmReceiver(self, subscr):
        self.setWindowTitle(f'{pageTitle} for: {subscr}')
        self.thread = EMTlmReceiver(subscr, self.appId)
        self.thread.emSignalTlmDatagram.connect(self.processPendingDatagrams)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    # This method processes packets. Called when the TelemetryReceiver receives a message/packet
    def processPendingDatagrams(self, datagram):
        # Packet Header
        #   uint16  StreamId;   0
        #   uint16  Sequence;   2
        #   uint16  Length;     4
        packetSeq = unpack(">H", datagram[2:4])
        seqCount = packetSeq[0] & 0x3FFF
        self.sequenceCount.setValue(seqCount)

        #
        # Get App Name, Event ID, Type and Event Text!
        #
        try:
            tlmOffset = self.mm[0]
        except ValueError:
            pass
        startByte = 12 + tlmOffset
        appName = datagram[startByte:startByte + 20].decode('utf-8', 'ignore')
        eventID = int.from_bytes(datagram[startByte + 20:startByte + 22],
                                 byteorder='little')
        eventType = int.from_bytes(datagram[startByte + 22:startByte + 24],
                                   byteorder='little')
        eventText = datagram[startByte + 32:].decode('utf-8', 'ignore')
        appName = appName.split("\0")[0]
        eventText = eventText.split("\0")[0]
        eventTypeStr = self.eventTypes.get(eventType, "INVALID EVENT TYPE")

        eventString = f"EVENT --> {appName}-{eventTypeStr} Event ID: {eventID} : {eventText}"
        self.eventOutput.appendPlainText(eventString)

    ## Reimplements closeEvent
    ## to properly quit the thread
    ## and close the window
    def closeEvent(self, event):
        self.thread.runs = False
        self.thread.wait(2000)
        super().closeEvent(event)


# Subscribes and receives zeroMQ messages
class EMTlmReceiver(QThread):
    # Setup signal to communicate with front-end GUI
    emSignalTlmDatagram = pyqtSignal(bytes)

    def __init__(self, subscr, aid):
        super().__init__()
        self.appId = aid
        self.runs = True

        # Init zeroMQ
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect("ipc:///tmp/GroundSystem")
        subscriptionString = f"{subscr}.Spacecraft1.TelemetryPackets.{appId}"
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, subscriptionString)

    def run(self):
        while self.runs:
            # Read envelope with address
            address, datagram = self.subscriber.recv_multipart()
            # Ignore if not an event message
            if self.appId in address.decode():
                self.emSignalTlmDatagram.emit(datagram)


#
# Display usage
#
def usage():
    print(("Must specify --title=\"<page name>\" --port=<udp_port> "
           "--appid=<packet_app_id(hex)> --endian=<endian(L|B) "
           "--file=<tlm_def_file>\n\nexample: --title=\"Executive Services\" "
           "--port=10800 --appid=800 --file=cfe-es-hk-table.txt --endian=L"))


if __name__ == '__main__':
    #
    # Set defaults for the arguments
    #
    pageTitle = "Event Messages"
    appId = 999
    endian = "L"
    subscription = ""

    #
    # process cmd line args
    #
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "htpafl",
            ["help", "title=", "port=", "appid=", "file=", "endian=", "sub="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        if opt in ("-p", "--port"):
            pass
        elif opt in ("-t", "--title"):
            pageTitle = arg
        elif opt in ("-f", "--file"):
            pass
        elif opt in ("-a", "--appid"):
            appId = arg
        elif opt in ("-e", "--endian"):
            endian = arg
        elif opt in ("-s", "--sub"):
            subscription = arg

    if not subscription or len(subscription.split('.')) < 3:
        subscription = "GroundSystem"

    print('Event Messages Page started. Subscribed to', subscription)

    #
    # Init the QT application and the Event Message class
    #
    app = QApplication(sys.argv)
    Telem = EventMessageTelemetry(appId)

    # Display the page
    Telem.show()
    Telem.raise_()
    Telem.initEMTlmReceiver(subscription)

    sys.exit(app.exec_())
