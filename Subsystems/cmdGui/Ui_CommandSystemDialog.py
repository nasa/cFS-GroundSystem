# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/lbleier/cFS/tools/cFS-GroundSystem/Subsystems/cmdGui/CommandSystemDialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CommandSystemDialog(object):
    def setupUi(self, CommandSystemDialog):
        CommandSystemDialog.setObjectName("CommandSystemDialog")
        CommandSystemDialog.resize(772, 1020)
        self.layoutWidget_2 = QtWidgets.QWidget(CommandSystemDialog)
        self.layoutWidget_2.setGeometry(QtCore.QRect(80, 20, 621, 25))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(self.layoutWidget_2)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.layoutWidget_3 = QtWidgets.QWidget(CommandSystemDialog)
        self.layoutWidget_3.setGeometry(QtCore.QRect(80, 60, 621, 33))
        self.layoutWidget_3.setObjectName("layoutWidget_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget_3)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem2 = QtWidgets.QSpacerItem(90, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget_3)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem4)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.layoutWidget_3)
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout_2.addWidget(self.buttonBox)
        self.tblCmdSys = QtWidgets.QTableWidget(CommandSystemDialog)
        self.tblCmdSys.setGeometry(QtCore.QRect(30, 120, 701, 721))
        self.tblCmdSys.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tblCmdSys.setObjectName("tblCmdSys")
        self.tblCmdSys.setColumnCount(5)
        self.tblCmdSys.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tblCmdSys.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblCmdSys.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblCmdSys.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblCmdSys.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblCmdSys.setHorizontalHeaderItem(4, item)
        self.tblCmdSys.verticalHeader().setVisible(False)

        self.retranslateUi(CommandSystemDialog)
        self.buttonBox.clicked['QAbstractButton*'].connect(CommandSystemDialog.close)
        QtCore.QMetaObject.connectSlotsByName(CommandSystemDialog)

    def retranslateUi(self, CommandSystemDialog):
        _translate = QtCore.QCoreApplication.translate
        CommandSystemDialog.setWindowTitle(_translate("CommandSystemDialog", "Command System Main Page"))
        self.label.setText(_translate("CommandSystemDialog", "cFE/CFS Subsystem Commands"))
        self.label_2.setText(_translate("CommandSystemDialog", "Available Pages"))
        item = self.tblCmdSys.horizontalHeaderItem(0)
        item.setText(_translate("CommandSystemDialog", "Subsystem/Page"))
        item = self.tblCmdSys.horizontalHeaderItem(1)
        item.setText(_translate("CommandSystemDialog", "Packet ID"))
        item = self.tblCmdSys.horizontalHeaderItem(2)
        item.setText(_translate("CommandSystemDialog", "Send To"))

