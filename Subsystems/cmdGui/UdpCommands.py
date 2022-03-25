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
# UdpCommands.py -- This is a class that creates a simple command dialog and
#                   sends commands using the cmdUtil UDP C program.
#
#                   The commands that can be sent are defined in comma
#                   delimited text files.
#                   This class deals with one set of commands in a file (up
#                   to 20) but multiple subsystems can be represented by
#                   spawning this class multiple times.
#
#                   This class could be duplicated to send over another
#                   interface such as TCP, Cubesat Space Protocol, or Xbee
#                   wireless radio
#
import getopt
import pickle
import shlex
import subprocess
import sys
from pathlib import Path

from PyQt5.QtWidgets import (QApplication, QDialog, QHeaderView, QPushButton,
                             QTableWidgetItem)

from MiniCmdUtil import MiniCmdUtil
from UiGenericcommanddialog import UiGenericcommanddialog

# ../cFS/tools/cFS-GroundSystem/Subsystems/cmdGui/
ROOTDIR = Path(sys.argv[0]).resolve().parent


class SubsystemCommands(QDialog, UiGenericcommanddialog):
    #
    # Init the class
    #
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(page_title)
        self.mcu = None

    #
    # Determines if command requires parameters
    #
    @staticmethod
    def check_params(idx):
        pf = f'{ROOTDIR}/ParameterFiles/{param_files[idx]}'
        try:
            with open(pf, 'rb') as po:
                param_names = pickle.load(po)[1]
            return len(param_names) > 0  # if has parameters
        except IOError:
            return False

    #
    # Generic button press method
    #
    def process_send_button_generic(self, idx):
        if cmd_item_is_valid[idx]:
            param_bool = self.check_params(idx)
            address = self.command_address_line_edit.text()

            # If parameters are required, launches Parameters page
            if param_bool:
                launch_string = (
                    f'python3 {ROOTDIR}/Parameter.py --title=\"{page_title}\" '
                    f'--descrip=\"{cmd_desc[idx]}\" --idx={idx} '
                    f'--host=\"{address}\" --port={page_port} '
                    f'--pktid={page_pkt_id} --endian={page_endian} '
                    f'--cmdcode={cmd_codes[idx]} --file={param_files[idx]}')
                cmd_args = shlex.split(launch_string)
                subprocess.Popen(cmd_args)
            # If parameters not required, directly calls cmdUtil to send command
            else:
                self.mcu = MiniCmdUtil(address, page_port, page_endian,
                                       page_pkt_id, cmd_codes[idx])
                send_success = self.mcu.send_packet()
                print("Command sent successfully:", send_success)
                # launch_string = (
                #     f'{ROOTDIR.parent}/cmdUtil/cmdUtil --host=\"{address}\" '
                #     f'--port={pagePort} --pktid={pagePktId} '
                #     f'--endian={pageEndian} --cmdcode={cmdCodes[idx]}')

    def closeEvent(self, event):
        if self.mcu:
            self.mcu.mm.close()
        super().closeEvent(event)


#
# Display usage
#
def usage():
    print((
        "Must specify --title=<page name> --file=<cmd_def_file> "
        "--pktid=<packet_app_id(hex)> --endian=<LE|BE> --address=<IP address> "
        "--port=<UDP port>\n\nexample: --title=\"Executive Services\" "
        "--file=cfe-es-cmds.txt --pktid=1806 --endian=LE --address=127.0.0.1 "
        "--port=1234"))


#
# Main
#
if __name__ == '__main__':
    #
    # Set defaults for the arguments
    #
    page_title = "Command Page"
    page_port = 1234
    page_address = "127.0.0.1"
    page_pkt_id = 1801
    page_endian = "LE"
    page_def_file = "cfe__es__msg_8h"

    #
    # process cmd line args
    #
    try:
        opts, args = getopt.getopt(sys.argv[1:], "htpfeap", [
            "help", "title=", "pktid=", "file=", "endian=", "address=", "port="
        ])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-t", "--title"):
            page_title = arg
        elif opt in ("-f", "--file"):
            page_def_file = arg
        elif opt in ("-p", "--pktid"):
            page_pkt_id = arg
        elif opt in ("-e", "--endian"):
            page_endian = arg
        elif opt in ("-a", "--address"):
            page_address = arg
        elif opt in ("-p", "--port"):
            page_port = arg

    #
    # Init the QT application and the command class
    #
    app = QApplication(sys.argv)
    commands = SubsystemCommands()
    commands.sub_system_line_edit.setText(page_title)
    commands.packet_id.display(page_pkt_id)
    commands.command_address_line_edit.setText(page_address)
    tbl = commands.tbl_commands

    #
    # Reads commands from command definition file
    #
    pickle_file = f'{ROOTDIR}/CommandFiles/{page_def_file}'
    with open(pickle_file, 'rb') as pickle_obj:
        cmd_desc, cmd_codes, param_files = pickle.load(pickle_obj)

    cmd_item_is_valid = []
    for i in range(len(cmd_desc)):
        cmd_item_is_valid.append(True)

    #
    # Fill the data fields on the page
    #
    for i, cmd in enumerate(cmd_desc):
        if cmd_item_is_valid[i]:
            tbl.insertRow(i)
            tbl_item = QTableWidgetItem(cmd_desc[i])
            tbl.setItem(i, 0, tbl_item)
            tbl_btn = QPushButton("Send")
            tbl_btn.clicked.connect(
                lambda _, x=i: commands.process_send_button_generic(x))
            tbl.setCellWidget(i, 1, tbl_btn)
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    tbl.horizontalHeader().setStretchLastSection(True)
    # tbl.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

    #
    # Display the page
    #
    commands.show()
    commands.raise_()
    sys.exit(app.exec_())
