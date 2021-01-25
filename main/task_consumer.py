import threading
import traceback
from PyQt5.QtCore import QObject, pyqtSignal, QThreadPool, pyqtSlot, QRunnable
from MySingleton import SingletonMeta
from data_reader import DataReader


class TaskTypes:
    """
    This class is basically a command list.
    """
    SERIAL_OPEN = 'open'
    SERIAL_DEV_ID = "read_dev_ID"
    SERIAL_RENAME_DEV_NAME = 'write_dev_name'
    SERIAL_DEV_NAME = 'read_dev_name'
    SERIAL_TIME = 'read_time'
    SERIAL_BATTERY = 'read_battery'
    SERIAL_READ_LOGGER_DATA: str = 'read'
    SERIAL_READ_LOG = 'read_log'
    SERIAL_READ_CONST = 'read_const'
    SERIAL_READING_MODE = 'reading_mode'
    SERIAL_READ_DAYLIGHT = 'read_daylight'
    SERIAL_ERASE = 'erase'
    SERIAL_WRITE_DAYLIGHT = 'write_daylight'
    SERIAL_WRITE_TIME = 'write_time'
    SERIAL_WRITE_LOG = 'write_log'
    SERIAL_WRITE_LOG_START_STOP = 'write_start_stop'
    SERIAL_READ_ALARM = 'read_alarm'
    SERIAL_WRITE_ALARM = 'write_alarm'
    SERIAL_READ_NUMBER_OF_DATA = 'read_row'
    SERIAL_REAL_TIME = 'real_time'
    SERIAL_READ_ERROR = 'read_error'
    SERIAL_ERASE_CHIP = 'erase_chip'
    SERIAL_WRITE_STRING = 'write_string'
    SERIAL_READ_STRING = 'read_string'
    SERIAL_WRITE_LONG = 'write_long'
    SERIAL_READ_LONG = 'read_long'
    SERIAL_WRITE_INT = 'write_int'
    SERIAL_READ_INT = 'read_int'
    SERIAL_WRITE_FLOAT = 'write_float'
    SERIAL_READ_FLOAT = 'read_float'
    SERIAL_WRITE_BYTE = 'write_byte'
    SERIAL_READ_BYTE = 'read_byte'
    SERIAL_RTC_ERROR = 'rtc_error'
    SERIAL_WRITE_LED_STATUS = 'led_stat'
    SERIAL_WRITE_LED_BRIGHTNESS = 'led_bright'
    SERIAL_CONNECT_LOGGER = 'con'
    SERIAL_DISCONNECT_LOGGER = 'discon'

class TaskStatus:
    WAITING = 0
    RUNNING = 1
    DONE = 2
    FAILED = 3


class TaskSignals(QObject):
    done = pyqtSignal(object)


class Task(QRunnable):

    def __init__(self, task_type: str, emit_fn, new_data=None):
        super(Task, self).__init__()
        self.status = TaskStatus.WAITING
        self.task_type = task_type
        self.emit_fn = emit_fn
        self.new_data = new_data
        self.signals = TaskSignals()
        self.signals.done.connect(self.emit_fn)

    @pyqtSlot()
    def run(self):
        response = dict()
        response['task_type'] = self.task_type
        try:
            self.status = TaskStatus.RUNNING
            # print(self.args)
            result = do_task(self.task_type, self.new_data)
        except Exception as e:
            traceback.print_exc()
            # print(e)
            response['exception'] = e
            self.status = TaskStatus.FAILED
        else:
            response['data'] = result
            self.status = TaskStatus.DONE
        finally:
            self.signals.done.emit(response)


def do_task(task_type, new_data):
    # print(f" do task : {task_type}  {args}")
    dr = DataReader()
    device = dr.get_connected_device()

    if not device:
        raise Exception("Device not found")

    if task_type == TaskTypes.SERIAL_OPEN:
        # dev = dr.get_connected_device()
        # print(device.device)
        dr.open(device.device)
        return 'OK'

    elif task_type == TaskTypes.SERIAL_DEV_ID or task_type == TaskTypes.SERIAL_DEV_NAME \
            or task_type == TaskTypes.SERIAL_TIME \
            or task_type == TaskTypes.SERIAL_BATTERY \
            or task_type == TaskTypes.SERIAL_RTC_ERROR \
            or task_type == TaskTypes.SERIAL_READ_DAYLIGHT \
            or task_type == TaskTypes.SERIAL_READ_LOG \
            or task_type == TaskTypes.SERIAL_READ_CONST \
            or task_type == TaskTypes.SERIAL_READ_ALARM\
            or task_type == TaskTypes.SERIAL_READING_MODE \
            or task_type == TaskTypes.SERIAL_READ_LOGGER_DATA \
            or task_type == TaskTypes.SERIAL_REAL_TIME \
            or task_type == TaskTypes.SERIAL_READ_ERROR\
            or task_type == TaskTypes.SERIAL_ERASE\
            or task_type == TaskTypes.SERIAL_ERASE_CHIP\
            or task_type == TaskTypes.SERIAL_CONNECT_LOGGER\
            or task_type == TaskTypes.SERIAL_DISCONNECT_LOGGER:

        if not dr.is_port_open():
            raise Exception("Device port is closed.")

        response = dr.read_data(task_type)
        return response

    elif task_type == TaskTypes.SERIAL_RENAME_DEV_NAME \
            or task_type == TaskTypes.SERIAL_WRITE_TIME\
            or task_type == TaskTypes.SERIAL_WRITE_LOG\
            or task_type == TaskTypes.SERIAL_WRITE_ALARM\
            or task_type == TaskTypes.SERIAL_WRITE_DAYLIGHT\
            or task_type == TaskTypes.SERIAL_WRITE_LOG_START_STOP\
            or task_type == TaskTypes.SERIAL_WRITE_BYTE\
            or task_type == TaskTypes.SERIAL_WRITE_FLOAT\
            or task_type == TaskTypes.SERIAL_WRITE_INT\
            or task_type == TaskTypes.SERIAL_WRITE_LONG\
            or task_type == TaskTypes.SERIAL_WRITE_STRING\
            or task_type == TaskTypes.SERIAL_WRITE_LED_STATUS\
            or task_type == TaskTypes.SERIAL_WRITE_LED_BRIGHTNESS:
        if not dr.is_port_open():
            raise Exception("Device port is closed.")

        response = dr.write_data(task_type, new_data)
        return response
    elif task_type == TaskTypes.SERIAL_READ_BYTE \
            or task_type == TaskTypes.SERIAL_READ_FLOAT \
            or task_type == TaskTypes.SERIAL_READ_INT \
            or task_type == TaskTypes.SERIAL_READ_LONG \
            or task_type == TaskTypes.SERIAL_READ_STRING:

        if not dr.is_port_open():
            raise Exception("Device port is closed.")

        response = dr.write_then_read_data(task_type, new_data)
        return response

class TaskConsumer(metaclass=SingletonMeta):

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.q = list()
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(1)

    def set_thread_pool(self, tp):
        self.thread_pool = tp

    def insert_task(self, task: Task) -> None:
        """
        Insert task if whether its not in queue or its status is either done or failed.
        :param task:
        :return:
        """
        with self.lock:
            self.__remove_finished_task()
            if not any(task.task_type == each.task_type for each in self.q):
                self.q.append(task)

    def get_task(self) -> Task:
        with self.lock:
            self.__remove_finished_task()
            if self.q:
                for each in self.q:
                    if each.task_type == TaskTypes.SERIAL_OPEN:
                        return each
                return self.q[0]
            else:
                return None

    def consume_task(self) -> None:
        task = self.get_task()
        if task and self.thread_pool.activeThreadCount() == 0:
            self.thread_pool.start(task)

    def clear_task_queue(self) -> None:
        self.q.clear()
        self.thread_pool.clear()

    def __remove_finished_task(self) -> None:
        clr_lst = [index for index, task in enumerate(self.q) if task.status > TaskStatus.RUNNING]
        for index in clr_lst:
            del self.q[index]



