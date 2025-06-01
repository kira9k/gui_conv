import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from os.path import exists
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QFileDialog
from PySide6.QtGui import QPixmap
from scipy import signal as sig

from src.ParsesFiles import ParseFiles
from src.calculate_mode_signal_and_conv import modulate_signal


class DataLoader:

    @staticmethod
    def load_from_file(flag: bool = True, parent=None) -> pd.DataFrame | None:
        """Загрузка .dtx через диалог выбора файла"""
        file_path, _ = QFileDialog.getOpenFileName(parent, "Выберите данные",
                                                   "", "Data (*.dtx)")
        if flag:
            column_names = [
                "Частота, Гц", "Норма, мВ", "СКЗ, мВ", "Макс, мВ", "Мин, мВ",
                "Среднее, мВ", "Тр_окт, мВ", "Отклик, мВ"
            ]
            skiprows = 64
        else:
            column_names = ["Время,с", "ZET210_1103_01, мВ"]
            skiprows = 53
        if file_path:
            try:
                df = ParseFiles.pars_dtx_spectr(file_path, column_names,
                                                skiprows)
                return df
            except Exception as e:
                print(f"Ошибка при загрузке данных: {e}")
        return None


class GraphBuilder:

    @staticmethod
    def create_spectr_plot(df: pd.DataFrame,
                           x_col: str = None,
                           y_col: str = None,
                           x_min: float = None,
                           x_max: float = None,
                           title: str = None) -> plt.Figure | None:
        """Строит и возвращает график спектра по DataFrame с выбором столбцов и диапазона X"""
        try:
            if x_col not in df.columns or y_col not in df.columns:
                raise ValueError(f"Нет столбца {x_col} или {y_col} в данных")
            x = df[x_col]
            y = df[y_col]
            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.set_title(title or "")
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            if x_min is not None and x_max is not None:
                ax.set_xlim(float(x_min), float(x_max))
            ax.grid(True)
            plt.close(fig)
            return fig
        except Exception as e:
            print(f"Ошибка при построении графика: {e}")
            return None

    @staticmethod
    def create_signal_plot(df: np.ndarray,
                           dt: pd.DataFrame = None,
                           x_col: str = "Время, с",
                           y_col: str = "Нормированный сигнал (-1, 1)",
                           x_min: float = None,
                           x_max: float = None) -> plt.Figure | None:
        """
        Строит и возвращает график сигнала по массиву и диапазону X.
        :param df: массив значений сигнала (numpy array)
        :param dt: DataFrame с дополнительными данными (не используется)
        :param x_col: подпись оси X
        :param y_col: подпись оси Y
        :param x_min: минимальное значение X
        :param x_max: максимальное значение X
        :return: matplotlib.figure.Figure или None при ошибке
        """
        try:
            x = np.arange(0,
                          len(df) * 0.00004,
                          0.00004)[:len(df)]  # Временная ось
            y = df
            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.set_title("График смоделированного сигнала")
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            if x_min is not None and x_max is not None:
                ax.set_xlim(float(x_min), float(x_max))
            ax.grid(True)
            plt.close(fig)
            return fig
        except Exception as e:
            print(f"Ошибка при построении графика: {e}")
            return None

    @staticmethod
    def plot_conv_mod(X: np.ndarray,
                      Y: np.ndarray,
                      M: int,
                      t0: float,
                      t_end: float,
                      W: float,
                      N: float,
                      flag_mod: bool = False) -> plt.Figure | None:
        """
        Строит график свёртки.
        :param X: массив X-координат
        :param Y: массив Y-координат
        :param M: количество периодов
        :param t0: начальное время
        :param t_end: конечное время
        :param W: частота
        :param N: коэффициент
        :param flag_mod: True для смоделированного сигнала, False для оригинального
        :return: matplotlib.figure.Figure или None при ошибке
        """
        title = 'Свертка смоделированного сигнала' if flag_mod else 'Свертка оригинального сигнала'
        try:
            fig, ax = plt.subplots()
            ax.plot(X, Y, label=title)
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_title(
                f"{title} при M = {M}, Nx = Ny = {N}\nt = [{t0}, {t_end}], W = {W}"
            )
            ax.grid(True)
            ax.legend()
            plt.close(fig)
            return fig
        except Exception as e:
            print(f"Ошибка при построении графика: {e}")
            return None

    @staticmethod
    def embed_to_widget(fig: plt.Figure, widget) -> FigureCanvas:
        """
        Встраивает график в Qt-виджет, предварительно очищая layout.
        :param fig: matplotlib.figure.Figure
        :param widget: QWidget, в который встраивается график
        :return: объект FigureCanvas
        """
        layout = widget.layout() if widget.layout() else QVBoxLayout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(canvas)
        widget.setLayout(layout)
        return canvas
