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
import mmap
import sys
from pathlib import Path
from struct import unpack

import zmq
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QDialog, QHeaderView,
                             QTableWidgetItem)

from Ui_GenericTelemetryDialog import Ui_GenericTelemetryDialog

## ../cFS/tools/cFS-GroundSystem/Subsystems/tlmGUI
ROOTDIR = Path(sys.argv[0]).resolve().parent


class SubsystemTelemetry(QDialog, Ui_GenericTelemetryDialog):
    #
    # Init the class
    #
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        with open("/tmp/OffsetData", "r+b") as f:
            self.mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)

    #
    # This method decodes a telemetry item from the packet and displays it
    #
    def displayTelemetryItem(self, datagram, tlmIndex, labelField, valueField):
        if tlmItemIsValid[tlmIndex]:
            try:
                tlmOffset = self.mm[0]
            except ValueError:
                pass
            TlmField1 = tlmItemFormat[tlmIndex]
            if TlmField1[0] == "<":
                TlmField1 = TlmField1[1:]
            try:
                itemStart = int(tlmItemStart[tlmIndex]) + tlmOffset
            except UnboundLocalError:
                pass
            TlmField2 = datagram[itemStart:itemStart +
                                 int(tlmItemSize[tlmIndex])]
            if TlmField2:
                TlmField = unpack(TlmField1, TlmField2)
                if tlmItemDisplayType[tlmIndex] == 'Dec':
                    valueField.setText(str(TlmField[0]))
                elif tlmItemDisplayType[tlmIndex] == 'Hex':
                    valueField.setText(hex(TlmField[0]))
                elif tlmItemDisplayType[tlmIndex] == 'Enm':
                    valueField.setText(tlmItemEnum[tlmIndex][int(TlmField[0])])
                elif tlmItemDisplayType[tlmIndex] == 'Str':
                    valueField.setText(TlmField[0].decode('utf-8', 'ignore'))
                labelField.setText(tlmItemDesc[tlmIndex])
            else:
                print("ERROR: Can't unpack buffer of length", len(TlmField2))

    # Start the telemetry receiver (see GTTlmReceiver class)
    def initGTTlmReceiver(self, subscr):
        self.setWindowTitle(f"{pageTitle} for: {subscr}")
        self.thread = GTTlmReceiver(subscr)
        self.thread.gtSignalTlmDatagram.connect(self.processPendingDatagrams)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    #
    # This method processes packets.
    # Called when the TelemetryReceiver receives a message/packet
    #
    def processPendingDatagrams(self, datagram):
        #
        # Show sequence number
        #
        packetSeq = unpack(">H", datagram[2:4])
        seqCount = packetSeq[0] & 0x3FFF  ## sequence count mask
        self.sequenceCount.setValue(seqCount)

        #
        # Decode and display all packet elements
        #
        for k in range(self.tblTelemetry.rowCount()):
            itemLabel = self.tblTelemetry.item(k, 0)
            itemValue = self.tblTelemetry.item(k, 1)
            self.displayTelemetryItem(datagram, k, itemLabel, itemValue)

    ## Reimplements closeEvent
    ## to properly quit the thread
    ## and close the window
    def closeEvent(self, event):
        self.thread.runs = False
        self.thread.wait(2000)
        self.mm.close()
        super().closeEvent(event)


# Subscribes and receives zeroMQ messages
class GTTlmReceiver(QThread):
    # Setup signal to communicate with front-end GUI
    gtSignalTlmDatagram = pyqtSignal(bytes)

    def __init__(self, subscr):
        super().__init__()
        self.runs = True

        # Init zeroMQ
        context = zmq.Context()
        self.subscriber = context.socket(zmq.SUB)
        self.subscriber.connect("ipc:///tmp/GroundSystem")
        myTlmPgAPID = subscr.split(".", 1)
        mySubscription = f"GroundSystem.Spacecraft1.TelemetryPackets.{myTlmPgAPID[1]}"
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, mySubscription)

    def run(self):
        while self.runs:
            # Read envelope with address
            _, datagram = self.subscriber.recv_multipart()
            # Send signal with received packet to front-end/GUI
            self.gtSignalTlmDatagram.emit(datagram)


#
# Display usage
#
def usage():
    print(("Must specify --title=\"<page name>\" --port=<udp_port> "
           "--appid=<packet_app_id(hex)> --endian=<endian(L|B) "
           "--file=<tlm_def_file>\n\nexample: --title=\"Executive Services\" "
           "--port=10800 --appid=800 --file=cfe-es-hk-table.txt --endian=L"))


#
# Main
#
if __name__ == '__main__':
    #
    # Set defaults for the arguments
    #
    pageTitle = "Telemetry Page"
    # udpPort = 10000
    appId = 999
    tlmDefFile = f"{ROOTDIR}/telemetry_def.txt"
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
        elif opt in ("-p", "--port"):
            pass
        elif opt in ("-t", "--title"):
            pageTitle = arg
        elif opt in ("-f", "--file"):
            tlmDefFile = arg
        elif opt in ("-t", "--appid"):
            appId = arg
        elif opt in ("-e", "--endian"):
            endian = arg
        elif opt in ("-s", "--sub"):
            subscription = arg

    if not subscription:
        subscription = "GroundSystem"

    print('Generic Telemetry Page started. Subscribed to', subscription)

    py_endian = '<' if endian.upper() == 'L' else '>'

    #
    # Init the QT application and the telemetry class
    #
    app = QApplication(sys.argv)
    Telem = SubsystemTelemetry()
    tbl = Telem.tblTelemetry
    Telem.subSystemLineEdit.setText(pageTitle)
    Telem.packetId.display(appId)

    #
    # Read in the contents of the telemetry packet definition
    #
    tlmItemIsValid, tlmItemDesc, \
    tlmItemStart, tlmItemSize, \
    tlmItemDisplayType, tlmItemFormat = ([] for _ in range(6))

    tlmItemEnum = [None] * 40

    i = 0
    with open(f"{ROOTDIR}/{tlmDefFile}") as tlmfile:
        reader = csv.reader(tlmfile, skipinitialspace=True)
        for row in reader:
            if not row[0].startswith("#"):
                tlmItemIsValid.append(True)
                tlmItemDesc.append(row[0])
                tlmItemStart.append(row[1])
                tlmItemSize.append(row[2])
                if row[3].lower() == 's':
                    tlmItemFormat.append(f'{row[2]}{row[3]}')
                else:
                    tlmItemFormat.append(f'{py_endian}{row[3]}')
                tlmItemDisplayType.append(row[4])
                if row[4] == 'Enm':
                    tlmItemEnum[i] = row[5:9]
                Telem.tblTelemetry.insertRow(i)
                lblItem, valItem = QTableWidgetItem(), QTableWidgetItem()
                Telem.tblTelemetry.setItem(i, 0, lblItem)
                Telem.tblTelemetry.setItem(i, 1, valItem)
                i += 1
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    tbl.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

    #
    # Display the page
    #
    Telem.show()
    Telem.raise_()
    Telem.initGTTlmReceiver(subscription)

    sys.exit(app.exec_())
