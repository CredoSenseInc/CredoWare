import time
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication

from MySingleton import SingletonMeta


class DataReader(metaclass=SingletonMeta):

    def __init__(self):
        self.ser = None
        self.ports = []

    def get_connected_device(self):
        self.ports = serial.tools.list_ports.comports(include_links=True)
        device = None
        for each in self.ports:
            if each.vid == 1027 or each.manufacturer == 'FTDI' or each.pid == 24577:
                device = each
                break
        return device

    def is_port_open(self):
        if self.ser is None:
            return False
        return self.ser.isOpen()

    def open(self, url):
        print(url)
        if self.ser is None:
            self.ser = serial.Serial(url, 2000000, timeout=3)
            time.sleep(2)
            print('port opened')
        elif not self.is_port_open():
            self.ser.open()
            time.sleep(2)
            print('port opened')

    def close(self):
        if self.ser and self.is_port_open():
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.ser.close()
            self.ser = None
            print('port closed')

    def read_data(self, task_type):
        global data
        from task_consumer import TaskTypes
        # print(task_type)
        self.ser.write(task_type.encode('ascii'))
        # print('aise toh')
        data_lst = []
        while True:
            if not self.is_port_open():
                break
            try:
                data = self.ser.readline().decode('utf-8').rstrip('\r\n')
            except:
                pass
            if data == "ready":
                break
            else:
                if not task_type == TaskTypes.SERIAL_ERASE:
                    data_lst.append(data)

        if task_type == TaskTypes.SERIAL_READ_LOGGER_DATA:
            return data_lst
        if not task_type == TaskTypes.SERIAL_ERASE:
            try:
                return data_lst[0]
            except:
                return None
        else:
            return None

    def write_data(self, task_type, new_data):
        self.ser.write(task_type.encode('ascii'))
        while True:
            data = self.ser.readline().decode('utf-8').rstrip('\r\n')
            if data == "ready":
                break

        self.ser.write(new_data.encode('ascii'))
        while True:
            data = self.ser.readline().decode('utf-8').rstrip('\r\n')
            if data == "ready":
                break

        return 'OK'

    def write_then_read_data(self, task_type, send_data):
        self.ser.write(task_type.encode('ascii'))
        while True:
            data = self.ser.readline().decode('utf-8').rstrip('\r\n')
            if data == "ready":
                break

        self.ser.write(send_data.encode('ascii'))
        data_lst = []
        while True:
            try:
                data = self.ser.readline().decode('utf-8').rstrip('\r\n')
            except:
                pass
            if data == "ready":
                break
            else:
                data_lst.append(data)

        return data_lst[0]