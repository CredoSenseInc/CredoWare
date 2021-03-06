import math
import os
import datetime
import time

from PyQt5 import  QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog

import utils
from data_reader import DataReader
from real_time_window import Ui_RealTimeWindow
from PyQt5 import QtWidgets

from task_consumer import TaskConsumer, Task, TaskTypes


class MyRealTimeWindow(QMainWindow, Ui_RealTimeWindow):

    def __init__(self, parent=None):
        super(MyRealTimeWindow, self).__init__(parent)

        self.setupUi(self)

        self.btn_reading_start.clicked.connect(self.start_pressed)
        self.btn_reading_stop.clicked.connect(self.stop_pressed)

        self.btn_reading_stop.setDisabled(True)
        self.reading_timer = QTimer()
        self.reading_timer.setInterval(2000)
        self.spinBox.setValue(2)
        self.timedate_data = []
        self.temperature_data = []
        self.humidity_data = []
        self.pressure_data = []

        self.write_yes = False
        self.savingText.hide()
        self.savingText.setStyleSheet('color:red;')
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMaximizeButtonHint)

        self.chk_dev_id = ""

        self.temp_lcd.display('-')
        self.hum_lcd.display('-')
        self.pre_lcd.display('-')

    def initialize_and_show(self):
        self.show()

    def start_pressed(self):
        self.temp_lcd.display('-')
        self.hum_lcd.display('-')
        self.pre_lcd.display('-')

        x = DataReader()
        self.chk_dev_id = x.read_data("read_dev_ID")

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("Do you want to save incoming real-time data?")
        msg_box.setWindowTitle("Message")

        save = msg_box.addButton('Yes', QMessageBox.YesRole)

        dont_save = msg_box.addButton('No', QMessageBox.NoRole)
        msg_box.exec_()

        if msg_box.clickedButton() == save:
            self.write_yes = True
            self.savingText.show()
            # self.choose_directory()
        elif msg_box.clickedButton() == dont_save:
            pass

        self.btn_reading_start.setDisabled(True)
        self.btn_reading_stop.setDisabled(False)

        self.reading_timer.setInterval(self.spinBox.value()*1000)
        self.spinBox.setDisabled(True)
        self.init_queue_real_time_thread()

    def stop_pressed(self):
        TaskConsumer().clear_task_queue()

        self.stop_queue_real_time_thread()
        self.btn_reading_start.setDisabled(False)
        self.btn_reading_stop.setDisabled(True)
        self.spinBox.setDisabled(False)
        self.show_msg("Reading Stopped\n")
        if self.write_yes:
            self.savingText.hide()
            self.choose_directory()
            self.write_csv()
            self.write_yes = False

    def init_queue_real_time_thread(self):

        self.reading_timer.start()
        self.reading_timer.timeout.connect(self.get_real_time_reading)

    def stop_queue_real_time_thread(self):
        self.reading_timer.stop()

    def get_real_time_reading(self):
        self.start = time.time()
        TaskConsumer().insert_task(Task(TaskTypes.SERIAL_REAL_TIME, self.task_done_callback))

    def clear_temporary(self):
        self.temperature_data.clear()
        self.humidity_data.clear()
        self.timedate_data.clear()
        self.pressure_data.clear()

    def task_done_callback(self, response):
        self.stop = time.time()
        print(f'time taken: {self.stop - self.start}')
        if 'exception' in response:
            print('error')
            return
        print(response)
        MyRealTimeWindow.temp = response['data']
        temp = MyRealTimeWindow.temp
        # print(temp)


        try:
            if self.chk_dev_id == 'CSL-T0.5':
                # tmp = self.apply_rules_to_values(float(temp))
                # temp = ((temp*(9/5))+32)  # convert to fahrenheit
                # print(tmp)
                tmp = float(temp)
                self.temp_lcd.display(tmp)
                self.timedate_data.append(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S"))
                self.temperature_data.append(tmp)

            if self.chk_dev_id == 'CSL-H2 T0.2':

                tmp, hum = temp.split()
                # print(tmp)
                # print(hum)
                if float(hum) == 100.00:
                    print('read again')
                    self.get_real_time_reading()
                else:
                    self.temp_lcd.display(tmp)
                    self.hum_lcd.display(hum)
                    self.timedate_data.append(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S"))
                    self.temperature_data.append(tmp)
                    self.humidity_data.append(hum)

            if self.chk_dev_id == 'CSL-H2 P1 T0.2':

                tmp, hum, pre = temp.split()
                # print(tmp)
                # print(hum)
                if float(hum) == 100.00:
                    print('read again')
                    self.get_real_time_reading()
                self.temp_lcd.display(tmp)
                self.hum_lcd.display(hum)
                self.pre_lcd.display(pre)
                self.timedate_data.append(datetime.datetime.now().strftime("%d %B %Y %H:%M:%S"))
                self.temperature_data.append(tmp)
                self.humidity_data.append(hum)
                self.pressure_data.append(pre)

        except Exception as er:
            print(er)
            pass

    def apply_rules_to_values(self, vals):
        c1, c2, c3, r = utils.READ_CONST_RESPONSE.split(' ')
        c1 = c1.split('=')[1]
        c2 = c2.split('=')[1]
        c3 = c3.split('=')[1]
        r = r.split('=')[1]
        c1 = float(c1)
        c2 = float(c2)
        c3 = float(c3)
        r = float(r)
        # for each in vals:
        temp = math.log(r * ((1023.0 / vals) - 1))
        val = 1 / (c1 + (c2 + (c3 * temp * temp)) * temp)
        val = val - 273.15

        return val

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Window Close', 'Exit real time data steaming ?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.temp_lcd.display('-')
            self.hum_lcd.display('-')
            self.pre_lcd.display('-')
            if self.write_yes:
                self.choose_directory()
                self.write_csv()
                self.write_yes = False
            self.stop_queue_real_time_thread()
            TaskConsumer().clear_task_queue()
            self.btn_reading_stop.setDisabled(True)
            self.btn_reading_start.setDisabled(False)
            self.spinBox.setDisabled(False)
            self.savingText.hide()
            self.clear_temporary()
            event.accept()
        else:
            event.ignore()

    def show_msg(self, msg):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(msg)
        msg_box.setWindowTitle("Message")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def choose_directory(self):
        self.save_file_name = QFileDialog.getSaveFileName(self, directory='Streaming_data.csv', caption='Save File As', filter='*.csv',
                                                          initialFilter='*.csv')
        print(self.save_file_name)
        # self.write_yes = True

    def write_csv(self):
        import csv
        print(self.save_file_name)
        try:
            with open(self.save_file_name[0], 'w+', newline='') as file:
                writer = csv.writer(file)

                if self.chk_dev_id == 'CSL-H2 T0.2':
                    writer.writerow(["Index", "Date-time", "Temperature (C)", "Relative Humidity (%)"])
                    i = 0
                    for x, y, z in zip(self.timedate_data, self.temperature_data, self.humidity_data):
                        i += 1
                        writer.writerow([i, x, y, z])

                if self.chk_dev_id == 'CSL-T0.5':
                    writer.writerow(["Index", "Date-time", "Temperature (C)"])
                    i = 0
                    for x, y in zip(self.timedate_data, self.temperature_data):
                        i += 1
                        writer.writerow([i, x, y])

                if self.chk_dev_id == 'CSL-H2 P1 T0.2':
                    writer.writerow(["Index", "Date-time", "Temperature (C)", "Relative Humidity (%)", "Barometric Pressure (mbar)"])
                    i = 0
                    for x, y, z, k in zip(self.timedate_data, self.temperature_data, self.humidity_data, self.pressure_data):
                        i += 1
                        writer.writerow([i, x, y, z, k])

            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText("Data saved"+"\nFile: " + self.save_file_name[0])
            msg_box.setWindowTitle("Done")
            self.clear_temporary()
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
        except:
            self.clear_temporary()
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText("Data saving aborted")
            msg_box.setWindowTitle("Error")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            self.write_yes = False
            pass