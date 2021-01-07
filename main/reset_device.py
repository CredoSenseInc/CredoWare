from task_consumer import TaskConsumer, TaskTypes, Task
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from device_model_window import Ui_Device_Selector
import time
import serial.tools.list_ports
from utils import DEVICE_MANUFACTURER

#TODO: Improve coding peformance (make dynamic)
class Reset(QMainWindow, Ui_Device_Selector):
    def __init__(self, parent=None):
        super(Reset, self).__init__(parent)
        # QApplication.setOverrideCursor(Qt.WaitCursor)
        self.setupUi(self)
        self.setWindowTitle("Factory Reset")
        self.comboBox.show()
        self.resetButton.clicked.connect(self.proceed_to_reset)
        self.progressBar.hide()
        self.nn = 0
        self.count_task = 0
        self.max_task = 0

        self.add_start = '65536'
        self.add_stop = '524279'

        self.add_device_name = '5000'
        self.add_device_name_length = '6000'

        self.add_logging_interval_value = '8200'
        self.add_logging_start_stat = '12300'
        self.add_logging_stop_stat = '12400'

        self.add_alarm_stat = '16600'
        self.add_alarm_high_value = '16400'
        self.add_alarm_low_value = '16500'

        self.add_device_ID = '20500'
        self.add_device_ID_length = '20600'

        self.add_data_points = '20700'
        self.add_data_length = '20800'

        self.add_constA = '21000'
        self.add_constB = '22000'
        self.add_constC = '23000'
        self.add_resistor_value = '24000'

        self.add_last_written_location = '25000'

        self.add_daylight_stat = '32000'

    def initialize_and_show(self):
        self.show()
        # QApplication.restoreOverrideCursor()
    def show_end(self):
        self.bottom_label.setText("Almost done, Please wait")
        for i in range(0,101):
            self.progressBar.setValue(i)
            time.sleep(.1)
        self.resetButton.setText("Done")
        self.bottom_label.setText("Close this window and restart CredoWare")

    def show_error_dialog(self, msg):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(msg)
        msg_box.setWindowTitle("ERROR")
        msg_box.setStandardButtons(QMessageBox.Ok)
        TaskConsumer().clear_task_queue()
        self.closeEvent()
        msg_box.exec_()

    def task_done_callback(self, response):
        self.count_task += 1
        print(self.count_task)
        self.progressBar.setValue(self.count_task * (100/self.max_task))
        if (self.count_task==self.max_task):
            self.show_end()


        print(f"task response : {response}")

        if response['task_type'] == TaskTypes.SERIAL_ERASE_CHIP:
            if response['data'] == 'done':
                print("erased")
                # self.progressBar.setValue(20)
            else:
                print("error erasing chip")
                self.show_error_dialog("Could not complete reset")

        if response['task_type'] == TaskTypes.SERIAL_WRITE_STRING:
            if response['data'] == 'OK':
                # self.progressBar.setValue(30)
                pass
            else:
                self.show_error_dialog("Could not complete reset")

        if response['task_type'] == TaskTypes.SERIAL_WRITE_LONG:
            if response['data'] == 'OK':
                # self.progressBar.setValue(40)
                pass
            else:
                self.show_error_dialog("Could not complete reset")
        if response['task_type'] == TaskTypes.SERIAL_RENAME_DEV_NAME:
            if response['data'] == 'OK':
                # self.progressBar.setValue(60)
                pass
            else:
                self.show_error_dialog("Could not complete reset")
        if response['task_type'] == TaskTypes.SERIAL_WRITE_LOG:
            if response['data'] == 'OK':
                # self.progressBar.setValue(70)
                pass
            else:
                self.show_error_dialog("Could not complete reset")
        if response['task_type'] == TaskTypes.SERIAL_WRITE_LOG_START_STOP:
            if response['data'] == 'OK':
                # self.progressBar.setValue(80)
                pass
            else:
                self.show_error_dialog("Could not complete reset")
        if response['task_type'] == TaskTypes.SERIAL_WRITE_DAYLIGHT:
            if response['data'] == 'OK':
                # self.progressBar.setValue(90)
                pass
            else:
                self.show_error_dialog("Could not complete reset")

        if response['task_type'] == TaskTypes.SERIAL_WRITE_FLOAT:
            if response['data'] == 'OK':
                self.n = self.n + 1
                if (self.n < 4):
                    print(self.write_constant(self.n))
            else:
                self.show_error_dialog("Could not complete reset")

        if response['task_type'] == TaskTypes.SERIAL_WRITE_ALARM:
            if response['data'] == 'OK':
                # self.progressBar.setValue(100)
                pass
            else:
                self.show_error_dialog("Could not complete reset")

        if response['task_type'] == TaskTypes.SERIAL_WRITE_BYTE:
            if response['data'] == 'OK':
                self.nn = self.nn +1
                if (self.nn < 3):
                    self.write_data_points_length(self.data_points, self.data_length, self.nn)
            else:
                self.show_error_dialog("Could not complete reset")


    def write_ID(self, dev_id=""):
        dev_id_write = self.add_device_ID + " " + dev_id
        TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_STRING, self.task_done_callback, dev_id_write))
        dev_id_length = self.add_device_ID_length + " " + str(len(dev_id))
        TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_BYTE, self.task_done_callback, dev_id_length))

    def write_last_written_loaction(self):
        loc_write = self.add_last_written_location + " " + self.add_start
        TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_LONG, self.task_done_callback, loc_write))

    def write_constant(self, n):

        c1 = self.add_constA + ' ' + '0.001126034650'
        c2 = self.add_constB + ' ' + '0.000234592633'
        c3 = self.add_constC + ' ' + '0.000000086143'
        r = self.add_resistor_value + ' ' + '24000'

        if n == 0:
            TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_FLOAT, self.task_done_callback, c1))
            return c1
        if n == 1:
            TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_FLOAT, self.task_done_callback, c2))
            return c2
        if n == 2:
            TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_FLOAT, self.task_done_callback, c3))
            return c3
        if n == 3:
            TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_INT, self.task_done_callback, r))
            return r

        # TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_INT, self.task_done_callback, r))
        # TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_FLOAT, self.task_done_callback, c2))
        # TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_FLOAT, self.task_done_callback, c3))


    def erase_chip(self):
        TaskConsumer().insert_task(Task(TaskTypes.SERIAL_ERASE_CHIP, self.task_done_callback))
        # import data_reader
        # dr = data_reader.DataReader()
        # dr.write('erase_chip')

    def write_data_points_length(self, points, length, nn):
        write_points = self.add_data_points + ' ' + points

        if nn==1:
            TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_BYTE, self.task_done_callback, write_points))

        write_length = self.add_data_length + ' ' + length

        if nn==2:
            TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_BYTE, self.task_done_callback, write_length))

    def proceed_to_reset(self):
        self.resetButton.setDisabled(True)
        self.progressBar.show()
        self.comboBox.setDisabled(True)
        self.resetButton.setText("Resetting. Do not close this window")

        self.erase_chip()

        self.write_ID(self.comboBox.currentText())

        if self.comboBox.currentText() == 'CSL-T0.5':
            self.max_task = 15
            self.n = 0
            self.write_constant(self.n)
            self.data_points = '1'
            self.data_length = '2'

        elif self.comboBox.currentText() == 'CSL-H2 T0.2':
            self.max_task = 11
            self.data_points = '2'
            self.data_length = '4'


        self.write_data_points_length(self.data_points, self.data_length, self.nn)

        self.write_last_written_loaction()

        TaskConsumer().insert_task(Task(TaskTypes.SERIAL_RENAME_DEV_NAME, self.task_done_callback, 'CSL_Series_Logger'))
        TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_LOG, self.task_done_callback, '30'))
        TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_LOG_START_STOP, self.task_done_callback,
                                        '0 0:0:1 1/1/20 0 0:0:1 2/2/20'))
        TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_DAYLIGHT, self.task_done_callback, '0'))
        TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_ALARM, self.task_done_callback, '1 50 -20 80 30 1100 '
                                                                                               '800'))

#         # self.progressBar.setValue(100)
        # self.resetButton.setText("Done")

    def getportlist(self):
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        return ports

    def findreader(self, ports):
        self.commport = 'None'
        for i in range(0, len(ports)):
            if ports[i].manufacturer == 'FTDI':
                self.commport = ports[i].device
                break
        return self.commport

    def closeEvent(self, event):
        TaskConsumer().clear_task_queue()
        event.accept()