import datetime
import logging
import math
import os

import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

import utils
from data_reader import DataReader
from graph_window import Ui_ReadLoggerDataWindow

logger = logging.getLogger(__name__)


class LoggerPlotWindow(QMainWindow, Ui_ReadLoggerDataWindow):

    def __init__(self, *args, **kwargs):
        super(LoggerPlotWindow, self).__init__(*args, **kwargs)

        self.setupUi(self)
        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))
        # self.comboBox_temp_unit.setCurrentIndex(1)
        self.comboBox_temp_unit.currentIndexChanged.connect(self.onCurrentIndexChanged)
        self.setWindowTitle("Graph Window")
        self.btn_generate_report.clicked.connect(self.generate_report)
        self.btn_save_csv_data.clicked.connect(self.save_data)
        self.temp_unit_now = 'C'

    def initialize_and_show(self, interval, data):
        self.start_dt = ''
        self.end_dt = ''
        self.interval = interval
        self.data = data

        if self.data != []:
            self.populate_graph()
            self.setWindowTitle("Loggeed Data")
            self.show()

        if self.iserror == '1' and self.data != []:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText("Memory error found in logger\nErase logger data before starting new session")
            msg_box.setWindowTitle("Warning")
            msg_box.exec_()

    def generate_report(self):
        # msg_box = QMessageBox(self)
        # msg_box.setIcon(QMessageBox.Information)
        # msg_box.setText("Choose a report format: \nPDF will generate a summary report.\nCSV will save the raw data in CSV format.")
        # msg_box.setWindowTitle("Message")
        # pdftBtn = msg_box.addButton('PDF', QMessageBox.ActionRole)
        # csvBtn = msg_box.addButton('CSV', QMessageBox.ActionRole)
        # msg_box.addButton('Cancel', QMessageBox.RejectRole)
        # msg_box.exec_()
        # if msg_box.clickedButton() == pdftBtn:
        self.choose_directory('pdf')
        # elif msg_box.clickedButton() == csvBtn:
        # self.choose_directory('csv')

    def save_data(self):
        self.choose_directory('csv')

    def choose_directory(self, file_ext):
        qfd = QFileDialog(self)
        options = qfd.Options()
        options |= qfd.DontUseNativeDialog
        file_dir = qfd.getExistingDirectory(self, "Choose a folder", "", qfd.ShowDirsOnly)
        # file_dir = qfd.getSaveFileName()
        # print(file_dir)
        if file_dir:
            # print(file_dir)
            self.write_data_to_file(file_ext, file_dir)

    def write_data_to_file(self, file_ext, file_dir):

        file_name_dt = []
        start_rt = self.start_dt.replace('/', '-')
        start_rt = start_rt.replace(':', '-')
        start_rt = start_rt.__add__("_to")
        end_rt = self.end_dt.replace('/', '-')
        end_rt = end_rt.replace(':', '-')
        file_name_dt.extend(start_rt.split(" "))
        file_name_dt.extend(end_rt.split(" "))
        file_name = '_'.join(file_name_dt)

        file_name = file_name + "_" + self.temp_unit_now + "." + file_ext

        full_file_path = os.path.join(file_dir, file_name)

        if file_ext == 'pdf':
            # print('pdf')
            x = DataReader()
            self.dev_name = x.read_data('read_dev_name')
            alrm_str = x.read_data('read_alarm')
            alarm_status, high_temp_value, low_temp_value, high_hum_value, low_hum_value, high_pre_value, low_pre_value = alrm_str.split(
                ' ')
            print(alarm_status)
            combo_index = self.comboBox_temp_unit.currentIndex()

            if combo_index == 1:
                float_high_temp_value = self.celsius_to_kelvin(float(high_temp_value))
                high_temp_value = str(float_high_temp_value)
                float_low_temp_value = self.celsius_to_kelvin(float(low_temp_value))
                low_temp_value = str(float_low_temp_value)

            if combo_index == 2:
                float_high_temp_value = self.celsius_to_fahrenheit(float(high_temp_value))
                high_temp_value = str(float_high_temp_value)
                float_low_temp_value = self.celsius_to_fahrenheit(float(low_temp_value))
                low_temp_value = str(float_low_temp_value)

            file_name = self.chk_dev_id + '_' + self.dev_name + "_summary_report_" + self.temp_unit_now + ".pdf"
            file_name = file_name.replace(' ', '_')
            full_file_path = os.path.join(file_dir, file_name)

            import pandas

            float_temperature_data = []
            float_humidity_data = []
            float_pressure_data = []
            alarm_data = []

            float_temperature_data.clear()
            float_humidity_data.clear()
            float_pressure_data.clear()
            alarm_data.clear()

            if self.chk_dev_id == 'CSL-H2 P1 T0.2':
                for i in range(0, len(self.temperature_data)):
                    float_temperature_data.insert(i, float(self.temperature_data[i]))
                    float_humidity_data.insert(i, float(self.humidity_data[i]))
                    float_pressure_data.insert(i, float(self.pressure_data[i]))

                    if ((float_humidity_data[i] >= float(high_hum_value))
                        or (float_humidity_data[i] <= float(low_hum_value))
                        or (float_temperature_data[i] >= float(high_temp_value))
                        or (float_temperature_data[i] <= float(low_temp_value))
                        or (float_pressure_data[i] >= float(high_pre_value))
                        or (float_pressure_data[i] <= float(low_pre_value))) \
                            and float(alarm_status == 1):
                        alarm_data.insert(i, 1)
                    else:
                        alarm_data.insert(i, 0)
                pdf_data = pandas.DataFrame({"DateTime": self.timedate_data, 'Temperature': float_temperature_data,
                                             'Relative Humidity': float_humidity_data,
                                             "Barometric Pressure": float_pressure_data, 'Alarm': alarm_data})

            if self.chk_dev_id == 'CSL-H2 T0.2':
                for i in range(0, len(self.temperature_data)):
                    float_temperature_data.insert(i, float(self.temperature_data[i]))
                    float_humidity_data.insert(i, float(self.humidity_data[i]))

                    if ((float_humidity_data[i] >= float(high_hum_value))
                            or (float_humidity_data[i] <= float(low_hum_value))
                            or (float_temperature_data[i] >= float(high_temp_value))
                            or (float_temperature_data[i] <= float(low_temp_value))) \
                            and float(alarm_status == 1):
                        alarm_data.insert(i, 1)
                    else:
                        alarm_data.insert(i, 0)
                pdf_data = pandas.DataFrame({"DateTime": self.timedate_data, 'Temperature': float_temperature_data,
                                             'Relative Humidity': float_humidity_data, 'Alarm': alarm_data})

            if self.chk_dev_id == 'CSL-T0.5':
                for i in range(0, len(self.temperature_data)):
                    float_temperature_data.insert(i, float(self.temperature_data[i]))
                    if ((float_temperature_data[i] >= float(high_temp_value)) or (float_temperature_data[i] <= float(
                            low_temp_value))) and float(alarm_status == 1):
                        alarm_data.insert(i, 1)
                    else:
                        alarm_data.insert(i, 0)

                pdf_data = pandas.DataFrame({"DateTime": self.timedate_data, 'Temperature': float_temperature_data,
                                             'Alarm': alarm_data})

            try:
                import pdf_report_reportlab as report
                report.generateReport(pdf_data, filepath=full_file_path, dev_name=self.dev_name,
                                      dev_model=self.chk_dev_id,
                                      t_alarm_lo=float(low_temp_value), t_alarm_hi=float(high_temp_value),
                                      rh_alarm_lo=float(low_hum_value), rh_alarm_hi=float(high_hum_value),
                                      bmp_alarm_lo=float(low_pre_value), bmp_alarm_hi=float(high_pre_value))

                self.file_write_done_message("Report generation successful\nFile name: " + file_name)
            except Exception as er:
                print(er)
                self.file_write_error_message("Error generating report")
                pass

        elif file_ext == 'csv':
            import csv
            try:
                with open(full_file_path, 'w+', newline='') as file:
                    writer = csv.writer(file)

                    # try:
                    #     print(self.flag_finder(value_list=self.temperature_data, max_deviation=0.01))
                    # except Exception as er:
                    #     print(er)

                    if self.chk_dev_id == 'CSL-H2 P1 T0.2':
                        writer.writerow(["Index", "Date-Time", "Temp", "RH", "BMP"])
                        i = 0
                        for x, y, z, k in zip(self.timedate_data, self.temperature_data, self.humidity_data,
                                              self.pressure_data):
                            i += 1
                            writer.writerow([i, x, y, z, k])

                    if self.chk_dev_id == 'CSL-H2 T0.2':
                        writer.writerow(["Index", "Date-Time", "Temp", "RH"])

                        try:
                            # temp_flags = self.flag_finder(value_list=self.temperature_data, max_deviation=1)
                            # hum_flags = self.flag_finder(value_list=self.humidity_data, max_deviation=1)
                            # print(temp_flags)
                            # print(hum_flags)
                            # flags = []
                            # for i in range(0, len(temp_flags)):
                            #     if temp_flags[i] == 1 or hum_flags[i] == 1:
                            #         flags.insert(i, 1)
                            #     else:
                            #         flags.insert(i, 0)

                            i = 0
                            for x, y, z in zip(self.timedate_data, self.temperature_data, self.humidity_data):
                                i += 1
                                writer.writerow([i, x, y, z])
                        except Exception as er:
                            print(er)
                            pass

                    if self.chk_dev_id == 'CSL-T0.5':
                        writer.writerow(["Index", "Date-Time", "Temp"])

                        try:
                            #     temp_flags = self.flag_finder(value_list=self.temperature_data, max_deviation=1)
                            #
                            #     flags = []
                            #     for i in range(0, len(temp_flags)):
                            #         if temp_flags[i] == 1:
                            #             flags.insert(i, 1)
                            #         else:
                            #             flags.insert(i, 0)

                            i = 0
                            for x, y in zip(self.timedate_data, self.temperature_data):
                                i += 1
                                writer.writerow([i, x, y])
                        except Exception as er:
                            print(er)
                            pass

                self.file_write_done_message("Saving data successful\nFile name: " + file_name)
            except Exception as er:
                print(er)
                self.file_write_error_message("Error saving data")
                pass

    def flag_finder(self, value_list, max_deviation):

        flag_list = []
        for i in range(0, len(value_list) - 1):
            try:
                if abs(float(value_list[i + 1]) - float(value_list[i])) > max_deviation or math.isnan(
                        float(value_list[i])):
                    flag_list.insert(i, 1)
                else:
                    flag_list.insert(i, 0)
            except:
                print('exception')
                flag_list.insert(i, 0)

    """
        The part below is for z score evaluation for data flagging
    """

    # def flag_finder2(value_list):
    #     # mean_of_all_data =
    #     flag_list = []
    #
    #     # if NaN is
    #     mean_of_all = numpy.mean(value_list)
    #     sd_of_all = numpy.std(value_list)
    #
    #     print(mean_of_all)
    #     print(sd_of_all)
    #
    #     for i in range(0, len(value_list)):
    #
    #         print('\n......')
    #         print(i)
    #
    #         print(value_list[i])
    #         z_score = (value_list[i] - mean_of_all) / sd_of_all
    #         print(f'z score is : {z_score}')
    #         try:
    #             if z_score > 1.5:
    #                 flag_list.insert(i, 1)
    #             else:
    #                 flag_list.insert(i, 0)
    #                 print('ignored')
    #         except:
    #             flag_list.insert(i, 0)
    #             print('ignored by default')
    #
    #     return flag_list

    def onCurrentIndexChanged(self, ix):
        try:
            self.MplWidget.canvas.axes.cla()

            combo_index = self.comboBox_temp_unit.currentIndex()

            if combo_index == 1:
                if self.temp_unit_now == 'C':
                    for i in range(0, len(self.temperature_data)):
                        self.temperature_data[i] = self.celsius_to_kelvin(float(self.temperature_data[i]))

                if self.temp_unit_now == 'F':
                    for i in range(0, len(self.temperature_data)):
                        self.temperature_data[i] = self.fahrenheit_to_kelvin(float(self.temperature_data[i]))

                self.temp_unit_now = 'K'

            if combo_index == 2:
                if self.temp_unit_now == 'C':
                    for i in range(0, len(self.temperature_data)):
                        self.temperature_data[i] = self.celsius_to_fahrenheit(float(self.temperature_data[i]))
                if self.temp_unit_now == 'K':
                    for i in range(0, len(self.temperature_data)):
                        self.temperature_data[i] = self.kelvin_to_fahrenheit(float(self.temperature_data[i]))

                self.temp_unit_now = 'F'

            if combo_index == 0:
                if self.temp_unit_now == 'F':
                    for i in range(0, len(self.temperature_data)):
                        self.temperature_data[i] = self.fahrenheit_to_celsius(float(self.temperature_data[i]))
                if self.temp_unit_now == 'K':
                    for i in range(0, len(self.temperature_data)):
                        self.temperature_data[i] = self.kelvin_to_celsius(float(self.temperature_data[i]))

                self.temp_unit_now = 'C'

            if self.chk_dev_id == 'CSL-H2 P1 T0.2':

                self.MplWidget.canvas.axes = self.MplWidget.canvas.figure.add_subplot(131)

                self.float_temp_data = []

                for i in range(0, len(self.temperature_data)):
                    self.float_temp_data.append(float(self.temperature_data[i]))

                self.MplWidget.canvas.axes.plot(self.timedate_data, self.float_temp_data, linestyle='solid',
                                                label='_nolegend_', color='r', marker='.')
                self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.AutoDateLocator())
                self.MplWidget.canvas.axes.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
                self.MplWidget.canvas.axes.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y %H:%M'))
                self.MplWidget.canvas.axes.set_xlabel('Date-Time', fontweight='bold')
                self.MplWidget.canvas.axes.set_ylabel('Temperature', fontweight='bold')
                self.MplWidget.canvas.figure.autofmt_xdate()
                # self.MplWidget.canvas.axes.legend()

            if self.chk_dev_id == 'CSL-H2 T0.2':

                self.MplWidget.canvas.axes = self.MplWidget.canvas.figure.add_subplot(121)

                self.float_temp_data = []

                for i in range(0, len(self.temperature_data)):
                    self.float_temp_data.append(float(self.temperature_data[i]))

                self.MplWidget.canvas.axes.plot(self.timedate_data, self.float_temp_data, linestyle='solid',
                                                label='_nolegend_', color='r', marker='.')
                self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.AutoDateLocator())
                self.MplWidget.canvas.axes.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
                self.MplWidget.canvas.axes.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y %H:%M'))
                self.MplWidget.canvas.axes.set_xlabel('Date-Time', fontweight='bold')
                self.MplWidget.canvas.axes.set_ylabel('Temperature', fontweight='bold')
                self.MplWidget.canvas.figure.autofmt_xdate()
                # self.MplWidget.canvas.axes.legend()

            if self.chk_dev_id == 'CSL-T0.5':
                self.comboBox_temp_unit.show()
                self.label.show()
                self.MplWidget.canvas.axes = self.MplWidget.canvas.figure.add_subplot(111)
                self.MplWidget.canvas.axes.set_xlabel('Date-Time', fontweight='bold')
                self.MplWidget.canvas.axes.set_ylabel('Temperature', fontweight='bold')
                self.MplWidget.canvas.axes.plot(self.timedate_data, self.temperature_data, linestyle='solid',
                                                label='Temperature', color='r', marker='.')
                self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.AutoDateLocator())
                self.MplWidget.canvas.axes.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
                self.MplWidget.canvas.axes.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y %H:%M'))
                self.MplWidget.canvas.figure.autofmt_xdate()

            self.MplWidget.canvas.draw()

        except:
            self.file_write_error_message("Cannot change temperature unit")
            self.comboBox_temp_unit.hide()
            pass

    def populate_graph(self):
        x = DataReader()
        self.chk_dev_id = x.read_data("read_dev_ID")
        row = x.read_data("read_row")
        self.iserror = x.read_data("read_error")
        # print("row is" + row)
        self.temperature_data = []
        self.humidity_data = []
        self.pressure_data = []
        self.timedate_data = []

        if self.data != []:
            t, d, n, l = self.data[0].split()
            # print("time is :" + t)
            # print("date is :" + d)
            current_key = f"{t} {d}"

            # print("incoming data :" + n)
            # print("interval for this :" + l)

            tstart = datetime.datetime.strptime(current_key, "%H:%M:%S %d/%m/%Y")
            # print(tstart.strftime("%H:%M:%S %d %B %Y"))
            self.start_dt = tstart.strftime("%d %B %Y at %H:%M")
            tint = datetime.timedelta(minutes=float(l) * (float(n) - 1))
            tend = tstart + tint
            # print(tend.strftime("%H:%M:%S %d/%m/%Y"))
            self.end_dt = tend.strftime("%d %B %Y at %H:%M")

            c = 1
            for i in range(1, len(self.data)):
                if c <= int(n):
                    # print(tstart + datetime.timedelta(minutes=(float(l) * (c - 1))))
                    self.timedate_data.append(tstart + datetime.timedelta(minutes=(float(l) * (c - 1))))
                    # print("number :" + str(c) + " data " + self.data[i])
                    if row == '1':
                        # print("row is 1")
                        self.temperature_data.append(self.data[i])
                    if row == '2':
                        # print("row is 2")
                        tmp, hum = self.data[i].split()
                        self.temperature_data.append(tmp)
                        self.humidity_data.append(hum)
                    if row == '3':
                        # print("row is 3")
                        tmp, hum, pre = self.data[i].split()
                        self.temperature_data.append(tmp)
                        self.humidity_data.append(hum)
                        self.pressure_data.append(pre)
                    c = c + 1
                else:
                    c = 1
                    t, d, n, l = self.data[i].split()
                    # print("time is :" + t)
                    # print("date is :" + d)
                    current_key = f"{t} {d}"
                    # print("incoming data :" + n)
                    # print("interval for this :" + l)

                    tstart = datetime.datetime.strptime(current_key, "%H:%M:%S %d/%m/%Y")
                    # print(tstart.strftime("%H:%M:%S %d %B %Y"))
                    # self.start_dt = tstart.strftime("%H:%M:%S %d %B %Y")
                    tint = datetime.timedelta(minutes=float(l) * (float(n) - 1))
                    tend = tstart + tint
                    # print(tend.strftime("%H:%M:%S %d/%m/%Y"))
                    self.end_dt = tend.strftime("%d %B %Y at %H:%M")

            self.graph_start_dt.setText(f" {self.start_dt}")
            self.graph_end_dt.setText(f" {self.end_dt}")

            if self.chk_dev_id == 'CSL-H2 P1 T0.2':

                self.comboBox_temp_unit.show()
                self.label.show()
                self.MplWidget.canvas.axes = self.MplWidget.canvas.figure.add_subplot(131)
                self.MplWidget.canvas.axes2 = self.MplWidget.canvas.figure.add_subplot(132)
                self.MplWidget.canvas.axes3 = self.MplWidget.canvas.figure.add_subplot(133)

                logger.info(self.timedate_data)

                self.float_temp_data = []
                self.float_hum_data = []
                self.float_pre_data = []

                self.modified_timedate_data = []

                for i in range(0, len(self.temperature_data)):

                    if self.temp_unit_now == 'C':
                        if not (float(self.temperature_data[i]) >= 85 or
                                float(self.temperature_data[i]) <= -40 or
                                math.isnan(float(self.temperature_data[i]))):
                            if not (math.isnan(float(self.humidity_data[i])) or float(
                                    self.humidity_data[i]) > 100 or float(self.humidity_data[i]) < 0):
                                if not (math.isnan(float(self.pressure_data[i])) or float(
                                        self.pressure_data[i]) > 1200 or float(self.pressure_data[i]) < 600):
                                    self.float_temp_data.append(float(self.temperature_data[i]))
                                    self.modified_timedate_data.append((self.timedate_data[i]))
                                    self.float_hum_data.append(float(self.humidity_data[i]))
                                    self.float_pre_data.append(float(self.pressure_data[i]))
                    elif self.temp_unit_now == 'F':

                        if not (float(self.temperature_data[i]) >= 185 or
                                float(self.temperature_data[i]) <= -40 or
                                math.isnan(float(self.temperature_data[i]))):
                            if not (math.isnan(float(self.humidity_data[i])) or float(
                                    self.humidity_data[i]) > 100 or float(self.humidity_data[i]) < 0):
                                if not (math.isnan(float(self.pressure_data[i])) or float(
                                        self.pressure_data[i]) > 1200 or float(self.pressure_data[i]) < 600):
                                    self.float_temp_data.append(float(self.temperature_data[i]))
                                    self.modified_timedate_data.append((self.timedate_data[i]))
                                    self.float_hum_data.append(float(self.humidity_data[i]))
                                    self.float_pre_data.append(float(self.pressure_data[i]))

                    elif self.temp_unit_now == 'K':

                        if not (float(self.temperature_data[i]) >= 358.15 or
                                float(self.temperature_data[i]) <= 233.15 or
                                math.isnan(float(self.temperature_data[i]))):
                            if not (math.isnan(float(self.humidity_data[i])) or float(
                                    self.humidity_data[i]) > 100 or float(self.humidity_data[i]) < 0):
                                if not (math.isnan(float(self.pressure_data[i])) or float(
                                        self.pressure_data[i]) > 1200 or float(self.pressure_data[i]) < 600):
                                    self.float_temp_data.append(float(self.temperature_data[i]))
                                    self.modified_timedate_data.append((self.timedate_data[i]))
                                    self.float_hum_data.append(float(self.humidity_data[i]))
                                    self.float_pre_data.append(float(self.pressure_data[i]))

                self.MplWidget.canvas.axes.plot(self.modified_timedate_data, self.float_temp_data, linestyle='solid',
                                                label='_nolegend_', color='r', marker='.')
                self.MplWidget.canvas.axes2.plot(self.modified_timedate_data, self.float_hum_data, linestyle='solid',
                                                 label='_nolegend_', color='b', marker='.')
                self.MplWidget.canvas.axes3.plot(self.modified_timedate_data, self.float_pre_data, linestyle='solid',
                                                 label='_nolegend_', color='g', marker='.')

                self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.AutoDateLocator())
                self.MplWidget.canvas.axes2.xaxis.set_major_locator(mdates.AutoDateLocator())
                self.MplWidget.canvas.axes3.xaxis.set_major_locator(mdates.AutoDateLocator())

                self.MplWidget.canvas.axes.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
                self.MplWidget.canvas.axes2.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
                self.MplWidget.canvas.axes3.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
                self.MplWidget.canvas.axes3.ticklabel_format(useOffset=False, axis='y')

                self.MplWidget.canvas.axes.xaxis.set_major_locator(ticker.MaxNLocator(nbins=6))
                self.MplWidget.canvas.axes2.xaxis.set_major_locator(ticker.MaxNLocator(nbins=6))
                self.MplWidget.canvas.axes3.xaxis.set_major_locator(ticker.MaxNLocator(nbins=6))

                self.MplWidget.canvas.axes.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y %H:%M'))
                self.MplWidget.canvas.axes2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y %H:%M'))
                self.MplWidget.canvas.axes3.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y %H:%M'))

                self.MplWidget.canvas.axes.set_xlabel('Date-Time', fontweight='bold')
                self.MplWidget.canvas.axes.set_ylabel('Temperature', fontweight='bold')

                self.MplWidget.canvas.axes2.set_xlabel('Date-Time', fontweight='bold')
                self.MplWidget.canvas.axes2.set_ylabel('Relative Humidity (%)', fontweight='bold')

                self.MplWidget.canvas.axes3.set_xlabel('Date-Time', fontweight='bold')
                self.MplWidget.canvas.axes3.set_ylabel('Barometric Pressure (mBar)', fontweight='bold')

                self.MplWidget.canvas.figure.autofmt_xdate()

                # self.MplWidget.canvas.axes.legend()
                # self.MplWidget.canvas.axes2.legend()

            if self.chk_dev_id == 'CSL-H2 T0.2':

                self.comboBox_temp_unit.show()
                self.label.show()
                self.MplWidget.canvas.axes = self.MplWidget.canvas.figure.add_subplot(121)
                self.MplWidget.canvas.axes2 = self.MplWidget.canvas.figure.add_subplot(122)
                logger.info(self.timedate_data)
                self.float_temp_data = []
                self.float_hum_data = []
                self.modified_timedate_data = []
                for i in range(0, len(self.temperature_data)):

                    if self.temp_unit_now == 'C':
                        if not (float(self.temperature_data[i]) >= 85 or
                                float(self.temperature_data[i]) <= -40 or
                                math.isnan(float(self.temperature_data[i]))):
                            if not (math.isnan(float(self.humidity_data[i])) or float(
                                    self.humidity_data[i]) > 100 or float(self.humidity_data[i]) < 0):
                                self.float_temp_data.append(float(self.temperature_data[i]))
                                self.modified_timedate_data.append((self.timedate_data[i]))
                                self.float_hum_data.append(float(self.humidity_data[i]))
                    elif self.temp_unit_now == 'F':

                        if not (float(self.temperature_data[i]) >= 185 or
                                float(self.temperature_data[i]) <= -40 or
                                math.isnan(float(self.temperature_data[i]))):
                            if not (math.isnan(float(self.humidity_data[i])) or float(
                                    self.humidity_data[i]) > 100 or float(self.humidity_data[i]) < 0):
                                self.float_temp_data.append(float(self.temperature_data[i]))
                                self.modified_timedate_data.append((self.timedate_data[i]))
                                self.float_hum_data.append(float(self.humidity_data[i]))

                    elif self.temp_unit_now == 'K':

                        if not (float(self.temperature_data[i]) >= 358.15 or
                                float(self.temperature_data[i]) <= 233.15 or
                                math.isnan(float(self.temperature_data[i]))):
                            if not (math.isnan(float(self.humidity_data[i])) or float(
                                    self.humidity_data[i]) > 100 or float(self.humidity_data[i]) < 0):
                                self.float_temp_data.append(float(self.temperature_data[i]))
                                self.modified_timedate_data.append((self.timedate_data[i]))
                                self.float_hum_data.append(float(self.humidity_data[i]))

                self.MplWidget.canvas.axes.plot(self.modified_timedate_data, self.float_temp_data, linestyle='solid',
                                                label='_nolegend_', color='r', marker='.')
                self.MplWidget.canvas.axes2.plot(self.modified_timedate_data, self.float_hum_data, linestyle='solid',
                                                 label='_nolegend_', color='b', marker='.')

                self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.AutoDateLocator())
                self.MplWidget.canvas.axes2.xaxis.set_major_locator(mdates.AutoDateLocator())
                self.MplWidget.canvas.axes.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
                self.MplWidget.canvas.axes2.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
                self.MplWidget.canvas.axes.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y %H:%M'))
                self.MplWidget.canvas.axes2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y %H:%M'))

                self.MplWidget.canvas.axes.set_xlabel('Date-Time', fontweight='bold')
                self.MplWidget.canvas.axes.set_ylabel('Temperature', fontweight='bold')
                self.MplWidget.canvas.axes2.set_xlabel('Date-Time', fontweight='bold')
                self.MplWidget.canvas.axes2.set_ylabel('Relative Humidity (%)', fontweight='bold')

                self.MplWidget.canvas.figure.autofmt_xdate()

                # self.MplWidget.canvas.axes.legend()
                # self.MplWidget.canvas.axes2.legend()

            if self.chk_dev_id == 'CSL-T0.5':

                self.comboBox_temp_unit.show()
                self.label.show()
                for i in range(0, len(self.temperature_data)):
                    self.temperature_data[i] = (self.apply_rules_to_values(float(self.temperature_data[i])))

                self.float_temp_data = []
                self.modified_timedate_data = []

                for i in range(0, len(self.temperature_data)):

                    if self.temp_unit_now == 'C':
                        if not (float(self.temperature_data[i]) >= 85 or
                                float(self.temperature_data[i]) <= -40 or
                                math.isnan(float(self.temperature_data[i]))):
                            self.float_temp_data.append(float(self.temperature_data[i]))
                            self.modified_timedate_data.append((self.timedate_data[i]))

                    elif self.temp_unit_now == 'F':
                        if not (float(self.temperature_data[i]) >= 185 or
                                float(self.temperature_data[i]) <= -40 or
                                math.isnan(float(self.temperature_data[i]))):
                            self.float_temp_data.append(float(self.temperature_data[i]))
                            self.modified_timedate_data.append((self.timedate_data[i]))

                    elif self.temp_unit_now == 'K':
                        if not (float(self.temperature_data[i]) >= 358.15 or
                                float(self.temperature_data[i]) <= 233.15 or
                                math.isnan(float(self.temperature_data[i]))):
                            self.float_temp_data.append(float(self.temperature_data[i]))
                            self.modified_timedate_data.append((self.timedate_data[i]))

                self.MplWidget.canvas.axes = self.MplWidget.canvas.figure.add_subplot(111)
                self.MplWidget.canvas.axes.set_xlabel('Date-Time', fontweight='bold')
                self.MplWidget.canvas.axes.set_ylabel('Temperature', fontweight='bold')
                self.MplWidget.canvas.axes.plot(self.modified_timedate_data, self.float_temp_data, linestyle='solid',
                                                label='_nolegend_', color='r', marker='.')

                self.MplWidget.canvas.axes.xaxis.set_major_locator(mdates.AutoDateLocator())
                self.MplWidget.canvas.axes.yaxis.set_major_locator(ticker.MaxNLocator(nbins=10))
                self.MplWidget.canvas.axes.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y %H:%M'))
                self.MplWidget.canvas.figure.autofmt_xdate()
        else:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText("Logger has no data")
            msg_box.setWindowTitle("Message")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()

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
        combo_index = self.comboBox_temp_unit.currentIndex()

        temp = math.log(r * ((1023.0 / vals) - 1))
        val = 1 / (c1 + (c2 + (c3 * temp * temp)) * temp)
        if combo_index == 0:
            val = self.kelvin_to_celsius(val)
        if combo_index == 2:
            val = self.kelvin_to_fahrenheit(val)

        return val

    def kelvin_to_celsius(self, kelvin):
        celsius = kelvin - 273.15
        return celsius

    def kelvin_to_fahrenheit(self, kelvin):
        fahrenheit = (kelvin - 273.15) * 9 / 5 + 32
        return fahrenheit

    def celsius_to_kelvin(self, celsius):
        kelvin = celsius + 273.15
        return kelvin

    def celsius_to_fahrenheit(self, celsius):
        fahrenheit = (celsius * 9 / 5) + 32
        return fahrenheit

    def fahrenheit_to_celsius(self, fahrenheit):
        celsius = (fahrenheit - 32) * (5 / 9)
        return celsius

    def fahrenheit_to_kelvin(self, fahrenheit):
        celsius = (fahrenheit - 32) * (5 / 9)
        kelvin = self.celsius_to_kelvin(celsius)
        return kelvin

    def convert_logarithm(self, val):
        val, e_val = val.split('e')
        val = float(val)
        e_val = float(e_val)
        res = val * (10 ** e_val)
        return res

    def file_write_done_message(self, msg):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(msg)
        msg_box.setWindowTitle("Done")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def file_write_error_message(self, msg):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(msg)
        msg_box.setWindowTitle("Error")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
