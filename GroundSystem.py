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
#cFS Ground System Version 2.0.0
#
#!/usr/bin/env python3
#
import shlex
import subprocess
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from MainWindow import Ui_MainWindow
from RoutingService import RoutingService

ROOTDIR = Path(sys.argv[0]).resolve().parent


#
# CFS Ground System: Setup and manage the main window
#
class GroundSystem(QMainWindow, Ui_MainWindow):
    #
    # Init the class
    #
    def __init__(self):
        super().__init__()
        self.setupUi((self))

        self.RoutingService = None
        self.alert = QMessageBox()

        self.pushButtonStartTlm.clicked.connect(self.startTlmSystem)
        self.pushButtonStartCmd.clicked.connect(self.startCmdSystem)
        # Init lists
        self.ipAddressesList = ['All']
        self.spacecraftNames = ['All']

    def closeEvent(self, evnt):
        if self.RoutingService:
            self.RoutingService.stop()
            print("Stopped routing service")

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
        selectedSpacecraft = self.getSelectedSpacecraftName()

        # Setup the subscription (to let know the
        # telemetry system the messages it will be receiving)
        if selectedSpacecraft == 'All':
            subscription = '--sub=GroundSystem'
        else:
            subscription = f'--sub=GroundSystem.{selectedSpacecraft}.TelemetryPackets'

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
            subscription = ''
            self.DisplayErrorMessage(
                'Cannot open FDL manager.\nNo spacecraft selected.')
        else:
            subscription = f'--sub=GroundSystem.{selectedSpacecraft}'
            subprocess.Popen([
                'python3', f'{ROOTDIR}/Subsystems/fdlGui/FdlSystem.py',
                subscription
            ])

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
if __name__ == "__main__":

    # Init app
    app = QApplication(sys.argv)

    # Init main window
    MainWindow = GroundSystem()

    # Show and put window on front
    MainWindow.show()
    MainWindow.raise_()

    # Start the Routing Service
    MainWindow.initRoutingService()

    # Execute the app
    sys.exit(app.exec_())
