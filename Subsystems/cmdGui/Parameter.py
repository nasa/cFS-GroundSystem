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
import getopt
import pickle
import re
import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QDialog, QHeaderView,
                             QTableWidgetItem)

from HTMLDocsParser import HTMLDocsParser
from MiniCmdUtil import MiniCmdUtil
from Ui_ParameterDialog import Ui_Dialog

ROOTDIR = Path(sys.argv[0]).resolve().parent


class Parameter(QDialog, Ui_Dialog):
    #
    # Initializes Parameter class
    #
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.parser = HTMLDocsParser()
        self.setWindowTitle("Parameter Dialog")
        self.SendButton_1.clicked.connect(self.ProcessSendButton)
        self.mcu = None

    #
    # Button method
    #
    def ProcessSendButton(self):
        input_list = []
        for j in range(self.tblParameters.rowCount()):
            item = tbl.item(j, 2)
            input_list.append(item.text().strip())

        param_list = []
        for k, inpt in enumerate(input_list):
            dataType = dataTypesNew[k]
            if dataType == '--string':
                param_list.append(f'{dataType}=\"{stringLen[k]}:{inpt}\"')
            else:
                param_list.append(f'{dataType}={inpt}')  # --byte=4
        param_string = ' '.join(param_list)
        self.mcu = MiniCmdUtil(pageAddress, pagePort, pageEndian, pagePktId,
                               cmdCode, param_string.strip())
        sendSuccess = self.mcu.sendPacket()
        if sendSuccess:
            self.status_box.setText('Command sent!')
        else:
            self.status_box.setText('Error occured')

    def closeEvent(self, event):
        if self.mcu:
            self.mcu.mm.close()
        super().closeEvent(event)


#
# Main method
#
if __name__ == '__main__':
    #
    # Initializes variables
    #
    subsysTitle, cmdDesc, pageEndian, pageAddress, cmdCode, params = (
        '' for _ in range(6))
    pagePktId, pagePort = 0, 0
    param_file = 'struct_c_f_e___e_s___start_app_cmd__t.html'

    #
    # Process command line arguments
    #
    opts, args = getopt.getopt(sys.argv[1:], "tdihppecf", [
        "title=", "descrip=", "idx=", "host=", "port=", "pktid=", "endian=",
        "cmdcode=", "file="
    ])

    for opt, arg in opts:
        if opt in ("-t", "--title"):
            subsysTitle = arg  # subsystem name, eg Telemetry
        elif opt in ("-d", "--descrip"):
            cmdDesc = arg  # command name, eg No-Op
        elif opt in ("-i", "--idx"):
            _ = int(arg)  # command index in command definition file
        elif opt in ("-h", "--host"):
            pageAddress = arg  # send to address
        elif opt in ("-p", "--port"):
            pagePort = arg  # port number
        elif opt in ("-p", "--pktid"):
            pagePktId = arg  # packet ID
        elif opt in ("-e", "--endian"):
            pageEndian = arg  # LE or BE
        elif opt in ("-c", "--cmdcode"):
            cmdCode = arg  # command code
        elif opt in ("-f", "--file"):
            param_file = arg  # parameter definition file

    #
    # Initializes QT application and Parameter class
    #
    app = QApplication(sys.argv)  # creates instance of QtApplication class
    param = Parameter()  # creates instance of Parameter class
    tbl = param.tblParameters

    #
    # Gets parameter information from pickle files
    #
    pickle_file = f'{ROOTDIR}/ParameterFiles/' + re.split(r'\.', param_file)[0]
    with open(pickle_file, 'rb') as pickle_obj:
        _, paramNames, _, paramDesc, dataTypesNew, stringLen = pickle.load(
            pickle_obj)

    #
    # Sets text in GUI
    #
    param.subSystemTextBrowser.setText(subsysTitle)  # subsystem name
    param.commandAddressTextBrowser.setText(
        f'{cmdDesc} Command')  # command name

    for i, name in enumerate(paramNames):
        tbl.insertRow(i)
        ## Create and insert the table items
        for n in range(tbl.columnCount()):
            tblItem = QTableWidgetItem()
            tbl.setItem(i, n, tblItem)
        ## Make the first two items in each row uneditable
        for n in range(tbl.columnCount() - 1):
            tbl.item(i, n).setFlags(Qt.ItemIsEnabled)
        try:
            tbl.item(i, 0).setText(name)
            tbl.item(i, 1).setText(paramDesc[i])
        except IndexError:
            pass  # Ignore nonexistent array items
    tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    # tbl.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

    #
    # Displays the dialog
    #
    param.show()
    param.raise_()
    sys.exit(app.exec_())
