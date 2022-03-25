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

import csv
import getopt
import shlex
import subprocess
import sys
from pathlib import Path
from struct import unpack

import zmq
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QDialog, QHeaderView, QPushButton,
                             QTableWidgetItem)

from UiTelemetrysystemdialog import UiTelemetrysystemdialog

ROOTDIR = Path(sys.argv[0]).resolve().parent


class TelemetrySystem(QDialog, UiTelemetrysystemdialog):
    #
    # Init the class
    #
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Telemetry System Main Page')
        self.move(0, 100)

        self.pkt_count = 0
        self.subscription = None

    #
    # convert a string of binary bytes to ascii hex
    #
    @staticmethod
    def str_to_hex(a_string):
        hex_str = ""
        for x in a_string:
            hex_str += f'{ord(x):02X} '
        return hex_str.strip()

    #
    # Dump the telemetry packet
    #
    def dump_packet(self, packet_data):
        app_id = (ord(packet_data[0]) << 8) + (ord(packet_data[1]))
        print("\n-----------------------------------------------")
        print("\nPacket: App ID =", hex(app_id))
        print("\nPacket Data:", self.str_to_hex(packet_data))

    def process_button_generic(self, idx):
        temp_sub = f"{self.subscription}.{hex(tlm_page_appid[idx])}"
        if tlm_page_is_valid[idx]:
            # need to extract data from fields, then start page with right params
            launch_string = (f'python3 {ROOTDIR}/{tlm_class[idx]} '
                             f'--title=\"{tlm_page_desc[idx]}\" '
                             f'--appid={hex(tlm_page_appid[idx])} '
                             f'--port={tlm_page_port[idx]} '
                             f'--file={tlm_page_def_file[idx]} '
                             f'--endian={endian} --sub={temp_sub}')
            # print(launch_string)
            cmd_args = shlex.split(launch_string)
            subprocess.Popen(cmd_args)

    # Start the telemetry receiver (see TSTlmReceiver class)
    def init_ts_tlm_receiver(self, subscr):
        self.setWindowTitle(f'Telemetry System page for: {subscr}')
        self.subscription = subscr
        self.thread = TSTlmReceiver(subscr)
        self.thread.ts_signal_tlm_datagram.connect(self.process_pending_datagrams)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    #
    # This method processes packets.
    # Called when the TelemetryReceiver receives a message/packet
    #
    def process_pending_datagrams(self, datagram):
        #
        # Show number of packets received
        #
        self.pkt_count += 1
        self.packet_count.setValue(self.pkt_count)
        # sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #
        # Decode the packet and forward it to the
        # correct port (if there is one)
        #
        stream_id = unpack(">H", datagram[:2])

        # Uncomment the next two lines to debug
        # print("Packet ID =", hex(stream_id[0]))
        # self.dumpPacket(datagram)
        for l in range(self.tbl_tlm_sys.rowCount()):
            if stream_id[0] == tlm_page_appid[l]:
                # send_host = "127.0.0.1"
                # send_port = tlmPagePort[l]
                # sendSocket.sendto(datagram, (send_host, send_port))

                tlm_page_count[l] += 1
                # I wish I knew a better way to update the count field
                # in the GUI. Maybe store a pointer to the field in the gui
                self.tbl_tlm_sys.item(l, 2).setText(str(tlm_page_count[l]))

                # Unclear why line 15 is skipped. Removing for now, need
                # to evaluate long term (lbleier 06/01/2020)
                # if l < 15:
                #     self.tblTlmSys.item(l, 2).setText(str(tlmPageCount[l]))
                # else:
                #     self.tblTlmSys.item(l + 1, 2).setText(str(tlmPageCount[l]))

    # Reimplements closeEvent
    # to properly quit the thread
    # and close the window
    def closeEvent(self, event):
        self.thread.runs = False
        self.thread.wait(2000)
        super().closeEvent(event)


# Subscribes and receives zeroMQ messages
class TSTlmReceiver(QThread):
    # Setup signal to communicate with front-end GUI
    ts_signal_tlm_datagram = pyqtSignal(bytes)

    def __init__(self, subscr):
        super().__init__()
        self.runs = True

        # Init zeroMQ
        context = zmq.Context()
        self.subscriber = context.socket(zmq.SUB)
        self.subscriber.connect("ipc:///tmp/GroundSystem")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, subscr)

    def run(self):
        while self.runs:
            # Receive and read envelope with address
            _, datagram = self.subscriber.recv_multipart()
            # Send signal with received packet to front-end/GUI
            self.ts_signal_tlm_datagram.emit(datagram)


#
# Main
#
if __name__ == '__main__':
    #
    # Init the QT application and the telemetry dialog class
    #
    app = QApplication(sys.argv)
    telem = TelemetrySystem()
    tbl = telem.tbl_tlm_sys

    #
    # Set defaults for the arguments
    #
    tlm_def_file = f"{ROOTDIR}/telemetry-pages.txt"
    endian = "L"
    subscription = ""

    #
    # process cmd line args
    #
    try:
        opts, args = getopt.getopt(sys.argv[1:], "htpafl", ["sub="])
    except getopt.GetoptError:
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-s", "--sub"):
            subscription = arg

    if not subscription:
        subscription = "GroundSystem"

    print('Telemetry System started. Subscribed to', subscription)
    #
    # Read in the contents of the telemetry packet definition
    #
    tlm_page_is_valid, tlm_page_desc, tlm_class, tlm_page_port, \
    tlm_page_appid, tlm_page_count, tlm_page_def_file = ([] for _ in range(7))
    i = 0

    with open(tlm_def_file) as tlmfile:
        reader = csv.reader(tlmfile, skipinitialspace=True)
        for row in reader:
            if not row[0].startswith('#'):
                tlm_page_is_valid.append(True)
                tlm_page_desc.append(row[0])
                tlm_class.append(row[1])
                tlm_page_port.append(int(row[2], 16) + 10000)
                tlm_page_appid.append(int(row[2], 16))
                tlm_page_def_file.append(row[3])
                tlm_page_count.append(0)
                i += 1
    #
    # Mark the remaining values as invalid
    #
    # for _ in range(i, 21):
    #     tlmPageAppid.append(0)
    #     tlmPageIsValid.append(False)

    #
    # fill the data fields on the page
    #
    for i, desc in enumerate(tlm_page_desc):
        if tlm_page_is_valid[i]:
            tbl.insertRow(i)
            for col, text in enumerate(
                (desc, hex(tlm_page_appid[i]), tlm_page_count[0])):
                tblItem = QTableWidgetItem(str(text))
                tbl.setItem(i, col, tblItem)
            btn = QPushButton("Display Page")
            btn.clicked.connect(lambda _, x=i: telem.process_button_generic(x))
            tbl.setCellWidget(i, tbl.columnCount() - 1, btn)
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    tbl.horizontalHeader().setStretchLastSection(True)

    #
    # Display the page
    #
    telem.show()
    telem.raise_()
    telem.init_ts_tlm_receiver(subscription)
    sys.exit(app.exec_())
