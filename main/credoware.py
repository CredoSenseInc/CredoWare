import datetime
import logging
import os, sys, subprocess

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QTimer, QDateTime, QDate, QTime, Qt
# import about_window
# from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import *
from main_window import Ui_MainWindow
# from sentry_sdk import capture_exception
import utils
from custom_dialog import ProgBar
from data_reader import DataReader
from logger_data_plot import LoggerPlotWindow
from realtime import MyRealTimeWindow
from about import MyAboutWindow
# from port_select import MyPortSelectWindow
from reset_device import Reset
from task_consumer import TaskConsumer, TaskTypes, Task
from utils import CONSCIOUS_BATTERY_LEVEL

# import sentry_sdk
import rollbar

rollbar.init('e3a546db962f43968a3956e2e201e320')

# sentry_sdk.init("https://e6fdc5ed07fb4248aaf35c1deca4ec8b@sentry.io/2500238")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
#     QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
# #
# if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
#     QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

def open_file(filename):
    try:
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])
    except:
        pass


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):

        super(MainWindow, self).__init__(*args, **kwargs)
        self.alert_msg_box = QMessageBox(self)
        self.setupUi(self)

        self.reading_timer = QTimer()

        self.device_selecton = Reset()
        self.real_time_window = MyRealTimeWindow()
        self.about_window = MyAboutWindow()

        """code segment for: port select window"""
        # self.port_select_window = MyPortSelectWindow()
        # self.port_select_window.initialize_and_show()
        # self.port_select_window.button_select_port.clicked.connect(self.initialize_main_window)

        self.logger_connected = None

        self.actionTurn_ON.triggered.connect(lambda: self.led_on())
        self.actionTrun_OFF.triggered.connect(lambda: self.led_off())

        self.checkBox_dst.setDisabled(True)

        self.connect_button.hide()

        self.actionAbout.triggered.connect(lambda: self.about_window.initialize_and_show())
        self.actionExit.triggered.connect(QApplication.closeAllWindows)

        self.actionCSL_Series_Logger_detail_guide.triggered.connect(lambda: open_file('csl_series_logger_manual.pdf'))
        self.actionCredoSense_website.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(
            'http://credosense.com')))
        # QAction.setDisabled(self.actionStart_reading_logged_data)
        # self.actionRemove_all_logged_data.setDisabled(True)
        # self.actionStart_real_time_data_streaming.setDisabled(True)
        # self.actionSync_logger_to_computer_time.triggered.setDisabled(True)

        self.comboBox_logging_start.currentIndexChanged.connect(self.logging_start_selection_changed)
        self.comboBox_logging_stop.currentIndexChanged.connect(self.logging_stop_selection_changed)
        self.dateTimeEdit_logging_start.setDateTime(QDateTime.currentDateTime())
        self.dateTimeEdit_logging_stop.setDateTime(QDateTime.currentDateTime())

        self.dateTimeEdit_logging_start.hide()
        self.dateTimeEdit_logging_stop.hide()
        self.label_24h.hide()
        self.label_logger_interval_show.setText("")

        self.show()

        self.queue_timer = QTimer()
        self.miscellaneous_timer = QTimer()
        self.device_connectivity_status_timer = QTimer()

        self.init_timers()

    """code segment for: port select window"""

    # def initialize_main_window(self):
    #     self.port_select_window.hide()
    #     self.show()
    #     self.init_timers()
    def disconnect_logger(self):

        self.connect_button.setDisabled(True)
        self.clear_labels()
        try:
            self.disconnect_buttons()
        except TypeError:
            pass

        self.label_device_id.setText("Disconnecting Logger. Please wait")
        self.label_device_id.setStyleSheet('color:red;')

        TaskConsumer().insert_task(Task(TaskTypes.SERIAL_DISCONNECT_LOGGER, self.task_done_callback))

    def connect_logger(self):

        self.connect_button.setDisabled(True)

        self.label_device_id.setText("Searching for Logger.")
        self.label_device_id.setStyleSheet('color:orange;')
        self.label_device_id.show()

        TaskConsumer().insert_task(Task(TaskTypes.SERIAL_CONNECT_LOGGER, self.task_done_callback))

    def init_timers(self):
        self.init_queue_task_consumer_thread()
        self.init_miscellaneous_task_consumer_thread()
        self.init_check_device_connectivity_status()

    def connect_buttons(self):

        # self.actionStart_reading_logged_data.setDisabled(False)
        # self.actionRemove_all_logged_data.setDisabled(False)
        # self.actionStart_real_time_data_streaming.setDisabled(False)
        # self.actionSync_logger_to_computer_time.triggered.setDisabled(False)

        self.actionStart_reading_logged_data.triggered.connect(lambda: self.start_reading_logger_data())
        self.actionRemove_all_logged_data.triggered.connect(lambda: self.erase_data())
        self.actionStart_real_time_data_streaming.triggered.connect(lambda: self.start_reading_realtime_data())
        self.actionSync_logger_to_computer_time.triggered.connect(lambda: self.sync_device_and_system_time())

        self.btn_read_logger_data.clicked.connect(self.start_reading_logger_data)
        self.btn_real_time_data.clicked.connect(self.start_reading_realtime_data)
        self.btn_set_logging_interval.clicked.connect(self.set_logging_interval)
        self.btn_device_rename.clicked.connect(self.rename_device)

        # self.checkBox_dst.setDisabled(False)
        self.checkBox_dst.clicked.connect(self.toogle_dst)

        self.btn_sync_device_system_time.clicked.connect(self.sync_device_and_system_time)
        self.btn_set_alarm.clicked.connect(self.set_alarm)

        # self.btn_erase_data.setDisabled(False)
        self.btn_erase_data.clicked.connect(self.erase_data)

        self.btn_set_start_stop_option.clicked.connect(self.set_logging_start_stop)

        # self.btn_reset_factory_settings.setDisabled(False)
        self.btn_reset_factory_settings.clicked.connect(self.reset_device)

    def led_off(self):
        TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_LED_STATUS, self.task_done_callback, "0,0,0"))

    def led_on(self):
        TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_LED_STATUS, self.task_done_callback, "1,1,0"))

    def disconnect_buttons(self):

        # self.actionStart_reading_logged_data.setDisabled(True)
        # self.actionRemove_all_logged_data.setDisabled(True)
        # self.actionStart_real_time_data_streaming.setDisabled(True)
        # self.actionSync_logger_to_computer_time.triggered.setDisabled(True)

        self.btn_read_logger_data.clicked.disconnect(self.start_reading_logger_data)
        self.btn_real_time_data.clicked.disconnect(self.start_reading_realtime_data)
        self.btn_set_logging_interval.clicked.disconnect(self.set_logging_interval)
        self.btn_device_rename.clicked.disconnect(self.rename_device)

        self.checkBox_dst.setDisabled(True)
        self.checkBox_dst.clicked.disconnect(self.toogle_dst)

        self.btn_sync_device_system_time.clicked.disconnect(self.sync_device_and_system_time)
        self.btn_set_alarm.clicked.disconnect(self.set_alarm)
        # self.btn_erase_data.setDisabled(True)
        self.btn_erase_data.clicked.disconnect(self.erase_data)
        self.btn_set_start_stop_option.clicked.disconnect(self.set_logging_start_stop)

        # self.btn_reset_factory_settings.setDisabled(True)

    def reset_device(self):
        if not self.device_selecton.isActiveWindow():
            self.device_selecton.raise_()
            self.device_selecton.activateWindow()

        if TaskConsumer().q != []:
            self.show_alert_dialog("Logger is busy")
        else:
            if self.is_reading_mode():
                self.waiting_window_end()
                self.device_selecton.initialize_and_show()

    def start_reading_realtime_data(self):
        if not self.real_time_window.isActiveWindow():
            self.real_time_window.raise_()
            self.real_time_window.activateWindow()

        if TaskConsumer().q != []:
            pass
        else:
            if self.is_reading_mode():
                self.waiting_window_end()
                self.real_time_window.initialize_and_show()

    def init_queue_task_consumer_thread(self):
        self.queue_timer.setInterval(1)
        self.queue_timer.timeout.connect(self.consume_queue_task)

    def init_miscellaneous_task_consumer_thread(self):
        self.miscellaneous_timer.setInterval(1000)
        self.miscellaneous_timer.timeout.connect(self.consume_miscellaneous_task)

    def init_check_device_connectivity_status(self):
        self.device_connectivity_status_timer.setInterval(3000)
        self.device_connectivity_status_timer.timeout.connect(self.check_device_connectivity_status)
        self.device_connectivity_status_timer.start()

    def consume_queue_task(self):
        TaskConsumer().consume_task()

    def consume_miscellaneous_task(self):
        self.update_system_time()
        self.update_device_time()

    def check_device_connectivity_status(self):
        dr = DataReader()
        device = dr.get_connected_device()
        # print(f'searching for device, found {device}')
        if device:
            if not self.queue_timer.isActive():
                self.queue_timer.start()

            if not self.miscellaneous_timer.isActive():
                self.miscellaneous_timer.start()

            if not dr.is_port_open():
                self.label_device_id.setText('CreDock connected. Searching for a logger...')
                self.label_device_id.setStyleSheet('color:green;')
                TaskConsumer().insert_task(Task(TaskTypes.SERIAL_OPEN, self.task_done_callback))
                try:
                    self.disconnect_buttons()
                except TypeError:
                    pass
            # else:
            #     print('port is already open')
        else:
            self.after_device_not_found_change()

    def after_device_not_found_change(self):
        self.queue_timer.stop()
        self.miscellaneous_timer.stop()
        TaskConsumer().clear_task_queue()
        DataReader().close()

        self.label_device_id.setText('Please connect a CreDock')
        self.label_device_id.setStyleSheet("color:red")
        try:
            self.disconnect_buttons()
        except TypeError:
            pass
        self.lbl_device_id.setText("")
        self.label_device_type.setText("")
        self.label_battery_level.setText("")
        self.label_battery_level_low_signal.setText("")
        self.label_device_time.setText("")
        self.lineEdit_device_name.setText("")
        self.label_logger_interval_show.setText("")

    def rename_device(self):

        test = self.lineEdit_device_name.text()

        if ' ' in test:
            self.show_alert_dialog('Space is not allowed in device name.\nPlease use \'_\' or \'-\' instead')
        elif not test.isascii():
            self.show_alert_dialog('Invalid characters found in name.')
        elif len(test) > 255:
            self.show_alert_dialog('Device name can be maximum 255 characters')
        else:
            if self.is_reading_mode():
                new_name = self.lineEdit_device_name.text()
                TaskConsumer().insert_task(Task(TaskTypes.SERIAL_RENAME_DEV_NAME, self.task_done_callback, new_name))

    def erase_data(self):
        reply = QMessageBox.question(self, 'Message', "Are you sure ? All data will be deleted with this action.",
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # logger.debug("worked")
            if self.is_reading_mode():
                TaskConsumer().insert_task(Task(TaskTypes.SERIAL_ERASE, self.task_done_callback))
        if reply == QMessageBox.No:
            pass

    def set_logging_start_stop(self):

        start_status = self.comboBox_logging_start.currentIndex()
        print(f'start stat: {start_status}')

        stop_status = self.comboBox_logging_stop.currentIndex()
        print(f'stop stat: {stop_status}')

        cdt = QDateTime.currentDateTime()

        if start_status == 1 and self.dateTimeEdit_logging_start.dateTime() <= cdt:
            self.waiting_window_end()
            self.show_alert_dialog("Start date & time cannot be less than current date & time.")
            return

        elif stop_status == 1 and self.dateTimeEdit_logging_stop.dateTime() <= cdt:
            self.waiting_window_end()
            self.show_alert_dialog("Stop date & time cannot be less than current date & time.")
            return

        elif start_status == 1 and stop_status == 1 and self.dateTimeEdit_logging_start.dateTime() >= self.dateTimeEdit_logging_stop.dateTime():
            self.waiting_window_end()
            self.show_alert_dialog("Start date & time should be greater than stop date & time.")
            return

        else:
            if self.is_reading_mode():
                start_td = self.dateTimeEdit_logging_start.dateTime().toString("h:m:s d/M/yy")
                stop_td = self.dateTimeEdit_logging_stop.dateTime().toString("h:m:s d/M/yy")
                w_str = " ".join([str(start_status), start_td, str(stop_status), stop_td])
                print(w_str)
                TaskConsumer().insert_task(
                    Task(TaskTypes.SERIAL_WRITE_LOG_START_STOP, self.task_done_callback, str(w_str)))

    def set_alarm(self):
        high_temp = 85
        low_temp = -45
        high_hum = 100
        low_hum = 0
        high_pre = 1200
        low_pre = 600
        if self.is_reading_mode():
            try:
                if self.chk_dev_id == 'CSL-H2 T0.2':
                    high_temp = int(self.lineEdit_high_temp.text())
                    low_temp = int(self.lineEdit_low_temp.text())
                    high_hum = int(self.lineEdit_high_hum.text())
                    low_hum = int(self.lineEdit_low_hum.text())
                    # self.lineEdit_high_pressure.setDisabled(True)
                    # self.lineEdit_low_pressure.setDisabled(True)

                    if low_temp > high_temp:
                        self.waiting_window_end()
                        self.show_alert_dialog("High temperature should be greater than low.")
                        return
                    elif high_temp > 85:
                        self.waiting_window_end()
                        self.show_alert_dialog("High temperature can be maximum 85.")
                        return
                    elif low_temp < -45:
                        self.waiting_window_end()
                        self.show_alert_dialog("Low temperature should be greater than or equal to -40.")
                        return

                    if low_hum > high_hum:
                        self.waiting_window_end()
                        self.show_alert_dialog("High humidity should be greater than low.")
                        return
                    elif high_hum > 100:
                        self.waiting_window_end()
                        self.show_alert_dialog("Humidity can be maximum 100.")
                        return
                    elif low_hum < 0:
                        self.waiting_window_end()
                        self.show_alert_dialog("Minimum value 0.")
                        return

                if self.chk_dev_id == 'CSL-H2 P1 T0.2':
                    high_temp = int(self.lineEdit_high_temp.text())
                    low_temp = int(self.lineEdit_low_temp.text())
                    high_hum = int(self.lineEdit_high_hum.text())
                    low_hum = int(self.lineEdit_low_hum.text())
                    high_pre = int(self.lineEdit_high_pressure.text())
                    low_pre = int(self.lineEdit_low_pressure.text())

                    if low_temp > high_temp:
                        self.show_alert_dialog("High temperature should be greater than low.")
                        return
                    elif high_temp > 85:
                        self.show_alert_dialog("High temperature can be maximum 85.")
                        return
                    elif low_temp < -45:
                        self.show_alert_dialog("Low temperature should be greater than or equal to -45.")
                        return

                    if low_hum > high_hum:
                        self.show_alert_dialog("High humidity should be greater than low.")
                        return
                    elif high_hum > 100:
                        self.show_alert_dialog("Humidity can be maximum 100.")
                        return
                    elif low_hum < 0:
                        self.show_alert_dialog("Low Humidity should be greater than or equal to 0.")
                        return

                    if low_pre > high_pre:
                        self.show_alert_dialog("High pressure should be greater than low.")
                        return
                    elif high_pre > 1200:
                        self.show_alert_dialog("Pressure can be maximum 1200.")
                        return
                    elif low_pre < 600:
                        self.show_alert_dialog("Low Pressure should be greater than or equal to 0.")
                        return

                if self.chk_dev_id == 'CSL-T0.5':
                    high_temp = int(self.lineEdit_high_temp.text())
                    low_temp = int(self.lineEdit_low_temp.text())
                    # self.lineEdit_high_hum.setDisabled(True)
                    # self.lineEdit_low_hum.setDisabled(True)
                    # self.lineEdit_high_pressure.setDisabled(True)
                    # self.lineEdit_low_pressure.setDisabled(True)

                    if low_temp > high_temp:
                        self.show_alert_dialog("High temperature should be greater than low.")
                        return
                    elif high_temp > 85:
                        self.show_alert_dialog("High temperature can be maximum 85.")
                        return
                    elif low_temp < -45:
                        self.show_alert_dialog("Low temperature should be greater than or equal to -45.")
                        return

                if self.checkBox_temp_alarm_status.isChecked():

                    new_str = " ".join(
                        ["1", str(high_temp), str(low_temp), str(high_hum), str(low_hum), str(high_pre), str(low_pre)])
                else:
                    new_str = " ".join(
                        ["0", str(high_temp), str(low_temp), str(high_hum), str(low_hum), str(high_pre), str(low_pre)])

                TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_ALARM, self.task_done_callback, new_str))

            except ValueError:
                self.waiting_window_end()
                self.show_alert_dialog("Only integer numbers are supported for alarm")

            except AttributeError:
                self.waiting_window_end()
                pass

    def logging_start_selection_changed(self, i):
        if self.comboBox_logging_start.currentIndex() == 0 and self.comboBox_logging_stop.currentIndex() == 0:
            self.label_24h.hide()

        if i == 0:
            self.dateTimeEdit_logging_start.hide()
        else:
            self.dateTimeEdit_logging_start.show()
            self.label_24h.show()

    def logging_stop_selection_changed(self, i):
        if self.comboBox_logging_start.currentIndex() == 0 and self.comboBox_logging_stop.currentIndex() == 0:
            self.label_24h.hide()

        if i == 0:
            self.dateTimeEdit_logging_stop.hide()
        else:
            self.dateTimeEdit_logging_stop.show()
            self.label_24h.show()

    def toogle_dst(self):
        if self.is_reading_mode():
            new_str = '1' if self.checkBox_dst.isChecked() else "0"
            TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_DAYLIGHT, self.task_done_callback, new_str))

    def update_system_time(self):
        current_dt = datetime.datetime.now()
        self.label_system_time.setText(current_dt.strftime("%d %b %Y, %H:%M:%S"))

    def update_device_time(self):
        if utils.CURRENT_DEVICE_TIME_RESPONSE:
            utils.CURRENT_DEVICE_TIME_RESPONSE = utils.CURRENT_DEVICE_TIME_RESPONSE + datetime.timedelta(seconds=1)
            self.label_device_time.setText(utils.CURRENT_DEVICE_TIME_RESPONSE.strftime("%d %b %Y, %H:%M:%S"))

    def sync_device_and_system_time(self):
        if self.is_reading_mode():
            dt_str = datetime.datetime.now().strftime('%H:%M:%S %d/%m/%y')
            TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_TIME, self.task_done_callback, dt_str))

    def task_done_callback(self, response):
        try:
            print(f"task response : {response}")
            if len(TaskConsumer().q) <= 1:
                self.waiting_window_end()

            if response['data'] == None and response['task_type'] != TaskTypes.SERIAL_ERASE:
                TaskConsumer().clear_task_queue()
                TaskConsumer().insert_task(Task(TaskTypes.SERIAL_OPEN, self.task_done_callback))

            if 'exception' in response:
                return

            if response['task_type'] == TaskTypes.SERIAL_OPEN:
                # self.connect_button.show()
                TaskConsumer().insert_task(Task(TaskTypes.SERIAL_CONNECT_LOGGER, self.task_done_callback))
                # print('done')
                pass
                # TaskConsumer().insert_task(Task(TaskTypes.SERIAL_READING_MODE, self.task_done_callback))

            elif response['task_type'] == TaskTypes.SERIAL_CONNECT_LOGGER:
                data = response['data']
                if data == 'yes' or data == 'connected':
                    self.logger_connected = True
                    self.connect_button.setText("Disconnect")

                    try:
                        self.connect_button.clicked.disconnect()
                    except Exception as e:
                        print(e)
                    self.connect_button.clicked.connect(self.disconnect_logger)
                    self.connect_button.setDisabled(False)

                    TaskConsumer().insert_task(Task(TaskTypes.SERIAL_READING_MODE, self.task_done_callback))
                else:
                    self.connect_button.setDisabled(True)
                    self.label_device_id.setText('Searching for a Logger')
                    self.label_device_id.setStyleSheet('color:orange;')

                    TaskConsumer().clear_task_queue()
                    TaskConsumer().insert_task(Task(TaskTypes.SERIAL_CONNECT_LOGGER, self.task_done_callback))

            elif response['task_type'] == TaskTypes.SERIAL_DISCONNECT_LOGGER:
                data = response['data']
                if data == 'yes' or data == 'disconnected':
                    self.logger_connected = False
                    self.label_device_id.setText('Disconnected')
                    self.label_device_id.setStyleSheet('color:red;')

                    self.connect_button.setText("Connect")
                    self.connect_button.clicked.disconnect()
                    self.connect_button.clicked.connect(self.connect_logger)
                    self.connect_button.setDisabled(False)

                    TaskConsumer().clear_task_queue()
                elif data == 'no':
                    TaskConsumer().insert_task(Task(TaskTypes.SERIAL_DISCONNECT_LOGGER, self.task_done_callback))
                else:
                    print('no data')

            elif response['task_type'] == TaskTypes.SERIAL_READING_MODE:
                data = response['data']

                if data == 'no_device':
                    self.label_device_id.setText('Disconnected')
                    self.label_device_id.setStyleSheet('color:red;')
                    self.connect_button.setText("Connect")
                    self.connect_button.clicked.disconnect(self.disconnect_logger)
                    self.connect_button.clicked.connect(self.connect_logger)
                    self.connect_button.setDisabled(False)
                    TaskConsumer().clear_task_queue()
                    TaskConsumer().insert_task(Task(TaskTypes.SERIAL_READING_MODE, self.task_done_callback))

                elif data == 'not_found':
                    self.label_device_id.setText('Disconnected')
                    self.label_device_id.setStyleSheet('color:red;')
                    self.connect_button.setText("Connect")
                    self.connect_button.clicked.disconnect(self.disconnect_logger)
                    self.connect_button.clicked.connect(self.connect_logger)
                    self.connect_button.setDisabled(False)
                    TaskConsumer().clear_task_queue()
                    TaskConsumer().insert_task(Task(TaskTypes.SERIAL_READING_MODE, self.task_done_callback))

                elif data == 'found':
                    self.waiting_window()
                    TaskConsumer().insert_task(Task(TaskTypes.SERIAL_DEV_ID, self.task_done_callback))

                    TaskConsumer().insert_task(Task(TaskTypes.SERIAL_BATTERY, self.task_done_callback))

                    TaskConsumer().insert_task(Task(TaskTypes.SERIAL_TIME, self.task_done_callback))

                    TaskConsumer().insert_task(Task(TaskTypes.SERIAL_DEV_NAME, self.task_done_callback))

                    TaskConsumer().insert_task(Task(TaskTypes.SERIAL_READ_LOG, self.task_done_callback))

                    TaskConsumer().insert_task(Task(TaskTypes.SERIAL_READ_DAYLIGHT, self.task_done_callback))

                    TaskConsumer().insert_task(Task(TaskTypes.SERIAL_READ_ALARM, self.task_done_callback))
                    # TaskConsumer().insert_task(Task(TaskTypes.SERIAL_REAL_TIME, self.task_done_callback))
                    TaskConsumer().insert_task(Task(TaskTypes.SERIAL_RTC_ERROR, self.task_done_callback))

            elif response['task_type'] == TaskTypes.SERIAL_TIME:
                time, date = response['data'].strip().split()
                #
                # if battery_percentage>100:
                #     battery_percentage = 100
                # self.label_battery_level_low_signal.setText(', ' + str(int(battery_percentage)) + '% '
                #                                                                                            'remaining')

                datetime_str = date + ' ' + time
                try:
                    datetime_object = datetime.datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
                    utils.CURRENT_DEVICE_TIME_RESPONSE = datetime_object
                    self.update_device_time()
                    if self.label_device_time.text() != self.label_system_time.text():
                        self.btn_sync_device_system_time.setStyleSheet("background-color: rgb(237, 65, 65);\n""color: "
                                                                       "rgb(255, 255, 255);")
                    else:
                        self.btn_sync_device_system_time.setStyleSheet(
                            "background-color: rgb(34, 232, 28);\n""color: rgb(0, 0, 0);")

                except ValueError:
                    self.show_alert_dialog(
                        "Logger timekeeping failed.\nPlease change/insert battery before syncing time")

            elif response['task_type'] == TaskTypes.SERIAL_BATTERY:
                battery = response['data']
                self.label_battery_level.setText(str(battery) + " V")
                self.label_battery_level.show()
                if float(battery.strip()) <= CONSCIOUS_BATTERY_LEVEL:
                    if float(battery.strip()) <= 1.0:
                        self.label_battery_level_low_signal.setText("No battery")
                        self.label_battery_level.hide()
                    else:
                        self.label_battery_level_low_signal.setText("Battery low, please replace (CR2450)")
                    self.label_battery_level_low_signal.setStyleSheet("color: red; ")
                else:
                    self.label_battery_level_low_signal.setStyleSheet("")
                    self.label_battery_level_low_signal.setText("")

            elif response['task_type'] == TaskTypes.SERIAL_RTC_ERROR:
                self.label_device_id.setText("Connected")
                # self.connect_button.setText("Disconnect")
                self.connect_button.show()
                self.connect_button.clicked.connect(self.disconnect_logger)
                self.connect_buttons()
                self.waiting_window_end()
                if response['data'] == 'yes':
                    self.show_alert_dialog(
                        "Clock battery level critical.\nPlease change/insert logger's clock battery (CR1025)")

            elif response['task_type'] == TaskTypes.SERIAL_DEV_NAME:
                self.lineEdit_device_name.setText(response['data'])

            elif response['task_type'] == TaskTypes.SERIAL_READ_CONST:
                utils.READ_CONST_RESPONSE = response['data']
                # print(utils.READ_CONST_RESPONSE)

            elif response['task_type'] == TaskTypes.SERIAL_READ_LOGGER_DATA:
                # self.msg_box_read_log_data.close()
                # self.msg_box_read_log_data.close()

                self.p.progressBar.setValue(80)
                self.p.setWindowTitle('Generating graph')
                logger_plot_window = LoggerPlotWindow(self)
                try:
                    if response['data']:
                        logger_plot_window.initialize_and_show(1, response['data'])
                        self.p.progressBar.setValue(100)
                        self.p.close()
                    else:
                        self.p.close()
                        msg_box = QMessageBox(self)
                        msg_box.setIcon(QMessageBox.Information)
                        msg_box.setText("Logger has no data")
                        msg_box.setWindowTitle("Message")
                        msg_box.setStandardButtons(QMessageBox.Ok)
                        msg_box.exec_()
                except Exception as er:
                    self.show_error_dialog("Error! Data corrupted\nPlease erase all logged data")
                    reply = QMessageBox.question(self, 'Recovery',
                                                 "Do you want to save the corrupted data to a text file?",
                                                 QMessageBox.Yes, QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        qfd = QFileDialog(self)
                        options = qfd.Options()
                        options |= qfd.DontUseNativeDialog
                        file_dir = qfd.getExistingDirectory(self, "Choose a folder", "", qfd.ShowDirsOnly)
                        if file_dir:
                            full_file_path = os.path.join(file_dir, 'Recovery_CSL_Series_Logger.txt')
                            f = open(full_file_path, "w+")
                            f.write("Data Format: \nLogging start time: Hour("
                                    "24hour):Minute:Second<space>Date/Month/Year<space>Data points<space>Interval, "
                                    "\nRecordings: \'Temperature<space>Humidity<space>Pressure\'\n")
                            f.write(str(response['data']))
                    self.p.close()
                    print(er)

            elif response['task_type'] == TaskTypes.SERIAL_RENAME_DEV_NAME:
                self.show_alert_dialog("Device rename successful!")

            elif response['task_type'] == TaskTypes.SERIAL_WRITE_TIME:
                TaskConsumer().insert_task(Task(TaskTypes.SERIAL_TIME, self.task_done_callback))
                self.show_alert_dialog("Write time successful!")

            elif response['task_type'] == TaskTypes.SERIAL_WRITE_LOG:
                TaskConsumer().insert_task(Task(TaskTypes.SERIAL_READ_LOG, self.task_done_callback))
                self.show_alert_dialog("Logging interval set successfully!")

            elif response['task_type'] == TaskTypes.SERIAL_ERASE:
                self.show_alert_dialog("Erase successful")

            elif response['task_type'] == TaskTypes.SERIAL_WRITE_LOG_START_STOP:
                TaskConsumer().insert_task(Task(TaskTypes.SERIAL_READ_LOG, self.task_done_callback))
                self.show_alert_dialog("Logging start stop time setting successful!")


            elif response['task_type'] == TaskTypes.SERIAL_READ_ALARM:
                alarm_status, high_temp_value, low_temp_value, high_hum_value, low_hum_value, high_pre_value, low_pre_value \
                    = \
                    response['data'].split(' ')

                if alarm_status == '1':
                    self.checkBox_temp_alarm_status.setChecked(True)
                    self.lineEdit_high_temp.setText(high_temp_value)
                    self.lineEdit_low_temp.setText(low_temp_value)

                    self.lineEdit_low_temp.setDisabled(False)
                    self.lineEdit_high_temp.setDisabled(False)
                    self.lineEdit_low_hum.setDisabled(True)
                    self.lineEdit_high_hum.setDisabled(True)
                    self.lineEdit_low_pressure.setDisabled(True)
                    self.lineEdit_high_pressure.setDisabled(True)
                    self.label_alarm.setText("Alarm is enabled. Temp High: " + high_temp_value + " | Low: " + low_temp_value)

                    if self.chk_dev_id == 'CSL-H2 T0.2':
                        self.lineEdit_high_hum.setText(high_hum_value)
                        self.lineEdit_low_hum.setText(low_hum_value)

                        self.lineEdit_low_temp.setDisabled(False)
                        self.lineEdit_high_temp.setDisabled(False)
                        self.lineEdit_low_hum.setDisabled(False)
                        self.lineEdit_high_hum.setDisabled(False)
                        self.lineEdit_low_pressure.setDisabled(True)
                        self.lineEdit_high_pressure.setDisabled(True)
                        self.label_alarm.setText("Alarm is enabled. Temp High: " + high_temp_value + " Low: " + low_temp_value \
                                                 + " | RH High: " + high_hum_value + " Low: " + low_hum_value)
                    if self.chk_dev_id == 'CSL-H2 P1 T0.2':
                        self.lineEdit_high_hum.setText(high_hum_value)
                        self.lineEdit_low_hum.setText(low_hum_value)
                        self.lineEdit_high_pressure.setText(high_pre_value)
                        self.lineEdit_low_pressure.setText(low_pre_value)

                        self.lineEdit_low_temp.setDisabled(False)
                        self.lineEdit_high_temp.setDisabled(False)
                        self.lineEdit_low_hum.setDisabled(False)
                        self.lineEdit_high_hum.setDisabled(False)
                        self.lineEdit_low_pressure.setDisabled(False)
                        self.lineEdit_high_pressure.setDisabled(False)
                        self.label_alarm.setText("Alarm is enabled. Temp High: " + high_temp_value + " Low: " + low_temp_value \
                                                 + " | RH high: " + high_hum_value + " Low: " + low_hum_value \
                                                 + " | BMP high: " + high_pre_value + " Low: " + low_pre_value)
                else:
                    self.checkBox_temp_alarm_status.setChecked(False)
                    self.label_alarm.setText("Alarm is off")

            elif response['task_type'] == TaskTypes.SERIAL_WRITE_ALARM:
                TaskConsumer().insert_task(Task(TaskTypes.SERIAL_READ_ALARM, self.task_done_callback))
                self.show_alert_dialog("Write alarm successful!")

            elif response['task_type'] == TaskTypes.SERIAL_READ_LOG:
                utils.READ_LOG_RESPONSE = response['data']
                self.interval, start_type, start_time, start_date, stop_type, stop_time, stop_date = response[
                    'data'].split()
                self.lineEdit_logging_interval.setText(self.interval)
                self.label_logger_interval_show.setText(
                    "Logging interval is currently set to " + self.interval + " minute(s)")
                self.update_logging_start_stop(start_type, start_time, start_date, stop_type, stop_time, stop_date)

            elif response['task_type'] == TaskTypes.SERIAL_WRITE_DAYLIGHT:
                if self.checkBox_dst.isChecked():
                    self.show_alert_dialog("Daylight saving turned on successfully!")
                else:
                    self.show_alert_dialog("Daylight saving turned off successfully!")

            elif response['task_type'] == TaskTypes.SERIAL_READ_DAYLIGHT:
                if response['data'] == '1':
                    self.checkBox_dst.setChecked(True)
                else:
                    self.checkBox_dst.setChecked(False)
            # elif response['task_type'] == TaskTypes.SERIAL_REAL_TIME:
            #     self.realtime = response['data']

            elif response['task_type'] == TaskTypes.SERIAL_DEV_ID:

                self.lbl_device_id.setText(response['data'])
                self.label_device_id.setText("Logger Found, Connecting...")
                self.label_device_id.setStyleSheet("color:green")
                self.chk_dev_id = response['data']

                if self.chk_dev_id == 'CSL-T0.5':
                    TaskConsumer().insert_task(Task(TaskTypes.SERIAL_READ_CONST, self.task_done_callback))
                    self.label_device_type.setText('Temperature Logger')
                    self.lineEdit_high_temp.setDisabled(False)
                    self.lineEdit_low_temp.setDisabled(False)
                    self.lineEdit_high_hum.setDisabled(True)
                    self.lineEdit_low_hum.setDisabled(True)
                    self.lineEdit_high_pressure.setDisabled(True)
                    self.lineEdit_low_pressure.setDisabled(True)

                if self.chk_dev_id == 'CSL-H2 T0.2':
                    self.label_device_type.setText('Temperature and Relative Humidity Logger')
                    self.lineEdit_high_temp.setDisabled(False)
                    self.lineEdit_low_temp.setDisabled(False)
                    self.lineEdit_high_hum.setDisabled(False)
                    self.lineEdit_low_hum.setDisabled(False)
                    self.lineEdit_high_pressure.setDisabled(True)
                    self.lineEdit_low_pressure.setDisabled(True)

                if self.chk_dev_id == 'CSL-H2 P1 T0.2':
                    self.label_device_type.setText('Temperature, Relative Humidity, and Barometric Pressure Logger')
                    self.lineEdit_high_temp.setDisabled(False)
                    self.lineEdit_low_temp.setDisabled(False)
                    self.lineEdit_high_hum.setDisabled(False)
                    self.lineEdit_low_hum.setDisabled(False)
                    self.lineEdit_high_pressure.setDisabled(False)
                    self.lineEdit_low_pressure.setDisabled(False)


        except Exception as response_error:
            print(response_error)
            TaskConsumer().insert_task(Task(TaskTypes.SERIAL_READING_MODE, self.task_done_callback))

        # elif response['task_type'] == TaskTypes.SERIAL_REAL_TIME:
        #     print(response)

    def update_logging_start_stop(self, start_type, start_time, start_date, stop_type, stop_time, stop_date):

        if start_type == '0':
            self.comboBox_logging_start.setCurrentIndex(0)
        else:
            try:
                self.comboBox_logging_start.setCurrentIndex(1)
                hour, minutes, seconds = start_time.split(':')
                dtf = datetime.datetime.strptime(start_date, '%d/%m/%y')
                dt = QtCore.QDateTime(QDate(dtf.year, dtf.month, dtf.day), QTime(int(hour), int(minutes), int(seconds)))
                self.dateTimeEdit_logging_start.setDateTime(dt)
            except:
                self.show_error_dialog("Error in start option")

        if stop_type == '0':
            self.comboBox_logging_stop.setCurrentIndex(0)
        else:
            try:
                self.comboBox_logging_stop.setCurrentIndex(1)
                hour, minutes, seconds = stop_time.split(':')
                dtf = datetime.datetime.strptime(stop_date, '%d/%m/%y')
                dt = QtCore.QDateTime(QDate(dtf.year, dtf.month, dtf.day), QTime(int(hour), int(minutes), int(seconds)))
                self.dateTimeEdit_logging_stop.setDateTime(dt)
            except:
                self.show_error_dialog("Error in stop option")

    def set_logging_interval(self):
        interval_value = self.lineEdit_logging_interval.text()

        if interval_value == "":
            self.waiting_window_end()
            self.show_alert_dialog("Interval cannot be empty")
            return

        elif not interval_value.isnumeric() or int(interval_value) > 1440 or int(interval_value) < 1:
            self.waiting_window_end()
            self.show_alert_dialog("Interval should be positive and within range 1 to 1440")
            return

        else:
            if self.is_reading_mode():
                TaskConsumer().insert_task(Task(TaskTypes.SERIAL_WRITE_LOG, self.task_done_callback, interval_value))

    def start_reading_logger_data(self):

        if TaskConsumer().q != []:
            self.show_alert_dialog("Logger is busy")
        else:
            if self.is_reading_mode():
                TaskConsumer().insert_task(Task(TaskTypes.SERIAL_READ_LOGGER_DATA, self.task_done_callback))
                self.p = ProgBar()
                # self.p.pbar.setStyleSheet('margin: 20px;')
                self.p.show()

    # self.msg_box_read_log_data = CustomDialog(self)
    # self.msg_box_read_log_data.show()

    def is_reading_mode(self):
        self.reading_mode_chk = DataReader().read_data('reading_mode')
        if self.reading_mode_chk == 'found':
            self.waiting_window()
            return True
        else:
            # self.init_check_device_connectivity_status()
            # self.check_device_connectivity_status()
            TaskConsumer().insert_task(Task(TaskTypes.SERIAL_READING_MODE, self.task_done_callback))
            self.clear_labels()
            self.show_error_dialog("Error.\nMake sure logger is connected and programming mode is turned on")
            return False

    def reconnect(self):
        pass
        # self.disconnect_logger()
        # TaskConsumer().insert_task(Task(TaskTypes.SERIAL_READING_MODE, self.task_done_callback))

    def clear_labels(self):
        self.label_alarm.setText("")
        self.label_device_id.setText("")
        self.lbl_device_id.setText("")
        self.label_device_type.setText("")
        self.label_battery_level.setText("")
        self.label_battery_level_low_signal.setText("")
        self.label_device_time.setText("")
        self.lineEdit_device_name.setText("")
        utils.CURRENT_DEVICE_TIME_RESPONSE = None
        self.lineEdit_logging_interval.setText("")
        self.label_logger_interval_show.setText("")
        self.lineEdit_high_temp.setText("")
        self.lineEdit_low_temp.setText("")
        self.lineEdit_high_hum.setText("")
        self.lineEdit_low_hum.setText("")
        self.lineEdit_low_pressure.setText("")
        self.lineEdit_high_pressure.setText("")
        # self.reconnect_button.hide()
        self.btn_sync_device_system_time.setStyleSheet("")

    def show_alert_dialog(self, msg):
        # self.waiting_window_end()
        self.alert_msg_box.setIcon(QMessageBox.Information)
        self.alert_msg_box.setText(msg)
        self.alert_msg_box.setWindowTitle("Message")
        self.alert_msg_box.setStandardButtons(QMessageBox.Ok)
        self.alert_msg_box.show()
        self.alert_msg_box.exec_()

    def show_error_dialog(self, msg):
        self.waiting_window_end()
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(msg)
        msg_box.setWindowTitle("Message")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def closeEvent(self, event):
        if self.logger_connected == False or self.logger_connected is None:
            reply = QMessageBox.question(self, 'Exit CredoWare', "Do you want to quit?", QMessageBox.Yes,
                                         QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.queue_timer.stop()
                self.miscellaneous_timer.stop()
                self.device_connectivity_status_timer.stop()
                self.reading_timer.stop()
                TaskConsumer().clear_task_queue()
                DataReader().close()

                # self.real_time_window.close()
                self.about_window.close()
                self.device_selecton.close()

                event.accept()
            else:
                event.ignore()
        else:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setText("Please disconnect logger before closing")
            msg_box.setWindowTitle("Exit CredoWare")
            ok_btn = msg_box.addButton('OK', QMessageBox.RejectRole)
            exit_btn = msg_box.addButton('Close anyway', QMessageBox.ActionRole)
            exit_btn.setStyleSheet('padding:5px;')
            exit_btn.setMinimumWidth(100)
            exit_btn.setMinimumHeight(15)
            ok_btn.setStyleSheet('padding:5px;')
            ok_btn.setMinimumHeight(15)
            ok_btn.setMinimumWidth(100)
            msg_box.exec_()
            if msg_box.clickedButton() == exit_btn:
                event.accept()
            else:
                event.ignore()

    def waiting_window(self):
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
        except:
            pass

    def waiting_window_end(self):
        try:
            QApplication.restoreOverrideCursor()
        except:
            pass


if __name__ == '__main__':
    try:
        app = QApplication([])

        screen_resolution = app.desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        w = 550
        h = 750
        app.setApplicationName("CredoWare")
        try:
            app.setWindowIcon(QtGui.QIcon("logo.png"))
        except Exception as er:
            print(er)
            pass
        window = MainWindow()
        if (height < 1000):
            if width < 1000:
                window.resize(width / 2, height - 150)
                window.move(int(width / 2 - width / 2 / 2), int(height / 2 - (height - 150) / 2) - (width / 100))
            else:
                window.resize(600, height - 150)
                window.move(int(width / 2 - 600 / 2), int(height / 2 - (height - 150) / 2) - (width / 100))
        else:
            window.resize(w, h)
            window.move(int(width / 2 - w / 2), int((height / 2 - h / 2) - (width / 100)))
        app.exec_()

    except Exception as er:
        print(er)
        rollbar.report_exc_info()
    finally:
        pass
