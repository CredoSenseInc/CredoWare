# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'loading_widget.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ProgBar(object):
    def setupUi(self, ProgBar):
        ProgBar.setObjectName("ProgBar")
        ProgBar.resize(500, 50)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ProgBar.sizePolicy().hasHeightForWidth())
        ProgBar.setSizePolicy(sizePolicy)
        ProgBar.setMinimumSize(QtCore.QSize(500, 50))
        ProgBar.setMaximumSize(QtCore.QSize(500, 50))
        font = QtGui.QFont()
        font.setFamily("Arial")
        ProgBar.setFont(font)
        ProgBar.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        ProgBar.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.Canada))
        self.verticalLayout = QtWidgets.QVBoxLayout(ProgBar)
        self.verticalLayout.setObjectName("verticalLayout")
        self.progressBar = QtWidgets.QProgressBar(ProgBar)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)

        self.retranslateUi(ProgBar)
        QtCore.QMetaObject.connectSlotsByName(ProgBar)

    def retranslateUi(self, ProgBar):
        _translate = QtCore.QCoreApplication.translate
        ProgBar.setWindowTitle(_translate("ProgBar", "Reading data, please wait"))
