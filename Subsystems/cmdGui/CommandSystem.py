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
import pickle
import shlex
import subprocess
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QDialog

from CommandSystemDialog import Ui_CommandSystemDialog

ROOTDIR = Path(sys.argv[0]).resolve().parent


class CommandSystem(QDialog, Ui_CommandSystemDialog):

    #
    # Init the class
    #
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.move(800, 100)

        for n in range(21):
            btn = getattr(self, f"pushButton_{n}")
            btn.clicked.connect(lambda _, x=n: self.ProcessButtonGeneric(x))

        for l in range(22):
            btn = getattr(self, f"quickButton_{l+1}")
            btn.clicked.connect(lambda _, x=l: self.ProcessQuickButton(x))

    #
    # Processes 'Display Page' button
    #
    def ProcessButtonGeneric(self, idx):
        if cmdPageIsValid[idx]:
            lePID = getattr(self, f'lineEditPktId_{idx}')
            leAddr = getattr(self, f'lineEdit_{idx}')
            pktId = lePID.text()
            address = leAddr.text()
            launch_string = (
                f'python3 {ROOTDIR}/{cmdClass[0]} '
                f'--title=\"{cmdPageDesc[idx]}\" --pktid={pktId} '
                f'--file={cmdPageDefFile[idx]} --address=\"{address}\" '
                f'--port={cmdPagePort[idx]} --endian={cmdPageEndian[idx]}')
            cmd_args = shlex.split(launch_string)
            subprocess.Popen(cmd_args)

    #
    # Determines if command requires parameters
    #
    @staticmethod
    def checkParams(idx):
        pickle_file = f'{ROOTDIR}/ParameterFiles/{quickParam[idx]}'
        try:
            with open(pickle_file, 'rb') as pickle_obj:
                paramNames = pickle.load(pickle_obj)[1]
            return len(paramNames) > 0
        except IOError:
            return False

    #
    # Processes quick button
    #
    def ProcessQuickButton(self, idx):
        if cmdPageIsValid[idx] and quickIndices[idx] >= 0:
            qIdx = quickIndices[idx]
            lePID = getattr(self, f'lineEditPktId_{idx}')
            leAddr = getattr(self, f'lineEdit_{idx}')
            pktId = lePID.text()
            address = leAddr.text()

            # if requires parameters
            if self.checkParams(qIdx):
                launch_string = (
                    f'python3 {ROOTDIR}/Parameter.py '
                    f'--title=\"{subsys[qIdx]}\" '
                    f'--descrip=\"{quickCmd[qIdx]}\" '
                    f'--idx={idx} --host=\"{address}\" '
                    f'--port={quickPort[qIdx]} '
                    f'--pktid={pktId} --endian={quickEndian[qIdx]} '
                    f'--cmdcode={quickCode[qIdx]} --file={quickParam[qIdx]}')
            # if doesn't require parameters
            else:
                launch_string = (
                    f'{ROOTDIR}/../cmdUtil/cmdUtil '
                    f'--host=\"{address}\" --port={quickPort[qIdx]} '
                    f'--pktid={pktId} --endian={quickEndian[qIdx]} '
                    f'--cmdcode={quickCode[qIdx]}')
            cmd_args = shlex.split(launch_string)
            subprocess.Popen(cmd_args)


#
# Main
#
if __name__ == '__main__':

    #
    # Set defaults for the arguments
    #
    cmdDefFile = "command-pages.txt"

    #
    # Init the QT application and the telemetry dialog class
    #
    app = QApplication(sys.argv)
    Command = CommandSystem()

    #
    # Read in the contents of the telemetry packet definition
    #
    cmdPageIsValid, cmdPageDesc, cmdPageDefFile, cmdPageAppid, \
        cmdPageEndian, cmdClass, cmdPageAddress, cmdPagePort = ([] for _ in range(8))

    i = 0

    with open(f"{ROOTDIR}/{cmdDefFile}") as cmdfile:
        reader = csv.reader(cmdfile, skipinitialspace=True)
        for cmdRow in reader:
            try:
                if cmdRow[0][0] != '#':
                    cmdPageIsValid.append(True)
                    cmdPageDesc.append(cmdRow[0])
                    cmdPageDefFile.append(cmdRow[1])
                    cmdPageAppid.append(int(cmdRow[2], 16))
                    cmdPageEndian.append(cmdRow[3])
                    cmdClass.append(cmdRow[4])
                    cmdPageAddress.append(cmdRow[5])
                    cmdPagePort.append(int(cmdRow[6]))
                    i += 1
            except IndexError as e:
                fullErr = repr(e)
                errName = fullErr[:fullErr.index('(')]
                print(f"{errName}:", e)
                print(("This could be due to improper formatting in "
                       "command-pages.txt.\nThis is a common error "
                       "caused by blank lines in command-pages.txt"))
    #
    # Mark the remaining values as invalid
    #
    for j in range(i, 22):
        cmdPageAppid.append(0)
        cmdPageIsValid.append(False)

    #
    # Read in contents of quick button definition file
    #
    quickDefFile = 'quick-buttons.txt'
    subsys, subsysFile, quickCmd, quickCode, quickPktId,\
        quickEndian, quickAddress, quickPort, quickParam, \
            quickIndices = ([] for _ in range(10))

    with open(f'{ROOTDIR}/{quickDefFile}') as subFile:
        reader = csv.reader(subFile)
        for fileRow in reader:
            if fileRow[0][0] != '#':
                subsys.append(fileRow[0])
                subsysFile.append(fileRow[1])
                quickCmd.append(fileRow[2].strip())
                quickCode.append(fileRow[3].strip())
                quickPktId.append(fileRow[4].strip())
                quickEndian.append(fileRow[5].strip())
                quickAddress.append(fileRow[6].strip())
                quickPort.append(fileRow[7].strip())
                quickParam.append(fileRow[8].strip())

    #
    # fill the data fields on the page
    #
    for k in range(22):
        subsysBrowser = getattr(Command, f'SubsysBrowser_{k}')
        if cmdPageIsValid[k]:
            lineEditPktId = getattr(Command, f'lineEditPktId_{k}')
            lineEditAddress = getattr(Command, f'lineEdit_{k}')
            quickButton = getattr(Command, f'quickButton_{k+1}')
            subsysBrowser.setText(cmdPageDesc[k])
            lineEditPktId.setText(hex(cmdPageAppid[k]))
            lineEditAddress.setText(cmdPageAddress[k])
            quickIdx = -1
            try:
                quickIdx = subsys.index(cmdPageDesc[k])
                quickButton.setText(quickCmd[quickIdx])
            except ValueError:
                pass
            quickIndices.append(quickIdx)
        else:
            subsysBrowser.setText("(unused)")

    #
    # Display the page
    #
    Command.show()
    Command.raise_()
    print('Command System started.')
    sys.exit(app.exec_())
