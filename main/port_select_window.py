# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'port_select_window.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PortSelectWindow(object):
    def setupUi(self, PortSelectWindow):
        PortSelectWindow.setObjectName("PortSelectWindow")
        PortSelectWindow.resize(363, 208)
        PortSelectWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(PortSelectWindow)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.label_dev_port = QtWidgets.QLabel(self.centralwidget)
        self.label_dev_port.setStyleSheet("padding:10px;")
        self.label_dev_port.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_dev_port.setObjectName("label_dev_port")
        self.gridLayout.addWidget(self.label_dev_port, 2, 1, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 6, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 0, 1, 1, 2)
        self.comboBox_port_sel = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_port_sel.setStyleSheet("QComboBox{\n"
"    padding: 1px 18px 1px 3px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    padding: 1px 2px 1px 2px;\n"
"}")
        self.comboBox_port_sel.setObjectName("comboBox_port_sel")
        self.gridLayout.addWidget(self.comboBox_port_sel, 2, 3, 1, 2)
        self.button_select_port = QtWidgets.QPushButton(self.centralwidget)
        self.button_select_port.setStyleSheet("QPushButton{\n"
"    padding: 5px;\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"    padding: 5px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    padding: 5px;\n"
"}")
        self.button_select_port.setObjectName("button_select_port")
        self.gridLayout.addWidget(self.button_select_port, 5, 3, 1, 2)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 2, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 5, 1, 1, 1)
        self.button_rescan = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_rescan.sizePolicy().hasHeightForWidth())
        self.button_rescan.setSizePolicy(sizePolicy)
        self.button_rescan.setStyleSheet("QPushButton{\n"
"    padding: 4px;\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"    padding: 4px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    padding: 4px;\n"
"}")
        self.button_rescan.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("reload.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_rescan.setIcon(icon)
        self.button_rescan.setObjectName("button_rescan")
        self.gridLayout.addWidget(self.button_rescan, 2, 5, 1, 1)
        self.label_port_sel_stat = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_port_sel_stat.setFont(font)
        self.label_port_sel_stat.setStyleSheet("padding: 10px;")
        self.label_port_sel_stat.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing)
        self.label_port_sel_stat.setObjectName("label_port_sel_stat")
        self.gridLayout.addWidget(self.label_port_sel_stat, 1, 1, 1, 5)
        PortSelectWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(PortSelectWindow)
        QtCore.QMetaObject.connectSlotsByName(PortSelectWindow)

    def retranslateUi(self, PortSelectWindow):
        _translate = QtCore.QCoreApplication.translate
        PortSelectWindow.setWindowTitle(_translate("PortSelectWindow", "MainWindow"))
        self.label_dev_port.setText(_translate("PortSelectWindow", "Select port"))
        self.button_select_port.setText(_translate("PortSelectWindow", "Continue"))
        self.label_port_sel_stat.setText(_translate("PortSelectWindow", "Select the port on which CreDock is connected"))
