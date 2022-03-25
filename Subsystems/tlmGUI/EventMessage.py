# !/usr/bin/env python3

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

from UiEventmessagedialog import UiEventmessagedialog

ROOTDIR = Path(sys.argv[0]).resolve().parent


class EventMessageTelemetry(QDialog, UiEventmessagedialog):
    def __init__(self, aid):
        super().__init__()
        self.setup_ui(self)
        self.appId = aid

        self.eventTypes = {
            1: "DEBUG",
            2: "INFORMATION",
            3: "ERROR",
            4: "CRITICAL"
        }

        with open("/tmp/OffsetData", "r+b") as f:
            self.mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)

    def init_em_tlm_receiver(self, subscr):
        self.setWindowTitle(f'{page_title} for: {subscr}')
        self.thread = EMTlmReceiver(subscr, self.appId)
        self.thread.em_signal_tlm_datagram.connect(self.process_pending_datagrams)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    # This method processes packets. Called when the TelemetryReceiver receives a message/packet
    def process_pending_datagrams(self, datagram):
        # Packet Header
        #   uint16  StreamId;   0
        #   uint16  Sequence;   2
        #   uint16  Length;     4
        packet_seq = unpack(">H", datagram[2:4])
        seq_count = packet_seq[0] & 0x3FFF
        self.sequence_count.setValue(seq_count)

        tlm_offset = 0
        #
        # Get App Name, Event ID, Type and Event Text!
        #
        try:
            tlm_offset = self.mm[0]
        except ValueError:
            pass
        start_byte = 12 + tlm_offset
        app_name = datagram[start_byte:start_byte + 20].decode('utf-8', 'ignore')
        event_id = int.from_bytes(datagram[start_byte + 20:start_byte + 22],
                                  byteorder='little')
        event_type = int.from_bytes(datagram[start_byte + 22:start_byte + 24],
                                    byteorder='little')
        event_text = datagram[start_byte + 32:].decode('utf-8', 'ignore')
        app_name = app_name.split("\0")[0]
        event_text = event_text.split("\0")[0]
        event_type_str = self.eventTypes.get(event_type, "INVALID EVENT TYPE")

        event_string = f"EVENT --> {app_name}-{event_type_str} Event ID: {event_id} : {event_text}"
        self.event_output.appendPlainText(event_string)

    # Reimplements closeEvent
    # to properly quit the thread
    # and close the window
    def closeEvent(self, event):
        self.thread.runs = False
        self.thread.wait(2000)
        super().closeEvent(event)


# Subscribes and receives zeroMQ messages
class EMTlmReceiver(QThread):
    # Setup signal to communicate with front-end GUI
    em_signal_tlm_datagram = pyqtSignal(bytes)

    def __init__(self, subscr, aid):
        super().__init__()
        self.app_id = aid
        self.runs = True

        # Init zeroMQ
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect("ipc:///tmp/GroundSystem")
        subscription_string = f"{subscr}.Spacecraft1.TelemetryPackets.{app_id}"
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, subscription_string)

    def run(self):
        while self.runs:
            # Read envelope with address
            address, datagram = self.subscriber.recv_multipart()
            # Ignore if not an event message
            if self.app_id in address.decode():
                self.em_signal_tlm_datagram.emit(datagram)


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
    page_title = "Event Messages"
    app_id = 999
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
            page_title = arg
        elif opt in ("-f", "--file"):
            pass
        elif opt in ("-a", "--appid"):
            app_id = arg
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
    telem = EventMessageTelemetry(app_id)

    # Display the page
    telem.show()
    telem.raise_()
    telem.init_em_tlm_receiver(subscription)

    sys.exit(app.exec_())
