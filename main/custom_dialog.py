from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget

from loading_widget import Ui_ProgBar


# class ProgBar(QtWidgets):
#
#     def __init__(self):
#         super().__init__()
#         progressbar = Ui_ProgBar()
#         self.progress_window = progressbar.setupUi()
#         self.progress_window.show

class ProgBar(QWidget, Ui_ProgBar):

    def __init__(self, parent=None):
        super(ProgBar, self).__init__(parent)

        self.setupUi(self)

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
