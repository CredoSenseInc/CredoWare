# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'device_model_window.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Device_Selector(object):
    def setupUi(self, Device_Selector):
        Device_Selector.setObjectName("Device_Selector")
        Device_Selector.resize(362, 228)
        self.centralwidget = QtWidgets.QWidget(Device_Selector)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 5, 0, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 6, 0, 1, 3)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.gridLayout.addWidget(self.comboBox, 0, 2, 1, 1, QtCore.Qt.AlignRight)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1, QtCore.Qt.AlignLeft)
        spacerItem2 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem2, 3, 0, 1, 3)
        self.bottom_label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bottom_label.sizePolicy().hasHeightForWidth())
        self.bottom_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.bottom_label.setFont(font)
        self.bottom_label.setStyleSheet("color: rgb(240, 55, 0);")
        self.bottom_label.setAlignment(QtCore.Qt.AlignCenter)
        self.bottom_label.setObjectName("bottom_label")
        self.gridLayout.addWidget(self.bottom_label, 7, 0, 1, 3)
        self.resetButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.resetButton.sizePolicy().hasHeightForWidth())
        self.resetButton.setSizePolicy(sizePolicy)
        self.resetButton.setObjectName("resetButton")
        self.gridLayout.addWidget(self.resetButton, 9, 0, 3, 3)
        Device_Selector.setCentralWidget(self.centralwidget)

        self.retranslateUi(Device_Selector)
        QtCore.QMetaObject.connectSlotsByName(Device_Selector)

    def retranslateUi(self, Device_Selector):
        _translate = QtCore.QCoreApplication.translate
        Device_Selector.setWindowTitle(_translate("Device_Selector", "MainWindow"))
        self.comboBox.setItemText(0, _translate("Device_Selector", "CSL-T0.5"))
        self.comboBox.setItemText(1, _translate("Device_Selector", "CSL-H2 T0.2"))
        self.label.setText(_translate("Device_Selector", "Please select device model"))
        self.bottom_label.setText(_translate("Device_Selector", "WARNING! \n"
"Selecting wrong device model\n"
"will lead to device malfunction"))
        self.resetButton.setText(_translate("Device_Selector", "Reset Device"))
