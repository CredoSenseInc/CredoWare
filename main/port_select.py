from PyQt5.QtWidgets import QMainWindow
from port_select_window import Ui_PortSelectWindow
import serial
import serial.tools.list_ports

class MyPortSelectWindow(QMainWindow, Ui_PortSelectWindow):

    def __init__(self, parent=None):
        super(MyPortSelectWindow, self).__init__(parent)
        self.setupUi(self)
        self.ports = []
        self.button_rescan.clicked.connect(self.button_action_refresh_port_list)

    def initialize_and_show(self):
        self.populate_port_list()
        self.show()

    def get_port_list(self):
        self.ports = serial.tools.list_ports.comports(include_links=True)
        print(f'found {len(self.ports)} devices')
        print(self.ports)
        # self.port_info()
        port_links = []
        for each in self.ports:
            port_links.append(each.device)
        return port_links

    def port_info(self):
        for each in self.ports:
            print(f'{each}:')
            print(f'device: {each.device}')
            print(f'name: {each.name}')
            print(f'description: {each.description}')
            print(f'hardware id: {each.hwid}')
            print(f'vid: {each.vid}')
            print(f'pid: {each.pid}')
            print(f'serial number: {each.serial_number}')
            print(f'location: {each.location}')
            print(f'manufacturer: {each.manufacturer}')
            print(f'product: {each.product}')
            print(f'interface: {each.interface}\n')

    def populate_port_list(self):
        port_choice_list = self.get_port_list()
        print(port_choice_list)
        self.comboBox_port_sel.clear()
        self.comboBox_port_sel.addItems(port_choice_list)

    def button_action_refresh_port_list(self):
        self.comboBox_port_sel.clear()
        self.populate_port_list()