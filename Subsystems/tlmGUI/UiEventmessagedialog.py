# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/lbleier/cFS/tools/cFS-GroundSystem/Subsystems/tlmGUI/EventMessageDialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class UiEventmessagedialog(object):
    def setup_ui(self, event_message_dialog):
        event_message_dialog.setObjectName("EventMessageDialog")
        event_message_dialog.resize(591, 277)
        self.vertical_layout = QtWidgets.QVBoxLayout(event_message_dialog)
        self.vertical_layout.setObjectName("verticalLayout")
        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.horizontal_layout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(event_message_dialog)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(size_policy)
        self.label_2.setMinimumSize(QtCore.QSize(91, 17))
        self.label_2.setMaximumSize(QtCore.QSize(135, 29))
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.horizontal_layout.addWidget(self.label_2)
        self.sequence_count = QtWidgets.QSpinBox(event_message_dialog)
        self.sequence_count.setReadOnly(True)
        self.sequence_count.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.sequence_count.setMaximum(16384)
        self.sequence_count.setObjectName("sequenceCount")
        self.horizontal_layout.addWidget(self.sequence_count)
        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontal_layout.addItem(spacer_item)
        self.line = QtWidgets.QFrame(event_message_dialog)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontal_layout.addWidget(self.line)
        self.label = QtWidgets.QLabel(event_message_dialog)
        self.label.setObjectName("label")
        self.horizontal_layout.addWidget(self.label)
        self.line_2 = QtWidgets.QFrame(event_message_dialog)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontal_layout.addWidget(self.line_2)
        spacer_item1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontal_layout.addItem(spacer_item1)
        spacer_item2 = QtWidgets.QSpacerItem(81, 31, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontal_layout.addItem(spacer_item2)
        self.button_box = QtWidgets.QDialogButtonBox(event_message_dialog)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.button_box.setObjectName("buttonBox")
        self.horizontal_layout.addWidget(self.button_box)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.event_output = QtWidgets.QPlainTextEdit(event_message_dialog)
        self.event_output.setReadOnly(True)
        self.event_output.setObjectName("eventOutput")
        self.vertical_layout.addWidget(self.event_output)

        self.retranslateUi(event_message_dialog)
        self.button_box.clicked['QAbstractButton*'].connect(event_message_dialog.close)
        QtCore.QMetaObject.connectSlotsByName(event_message_dialog)

    def retranslateUi(self, event_message_dialog):
        _translate = QtCore.QCoreApplication.translate
        event_message_dialog.setWindowTitle(_translate("EventMessageDialog", "Event Messages"))
        self.label_2.setText(_translate("EventMessageDialog", "Sequence Count"))
        self.label.setText(_translate("EventMessageDialog", "Events"))

