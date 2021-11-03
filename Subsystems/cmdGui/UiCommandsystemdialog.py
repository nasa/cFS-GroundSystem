# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/lbleier/cFS/tools/cFS-GroundSystem/Subsystems/cmdGui/CommandSystemDialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class UiCommandsystemdialog(object):
    def setupUi(self, command_system_dialog):
        command_system_dialog.setObjectName("CommandSystemDialog")
        command_system_dialog.resize(772, 1020)
        self.layout_widget_2 = QtWidgets.QWidget(command_system_dialog)
        self.layout_widget_2.setGeometry(QtCore.QRect(80, 20, 621, 25))
        self.layout_widget_2.setObjectName("layoutWidget_2")
        self.horizontal_layout = QtWidgets.QHBoxLayout(self.layout_widget_2)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.setObjectName("horizontalLayout")
        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontal_layout.addItem(spacer_item)
        self.label = QtWidgets.QLabel(self.layout_widget_2)
        self.label.setObjectName("label")
        self.horizontal_layout.addWidget(self.label)
        spacer_item1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontal_layout.addItem(spacer_item1)
        self.layout_widget_3 = QtWidgets.QWidget(command_system_dialog)
        self.layout_widget_3.setGeometry(QtCore.QRect(80, 60, 621, 33))
        self.layout_widget_3.setObjectName("layoutWidget_3")
        self.horizontal_layout_2 = QtWidgets.QHBoxLayout(self.layout_widget_3)
        self.horizontal_layout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout_2.setObjectName("horizontalLayout_2")
        spacer_item2 = QtWidgets.QSpacerItem(90, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontal_layout_2.addItem(spacer_item2)
        spacer_item3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontal_layout_2.addItem(spacer_item3)
        self.label_2 = QtWidgets.QLabel(self.layout_widget_3)
        self.label_2.setObjectName("label_2")
        self.horizontal_layout_2.addWidget(self.label_2)
        spacer_item4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontal_layout_2.addItem(spacer_item4)
        self.button_box = QtWidgets.QDialogButtonBox(self.layout_widget_3)
        self.button_box.setOrientation(QtCore.Qt.Vertical)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.button_box.setCenterButtons(True)
        self.button_box.setObjectName("buttonBox")
        self.horizontal_layout_2.addWidget(self.button_box)
        self.tbl_cmd_sys = QtWidgets.QTableWidget(command_system_dialog)
        self.tbl_cmd_sys.setGeometry(QtCore.QRect(30, 120, 701, 721))
        self.tbl_cmd_sys.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tbl_cmd_sys.setObjectName("tblCmdSys")
        self.tbl_cmd_sys.setColumnCount(5)
        self.tbl_cmd_sys.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tbl_cmd_sys.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tbl_cmd_sys.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tbl_cmd_sys.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tbl_cmd_sys.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tbl_cmd_sys.setHorizontalHeaderItem(4, item)
        self.tbl_cmd_sys.verticalHeader().setVisible(False)

        self.retranslate_ui(command_system_dialog)
        self.button_box.clicked['QAbstractButton*'].connect(command_system_dialog.close)
        QtCore.QMetaObject.connectSlotsByName(command_system_dialog)

    def retranslate_ui(self, command_system_dialog):
        _translate = QtCore.QCoreApplication.translate
        command_system_dialog.setWindowTitle(_translate("CommandSystemDialog", "Command System Main Page"))
        self.label.setText(_translate("CommandSystemDialog", "cFE/CFS Subsystem Commands"))
        self.label_2.setText(_translate("CommandSystemDialog", "Available Pages"))
        item = self.tbl_cmd_sys.horizontalHeaderItem(0)
        item.setText(_translate("CommandSystemDialog", "Subsystem/Page"))
        item = self.tbl_cmd_sys.horizontalHeaderItem(1)
        item.setText(_translate("CommandSystemDialog", "Packet ID"))
        item = self.tbl_cmd_sys.horizontalHeaderItem(2)
        item.setText(_translate("CommandSystemDialog", "Send To"))
