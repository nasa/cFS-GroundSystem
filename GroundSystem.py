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
# cFS Ground System Version 2.0.0
#
#!/usr/bin/env python3
#
import shlex
import subprocess
import sys
import os
import signal
import pathlib

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from RoutingService import RoutingService
from Ui_MainWindow import Ui_MainWindow

from _version import __version__ as _version
from _version import _version_string

__version__ = _version

#ROOTDIR = Path(sys.argv[0]).resolve().parent
ROOTDIR = pathlib.Path(__file__).parent.absolute()


#
# CFS Ground System: Setup and manage the main window
#
class GroundSystem(QMainWindow, Ui_MainWindow):
    TLM_HDR_V1_OFFSET = 4
    TLM_HDR_V2_OFFSET = 4
    CMD_HDR_PRI_V1_OFFSET = 0
    CMD_HDR_SEC_V1_OFFSET = 0
    CMD_HDR_PRI_V2_OFFSET = 4
    CMD_HDR_SEC_V2_OFFSET = 4

    #
    # Init the class
    #
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.RoutingService = None
        self.alert = QMessageBox()

        # set initial defaults
        self.sbTlmOffset.setValue(self.TLM_HDR_V1_OFFSET)
        self.sbCmdOffsetPri.setValue(self.CMD_HDR_PRI_V1_OFFSET)
        self.sbCmdOffsetSec.setValue(self.CMD_HDR_SEC_V1_OFFSET)

        self.pushButtonStartTlm.clicked.connect(self.startTlmSystem)
        self.pushButtonStartCmd.clicked.connect(self.startCmdSystem)
        self.cbTlmHeaderVer.currentIndexChanged.connect(self.setTlmOffset)
        self.cbCmdHeaderVer.currentIndexChanged.connect(self.setCmdOffsets)

        for sb in (self.sbTlmOffset, self.sbCmdOffsetPri, self.sbCmdOffsetSec):
            sb.valueChanged.connect(self.saveOffsets)
        # Init lists
        self.ipAddressesList = ['All']
        self.spacecraftNames = ['All']

    def closeEvent(self, evnt):
        if self.RoutingService:
            self.RoutingService.stop()
            print("Stopped routing service")
        os.kill(0, signal.SIGKILL)
        super().closeEvent(evnt)

    # Read the selected spacecraft from combo box on GUI
    def getSelectedSpacecraftAddress(self):
        return self.comboBoxIpAddresses.currentText().strip()

    # Returns the name of the selected spacecraft
    def getSelectedSpacecraftName(self):
        return self.spacecraftNames[self.ipAddressesList.index(
            self.getSelectedSpacecraftAddress())].strip()

    #
    # Display popup with error
    #
    def DisplayErrorMessage(self, message):
        print(message)
        self.alert.setText(message)
        self.alert.setIcon(QMessageBox.Warning)
        self.alert.exec_()

    # Start the telemetry system for the selected spacecraft
    def startTlmSystem(self):
        # Setup the subscription (to let the telemetry
        # system know the messages it will be receiving)
        subscription = '--sub=GroundSystem'
        selectedSpacecraft = self.getSelectedSpacecraftName()
        if selectedSpacecraft != 'All':
            subscription += f'.{selectedSpacecraft}.TelemetryPackets'

        # Open Telemetry System
        system_call = f'python3 {ROOTDIR}/Subsystems/tlmGUI/TelemetrySystem.py {subscription}'
        args = shlex.split(system_call)
        subprocess.Popen(args)

    # Start command system
    @staticmethod
    def startCmdSystem():
        subprocess.Popen(
            ['python3', f'{ROOTDIR}/Subsystems/cmdGui/CommandSystem.py'])

    # Start FDL-FUL gui system
    def startFDLSystem(self):
        selectedSpacecraft = self.getSelectedSpacecraftName()
        if selectedSpacecraft == 'All':
            self.DisplayErrorMessage(
                'Cannot open FDL manager.\nNo spacecraft selected.')
        else:
            subscription = f'--sub=GroundSystem.{selectedSpacecraft}'
            subprocess.Popen([
                'python3', f'{ROOTDIR}/Subsystems/fdlGui/FdlSystem.py',
                subscription
            ])

    def setTlmOffset(self):
        selectedVer = self.cbTlmHeaderVer.currentText().strip()
        if selectedVer == "Custom":
            self.sbTlmOffset.setEnabled(True)
        else:
            self.sbTlmOffset.setEnabled(False)
            if selectedVer == "1":
                self.sbTlmOffset.setValue(self.TLM_HDR_V1_OFFSET)
            elif selectedVer == "2":
                self.sbTlmOffset.setValue(self.TLM_HDR_V2_OFFSET)

    def setCmdOffsets(self):
        selectedVer = self.cbCmdHeaderVer.currentText().strip()
        if selectedVer == "Custom":
            self.sbCmdOffsetPri.setEnabled(True)
            self.sbCmdOffsetSec.setEnabled(True)
        else:
            self.sbCmdOffsetPri.setEnabled(False)
            self.sbCmdOffsetSec.setEnabled(False)
            if selectedVer == "1":
                self.sbCmdOffsetPri.setValue(self.CMD_HDR_PRI_V1_OFFSET)
                self.sbCmdOffsetSec.setValue(self.CMD_HDR_SEC_V1_OFFSET)
            elif selectedVer == "2":
                self.sbCmdOffsetPri.setValue(self.CMD_HDR_PRI_V2_OFFSET)
                self.sbCmdOffsetSec.setValue(self.CMD_HDR_SEC_V2_OFFSET)

    def saveOffsets(self):
        offsets = bytes((self.sbTlmOffset.value(), self.sbCmdOffsetPri.value(),
                         self.sbCmdOffsetSec.value()))
        with open("/tmp/OffsetData", "wb") as f:
            f.write(offsets)

    # Update the combo box list in gui
    def updateIpList(self, ip, name):
        self.ipAddressesList.append(ip)
        self.spacecraftNames.append(name)
        self.comboBoxIpAddresses.addItem(ip)

    # Start the routing service (see RoutingService.py)
    def initRoutingService(self):
        self.RoutingService = RoutingService()
        self.RoutingService.signalUpdateIpList.connect(self.updateIpList)
        self.RoutingService.start()


#
# Main

#
def main():

    # Report Version Number upon startup
    print(_version_string)
    
    # Init app
    app = QApplication(sys.argv)

    # Init main window
    MainWindow = GroundSystem()

    # Show and put window on front
    MainWindow.show()
    MainWindow.raise_()

    # Start the Routing Service
    MainWindow.initRoutingService()
    MainWindow.saveOffsets()

    # Execute the app
    sys.exit(app.exec_())

if __name__ == "__main__":
   main() 
