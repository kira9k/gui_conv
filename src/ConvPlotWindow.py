from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from typing import Callable, Any


class ConvPlotWindow(QDialog):
    """
    Окно для отображения и перестроения графика свёртки сигнала по выбранной частоте.
    """

    def __init__(self,
                 fig,
                 parent=None,
                 recalc_callback: Callable[[float], Any] = None,
                 default_freq: float = None) -> None:
        """
        Инициализация окна с графиком свёртки и возможностью перестроения по частоте.
        :param fig: matplotlib.figure.Figure для отображения
        :param parent: родительский виджет (по умолчанию None)
        :param recalc_callback: функция для пересчёта графика по частоте (freq: float) -> Figure
        :param default_freq: частота по умолчанию для поля ввода
        """
        super().__init__(parent)
        self.setWindowTitle("График свёртки сигнала")
        self.setMinimumSize(600, 400)
        self.recalc_callback = recalc_callback
        self.current_canvas = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        # --- Панель управления частотой ---
        freq_layout = QHBoxLayout()
        freq_label = QLabel("Частота свёртки (Гц):")
        self.freq_edit = QLineEdit()
        if default_freq is not None:
            self.freq_edit.setText(str(default_freq))
        self.rebuild_btn = QPushButton("Перестроить")
        self.rebuild_btn.clicked.connect(self.on_rebuild)
        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(self.freq_edit)
        freq_layout.addWidget(self.rebuild_btn)
        layout.addLayout(freq_layout)

        # --- График ---
        self.canvas = FigureCanvas(fig)
        layout.addWidget(self.canvas)

    def on_rebuild(self):
        """
        Перестроить график по новой частоте.
        """
        if self.recalc_callback is None:
            return
        try:
            freq = float(self.freq_edit.text())
        except ValueError:
            self.freq_edit.setStyleSheet("background: #ffcccc;")
            return
        self.freq_edit.setStyleSheet("")
        new_fig = self.recalc_callback(freq)
        if new_fig is not None:
            self._update_canvas(new_fig)

    def _update_canvas(self, fig):
        """
        Обновить canvas новым графиком.
        """
        layout = self.layout()
        if self.canvas is not None:
            layout.removeWidget(self.canvas)
            self.canvas.setParent(None)
        self.canvas = FigureCanvas(fig)
        layout.addWidget(self.canvas)
