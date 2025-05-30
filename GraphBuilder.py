import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from os.path import exists
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QFileDialog
from PySide6.QtGui import QPixmap
from scipy import signal as sig

from gui_conv.src.ParsesFiles import ParseFiles
from gui_conv.src.calculate_mode_signal_and_conv import modulate_signal


class DataLoader:

    @staticmethod
    def load_from_file(flag: bool = True, parent=None):
        """Загрузка .dtx через диалог выбора файла"""
        file_path, _ = QFileDialog.getOpenFileName(parent, "Выберите данные",
                                                   "", "Data (*.dtx)")

        if flag == True:
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


class GraphBuilder:

    @staticmethod
    def create_spectr_plot(df,
                           x_col=None,
                           y_col=None,
                           x_min=None,
                           x_max=None,
                           title=None):
        """Строит и возвращает график спектра по DataFrame с выбором столбцов и диапазона X"""
        try:
            x = df[x_col]
            y = df[y_col]
            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.set_title(f"{title}")
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            if x_min is not None and x_max is not None:
                ax.set_xlim(float(x_min), float(x_max))
            ax.grid(True)
            result = fig
            plt.close(fig)
            return result
        except Exception as e:
            print(f"Ошибка при построении графика: {e}")
            return None

    @staticmethod
    def create_signal_plot(df,
                           dt,
                           x_col="Время, с",
                           y_col="Нормированный сигнал (-1, 1)",
                           x_min=None,
                           x_max=None):
        """Строит и возвращает график сигнала по DataFrame с выбором столбцов и диапазона X"""
        try:
            x = np.arange(0, 6, 0.00004)  #dt[x_col]
            y = df
            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.set_title(f"График модулированного сигнала")
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            if x_min is not None and x_max is not None:
                ax.set_xlim(float(x_min), float(x_max))
            ax.grid(True)
            result = fig
            plt.close(fig)
            return result
        except Exception as e:
            print(f"Ошибка при построении графика: {e}")

            return None

    @staticmethod
    def plot_conv_mod(X, Y, M, t0, t_end, W, N, flag_mod: bool = False):
        if flag_mod == True:
            title = 'Свертка модулированного сигнала'
        else:
            title = 'Свертка оригинального сигнала'
        try:

            fig, ax = plt.subplots()
            ax.plot(X, Y, label=f'{title}')
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_title(f"{title} при M = {M}, Nx = Ny = {N}\n"
                         f"t = [{t0}, {t_end}], W = {W}")
            ax.grid(True)
            ax.legend()
            ax.grid(True)
            result = fig
            plt.close(fig)
            return result
        except Exception as e:
            print(f"Ошибка при построении графика: {e}")
            return None

    @staticmethod
    def embed_to_widget(fig, widget):
        """Встраивает график в Qt-виджет, предварительно очищая layout"""
        # Очищаем layout перед добавлением нового canvas
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
