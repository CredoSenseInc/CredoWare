from PyQt5.QtWidgets import QMainWindow
from about_window import Ui_About
from urllib.request import urlopen
import webbrowser
import semantic_version


class MyAboutWindow(QMainWindow, Ui_About):

    def __init__(self, parent=None):
        super(MyAboutWindow, self).__init__(parent)
        self.setupUi(self)

        self.version = semantic_version.Version('1.0.4')
        self.version_number.setText(str(self.version))
        self.btn_update_chk.clicked.connect(self.check_update_button)

    def initialize_and_show(self):
        self.show()

    def check_update_button(self):
        self.btn_update_chk.setText("Checking for update")
        try:
            ver_chk = urlopen("https://raw.githubusercontent.com/CredoSenseInc/CredoWare/master/__version__"
                              "").read().decode('utf-8').rstrip('\n')
            if (semantic_version.Version(str(ver_chk))> self.version):
                self.btn_update_chk.setText("Update available.\nLatest version: "+ver_chk+"\nClick for download page")
                self.btn_update_chk.clicked.disconnect(self.check_update_button)
                self.btn_update_chk.clicked.connect(self.gotowebsite)
            else:
                self.btn_update_chk.setText("You have the latest version")
                self.btn_update_chk.clicked.disconnect(self.check_update_button)
        except:
            self.btn_update_chk.setText("Error, click to retry")
            pass

    def gotowebsite(self):
        webbrowser.open_new_tab('https://credosense.com/downloads/')