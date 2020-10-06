from PyQt5.QtWidgets  import *
from matplotlib import style
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class MplWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure(tight_layout=True))
        # self.canvas.figure.tight_layout()
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        # self.canvas.axes.hold(False)
        style.use('ggplot')

        self.setLayout(vertical_layout)

    # def plot_data(self, x_data, y_data):
    #     plt.plot_date(x_data, y_data, linestyle='solid')