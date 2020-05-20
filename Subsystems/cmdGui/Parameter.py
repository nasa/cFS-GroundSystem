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
import shlex
import subprocess
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QDialog

from HTMLDocsParser import HTMLDocsParser
from ParameterDialog import Ui_Dialog

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

    #
    # Button method
    #
    def ProcessSendButton(self):
        input_list = []
        for j in range(1, 11):
            inputStr = getattr(self, f"input_{j}")
            input_list.append(inputStr.text().strip())

        k = 0
        param_list = []
        while input_list[k]:
            dataType = dataTypesNew[k]
            if dataType == '--string':
                param_list.append(
                    f'{dataType}=\"{stringLen[k]}:{input_list[k]}\"')
            else:
                param_list.append(f'{dataType}={input_list[k]}')  # --byte=4
            k += 1
        param_string = ' '.join(param_list)
        launch_string = (
            f'{ROOTDIR}/../cmdUtil/cmdUtil --host={pageAddress} '
            f'--port={pagePort} --pktid={pagePktId} --endian={pageEndian} '
            f'--cmdcode={cmdCode} {param_string.strip()}')
        cmd_args = shlex.split(launch_string)
        subprocess.Popen(cmd_args)
        self.status_box.setText('Command sent!')


#
# Main method
#
if __name__ == '__main__':
    #
    # Initializes variables
    #
    subsysTitle, cmdDesc, pageEndian, pageAddress, cmdCode, params = (
        '' for _ in range(6))
    idx, pagePktId, pagePort = (0 for _ in range(3))
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
            idx = int(arg)  # comand index in command definition file
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

    #
    # Gets parameter information from pickle files
    #
    pickle_file = f'{ROOTDIR}/ParameterFiles/' + re.split(r'\.', param_file)[0]
    with open(pickle_file, 'rb') as pickle_obj:
        dataTypesOrig, paramNames, paramLen, paramDesc, dataTypesNew, stringLen = pickle.load(
            pickle_obj)

    #
    # Sets text in GUI
    #
    param.subSystemTextBrowser.setText(subsysTitle)  # subsystem name
    param.commandAddressTextBrowser.setText(
        f'{cmdDesc} Command')  # command name

    for i in range(10):
        paramName = getattr(param, f"paramName_{i+1}")
        descrip = getattr(param, f"descrip_{i+1}")
        try:
            paramName.setText(paramNames[i])
            descrip.setText(paramDesc[i])
        except IndexError:
            pass

    #
    # Displays the dialog
    #
    param.show()
    param.raise_()
    sys.exit(app.exec_())
