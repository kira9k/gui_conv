from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ConvPlotWindow(QDialog):

    def __init__(self, fig, parent=None):
        super().__init__(parent)
        self.setWindowTitle("График свёртки сигнала")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout()
        self.setLayout(layout)
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
