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

from Ui_TelemetrySystemDialog import Ui_TelemetrySystemDialog

ROOTDIR = Path(sys.argv[0]).resolve().parent


class TelemetrySystem(QDialog, Ui_TelemetrySystemDialog):
    #
    # Init the class
    #
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Telemetry System Main Page')
        self.move(0, 100)

        self.pktCount = 0
        self.subscription = None

    #
    # convert a string of binary bytes to ascii hex
    #
    @staticmethod
    def strToHex(aString):
        hexStr = ""
        for x in aString:
            hexStr += f'{ord(x):02X} '
        return hexStr.strip()

    #
    # Dump the telemetry packet
    #
    def dumpPacket(self, packetData):
        appId = (ord(packetData[0]) << 8) + (ord(packetData[1]))
        print("\n-----------------------------------------------")
        print("\nPacket: App ID =", hex(appId))
        print("\nPacket Data:", self.strToHex(packetData))

    def ProcessButtonGeneric(self, idx):
        tempSub = f"{self.subscription}.{hex(tlmPageAppid[idx])}"
        if tlmPageIsValid[idx]:
            # need to extract data from fields, then start page with right params
            launch_string = (f'python3 {ROOTDIR}/{tlmClass[idx]} '
                             f'--title=\"{tlmPageDesc[idx]}\" '
                             f'--appid={hex(tlmPageAppid[idx])} '
                             f'--port={tlmPagePort[idx]} '
                             f'--file={tlmPageDefFile[idx]} '
                             f'--endian={endian} --sub={tempSub}')
            # print(launch_string)
            cmd_args = shlex.split(launch_string)
            subprocess.Popen(cmd_args)

    # Start the telemetry receiver (see TSTlmReceiver class)
    def initTSTlmReceiver(self, subscr):
        self.setWindowTitle(f'Telemetry System page for: {subscr}')
        self.subscription = subscr
        self.thread = TSTlmReceiver(subscr)
        self.thread.tsSignalTlmDatagram.connect(self.processPendingDatagrams)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    #
    # This method processes packets.
    # Called when the TelemetryReceiver receives a message/packet
    #
    def processPendingDatagrams(self, datagram):
        #
        # Show number of packets received
        #
        self.pktCount += 1
        self.packetCount.setValue(self.pktCount)
        # sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #
        # Decode the packet and forward it to the
        # correct port (if there is one)
        #
        streamId = unpack(">H", datagram[:2])

        ## Uncomment the next two lines to debug
        # print("Packet ID =", hex(streamId[0]))
        # self.dumpPacket(datagram)
        for l in range(self.tblTlmSys.rowCount()):
            if streamId[0] == tlmPageAppid[l]:
                # send_host = "127.0.0.1"
                # send_port = tlmPagePort[l]
                # sendSocket.sendto(datagram, (send_host, send_port))

                tlmPageCount[l] += 1
                ## I wish I knew a better way to update the count field
                ## in the GUI. Maybe store a pointer to the field in the gui
                self.tblTlmSys.item(l, 2).setText(str(tlmPageCount[l]))

                ## Unclear why line 15 is skipped. Removing for now, need
                ## to evaluate long term (lbleier 06/01/2020)
                # if l < 15:
                #     self.tblTlmSys.item(l, 2).setText(str(tlmPageCount[l]))
                # else:
                #     self.tblTlmSys.item(l + 1, 2).setText(str(tlmPageCount[l]))

    ## Reimplements closeEvent
    ## to properly quit the thread
    ## and close the window
    def closeEvent(self, event):
        self.thread.runs = False
        self.thread.wait(2000)
        super().closeEvent(event)


# Subscribes and receives zeroMQ messages
class TSTlmReceiver(QThread):
    # Setup signal to communicate with front-end GUI
    tsSignalTlmDatagram = pyqtSignal(bytes)

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
            self.tsSignalTlmDatagram.emit(datagram)


#
# Main
#
if __name__ == '__main__':
    #
    # Init the QT application and the telemetry dialog class
    #
    app = QApplication(sys.argv)
    Telem = TelemetrySystem()
    tbl = Telem.tblTlmSys

    #
    # Set defaults for the arguments
    #
    tlmDefFile = f"{ROOTDIR}/telemetry-pages.txt"
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
    tlmPageIsValid, tlmPageDesc, tlmClass, tlmPagePort,\
        tlmPageAppid, tlmPageCount, tlmPageDefFile = ([] for _ in range(7))
    i = 0

    with open(tlmDefFile) as tlmfile:
        reader = csv.reader(tlmfile, skipinitialspace=True)
        for row in reader:
            if not row[0].startswith('#'):
                tlmPageIsValid.append(True)
                tlmPageDesc.append(row[0])
                tlmClass.append(row[1])
                tlmPagePort.append(int(row[2], 16) + 10000)
                tlmPageAppid.append(int(row[2], 16))
                tlmPageDefFile.append(row[3])
                tlmPageCount.append(0)
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
    for i, desc in enumerate(tlmPageDesc):
        if tlmPageIsValid[i]:
            tbl.insertRow(i)
            for col, text in enumerate(
                (desc, hex(tlmPageAppid[i]), tlmPageCount[0])):
                tblItem = QTableWidgetItem(str(text))
                tbl.setItem(i, col, tblItem)
            btn = QPushButton("Display Page")
            btn.clicked.connect(lambda _, x=i: Telem.ProcessButtonGeneric(x))
            tbl.setCellWidget(i, tbl.columnCount() - 1, btn)
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    tbl.horizontalHeader().setStretchLastSection(True)

    #
    # Display the page
    #
    Telem.show()
    Telem.raise_()
    Telem.initTSTlmReceiver(subscription)
    sys.exit(app.exec_())
