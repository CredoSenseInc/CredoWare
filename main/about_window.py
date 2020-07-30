# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'About_window.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_About(object):
    def setupUi(self, About):
        About.setObjectName("About")
        About.resize(341, 200)
        About.setMaximumSize(QtCore.QSize(350, 200))
        self.centralwidget = QtWidgets.QWidget(About)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.versionlabel = QtWidgets.QLabel(self.centralwidget)
        self.versionlabel.setObjectName("versionlabel")
        self.horizontalLayout.addWidget(self.versionlabel)
        self.version_number = QtWidgets.QLabel(self.centralwidget)
        self.version_number.setObjectName("version_number")
        self.horizontalLayout.addWidget(self.version_number)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout_3.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.btn_update_chk = QtWidgets.QPushButton(self.centralwidget)
        self.btn_update_chk.setObjectName("btn_update_chk")
        self.gridLayout_3.addWidget(self.btn_update_chk, 5, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem1, 1, 0, 1, 2)
        spacerItem2 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem2, 4, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 3, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_3, 1, 4, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 1, 3, 1, 1)
        self.logo = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logo.sizePolicy().hasHeightForWidth())
        self.logo.setSizePolicy(sizePolicy)
        self.logo.setMinimumSize(QtCore.QSize(70, 70))
        self.logo.setMaximumSize(QtCore.QSize(70, 70))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap("logo.png"))
        self.logo.setScaledContents(True)
        self.logo.setAlignment(QtCore.Qt.AlignCenter)
        self.logo.setObjectName("logo")
        self.gridLayout.addWidget(self.logo, 1, 2, 1, 1)
        About.setCentralWidget(self.centralwidget)

        self.retranslateUi(About)
        QtCore.QMetaObject.connectSlotsByName(About)

    def retranslateUi(self, About):
        _translate = QtCore.QCoreApplication.translate
        About.setWindowTitle(_translate("About", "About"))
        self.label.setText(_translate("About", "CredoWare"))
        self.versionlabel.setText(_translate("About", "Version: "))
        self.version_number.setText(_translate("About", "1.0"))
        self.btn_update_chk.setText(_translate("About", "Check for Update"))
        self.label_2.setText(_translate("About", "CredoWare is developed by \n"
"CredoSense Limited Inc.\n"
"Licensed underThe 3-Clause BSD License\n"
"licensing details:\n"
"https://opensource.org/licenses/BSD-3-Clause"))
