from PyQt5 import QtWidgets, uic
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os


class ReadLoggerDataWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot_data = None
        # print(data)

        # Load the UI Page
        uic.loadUi('graph_window.ui', self)
        self.setWindowTitle("Read Logged Data")
        # self.addStretch()
        self.plot([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [30, 32, 34, 32, 33, 31, 29, 32, 35, 45])

    def receive_plot_data(self, plot_data):
        self.plot_data = plot_data
        print(self.plot_data)

    def plot(self, hour, temperature):
        self.graph_widget.plot(hour, temperature)


# def main():
#     app = QtWidgets.QApplication(sys.argv)
#     main = ReadLoggerDataWindow()
#     main.show()
#     sys.exit(app.exec_())
#rtMainWindow
#
# if __name__ == '__main__':
#     main()