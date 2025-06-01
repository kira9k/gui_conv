from PySide6.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ConvPlotWindow(QDialog):
    """
    Окно для отображения графика свёртки сигнала.
    """

    def __init__(self, fig, parent=None) -> None:
        """
        Инициализация окна с графиком свёртки.
        :param fig: matplotlib.figure.Figure для отображения
        :param parent: родительский виджет (по умолчанию None)
        """
        super().__init__(parent)
        self.setWindowTitle("График свёртки сигнала")
        self.setMinimumSize(600, 400)
        layout = QVBoxLayout()
        self.setLayout(layout)
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
