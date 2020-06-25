# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/lbleier/cFS/tools/cFS-GroundSystem/Subsystems/tlmGUI/EventMessageDialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EventMessageDialog(object):
    def setupUi(self, EventMessageDialog):
        EventMessageDialog.setObjectName("EventMessageDialog")
        EventMessageDialog.resize(591, 277)
        self.verticalLayout = QtWidgets.QVBoxLayout(EventMessageDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(EventMessageDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QtCore.QSize(91, 17))
        self.label_2.setMaximumSize(QtCore.QSize(135, 29))
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.sequenceCount = QtWidgets.QSpinBox(EventMessageDialog)
        self.sequenceCount.setReadOnly(True)
        self.sequenceCount.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.sequenceCount.setMaximum(16384)
        self.sequenceCount.setObjectName("sequenceCount")
        self.horizontalLayout.addWidget(self.sequenceCount)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.line = QtWidgets.QFrame(EventMessageDialog)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.label = QtWidgets.QLabel(EventMessageDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.line_2 = QtWidgets.QFrame(EventMessageDialog)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout.addWidget(self.line_2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        spacerItem2 = QtWidgets.QSpacerItem(81, 31, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.buttonBox = QtWidgets.QDialogButtonBox(EventMessageDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.eventOutput = QtWidgets.QPlainTextEdit(EventMessageDialog)
        self.eventOutput.setReadOnly(True)
        self.eventOutput.setObjectName("eventOutput")
        self.verticalLayout.addWidget(self.eventOutput)

        self.retranslateUi(EventMessageDialog)
        self.buttonBox.clicked['QAbstractButton*'].connect(EventMessageDialog.close)
        QtCore.QMetaObject.connectSlotsByName(EventMessageDialog)

    def retranslateUi(self, EventMessageDialog):
        _translate = QtCore.QCoreApplication.translate
        EventMessageDialog.setWindowTitle(_translate("EventMessageDialog", "Event Messages"))
        self.label_2.setText(_translate("EventMessageDialog", "Sequence Count"))
        self.label.setText(_translate("EventMessageDialog", "Events"))

