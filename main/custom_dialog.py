from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QWidget, QPushButton
from PyQt5.QtCore import QBasicTimer


class ProgBar(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.pbar = QProgressBar(self)
        self.pbar.setValue(10)
        self.setWindowTitle('Reading data, please wait')
        self.resize(500,50)
        self.pbar.resize(500,30)
        self.show()


# class CustomDialog(QDialog):
#
#     def __init__(self, *args, **kwargs):
#         super(QDialog, self).__init__(*args, **kwargs)
#
#         self.setWindowTitle("Reading data... \nPlease wait")
#
#         self.lbl = QLabel("Reading data... \nPlease wait")
#         self.lbl.setAlignment(Qt.AlignCenter)
#         self.lbl.setFont(QFont('Arial', 15))
#
#         self.layout = QVBoxLayout()
#         self.layout.addWidget(self.lbl)
#         self.setLayout(self.layout)
#         self.resize(300, 100)
