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

import shlex
import subprocess
import sys
import os
import signal
import pathlib

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from RoutingService import RoutingService
from UiMainWindow import UiMainWindow

from _version import __version__ as _version
from _version import _version_string

__version__ = _version

# ROOTDIR = Path(sys.argv[0]).resolve().parent
ROOTDIR = pathlib.Path(__file__).parent.absolute()


#
# CFS Ground System: Setup and manage the main window
#
class GroundSystem(QMainWindow, UiMainWindow):
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

        self.routing_service = None
        self.alert = QMessageBox()

        # set initial defaults
        self.sb_tlm_offset.setValue(self.TLM_HDR_V1_OFFSET)
        self.sb_cmd_offset_pri.setValue(self.CMD_HDR_PRI_V1_OFFSET)
        self.sb_cmd_offset_sec.setValue(self.CMD_HDR_SEC_V1_OFFSET)

        self.push_button_start_tlm.clicked.connect(self.start_tlm_system)
        self.push_button_start_cmd.clicked.connect(self.start_cmd_system)
        self.cb_tlm_header_ver.currentIndexChanged.connect(self.set_tlm_offset)
        self.cb_cmd_header_ver.currentIndexChanged.connect(self.set_cmd_offsets)

        for sb in (self.sb_tlm_offset, self.sb_cmd_offset_pri, self.sb_cmd_offset_sec):
            sb.valueChanged.connect(self.save_offsets)
        # Init lists
        self.ip_addresses_list = ['All']
        self.spacecraft_names = ['All']

    def closeEvent(self, evnt):
        if self.routing_service:
            self.routing_service.stop()
            print("Stopped routing service")
        os.kill(0, signal.SIGKILL)
        super().closeEvent(evnt)

    # Read the selected spacecraft from combo box on GUI
    def get_selected_spacecraft_address(self):
        return self.combo_box_ip_addresses.currentText().strip()

    # Returns the name of the selected spacecraft
    def get_selected_spacecraft_name(self):
        return self.spacecraft_names[self.ip_addresses_list.index(
            self.get_selected_spacecraft_address())].strip()

    #
    # Display popup with error
    #
    def display_error_message(self, message):
        print(message)
        self.alert.setText(message)
        self.alert.setIcon(QMessageBox.Warning)
        self.alert.exec_()

    # Start the telemetry system for the selected spacecraft
    def start_tlm_system(self):
        # Setup the subscription (to let the telemetry
        # system know the messages it will be receiving)
        subscription = '--sub=GroundSystem'
        selected_spacecraft = self.get_selected_spacecraft_name()
        if selected_spacecraft != 'All':
            subscription += f'.{selected_spacecraft}.TelemetryPackets'

        # Open Telemetry System
        system_call = f'python3 {ROOTDIR}/Subsystems/tlmGUI/TelemetrySystem.py {subscription}'
        args = shlex.split(system_call)
        subprocess.Popen(args)

    # Start command system
    @staticmethod
    def start_cmd_system():
        subprocess.Popen(
            ['python3', f'{ROOTDIR}/Subsystems/cmdGui/CommandSystem.py'])

    # Start FDL-FUL gui system
    def start_fdl_system(self):
        selected_spacecraft = self.get_selected_spacecraft_name()
        if selected_spacecraft == 'All':
            self.display_error_message(
                'Cannot open FDL manager.\nNo spacecraft selected.')
        else:
            subscription = f'--sub=GroundSystem.{selected_spacecraft}'
            subprocess.Popen([
                'python3', f'{ROOTDIR}/Subsystems/fdlGui/FdlSystem.py',
                subscription
            ])

    def set_tlm_offset(self):
        selected_ver = self.cb_tlm_header_ver.currentText().strip()
        if selected_ver == "Custom":
            self.sb_tlm_offset.setEnabled(True)
        else:
            self.sb_tlm_offset.setEnabled(False)
            if selected_ver == "1":
                self.sb_tlm_offset.setValue(self.TLM_HDR_V1_OFFSET)
            elif selected_ver == "2":
                self.sb_tlm_offset.setValue(self.TLM_HDR_V2_OFFSET)

    def set_cmd_offsets(self):
        selected_ver = self.cb_cmd_header_ver.currentText().strip()
        if selected_ver == "Custom":
            self.sb_cmd_offset_pri.setEnabled(True)
            self.sb_cmd_offset_sec.setEnabled(True)
        else:
            self.sb_cmd_offset_pri.setEnabled(False)
            self.sb_cmd_offset_sec.setEnabled(False)
            if selected_ver == "1":
                self.sb_cmd_offset_pri.setValue(self.CMD_HDR_PRI_V1_OFFSET)
                self.sb_cmd_offset_sec.setValue(self.CMD_HDR_SEC_V1_OFFSET)
            elif selected_ver == "2":
                self.sb_cmd_offset_pri.setValue(self.CMD_HDR_PRI_V2_OFFSET)
                self.sb_cmd_offset_sec.setValue(self.CMD_HDR_SEC_V2_OFFSET)

    def save_offsets(self):
        offsets = bytes((self.sb_tlm_offset.value(), self.sb_cmd_offset_pri.value(),
                         self.sb_cmd_offset_sec.value()))
        with open("/tmp/OffsetData", "wb") as f:
            f.write(offsets)

    # Update the combo box list in gui
    def update_ip_list(self, ip, name):
        self.ip_addresses_list.append(ip)
        self.spacecraft_names.append(name)
        self.combo_box_ip_addresses.addItem(ip)

    # Start the routing service (see RoutingService.py)
    def init_routing_service(self):
        self.routing_service = RoutingService()
        self.routing_service.signal_update_ip_list.connect(self.update_ip_list)
        self.routing_service.start()


#
# Main

#
def main():
    # Report Version Number upon startup
    print(_version_string)

    # Init app
    app = QApplication(sys.argv)

    # Init main window
    main_window = GroundSystem()

    # Show and put window on front
    main_window.show()
    main_window.raise_()

    # Start the Routing Service
    main_window.init_routing_service()
    main_window.save_offsets()

    # Execute the app
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
