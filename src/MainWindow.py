from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QComboBox, QLineEdit, QHBoxLayout
from src.GraphBuilder import GraphBuilder, DataLoader
from src.ParsesFiles import ParseFiles
from PySide6.QtWidgets import QFileDialog, QDialog
from scipy import signal as sig

from src.calculate_mode_signal_and_conv import calculate_conv, min_max_normalize, z_score_normalize, modulate_signal
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from src.ConvPlotWindow import ConvPlotWindow


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Графики")
        self.setGeometry(100, 100, 800, 600)

        # Центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        # --- Управляющие элементы в две колонки ---
        main_controls_layout = QHBoxLayout()
        controls1 = QVBoxLayout()
        controls2 = QVBoxLayout()

        # Первый график: выпадающие списки, диапазон, кнопки
        self.combo_x = QComboBox()
        self.combo_y = QComboBox()
        controls1.addWidget(self.combo_x)
        controls1.addWidget(self.combo_y)
        range_layout1 = QHBoxLayout()
        self.x_min_edit1 = QLineEdit()
        self.x_min_edit1.setPlaceholderText("X min (0 Гц)")
        self.x_max_edit1 = QLineEdit()
        self.x_max_edit1.setPlaceholderText("X max (12500 Гц)")
        range_layout1.addWidget(self.x_min_edit1)
        range_layout1.addWidget(self.x_max_edit1)
        controls1.addLayout(range_layout1)
        self.btn_parse_plot = QPushButton(
            "Построить график спектра из файла .dtx")
        self.btn_parse_plot.clicked.connect(self.create_parsed_plot)
        controls1.addWidget(self.btn_parse_plot)
        self.btn_update_plot = QPushButton(
            "Перестроить выбранный график спеткра")
        self.btn_update_plot.clicked.connect(self.update_plot_by_columns)
        controls1.addWidget(self.btn_update_plot)
        self.btn_modulate = QPushButton(
            "Построить смоделированный сигнал из спектра")
        self.btn_modulate.clicked.connect(self.create_modulated_plot)
        controls1.addWidget(self.btn_modulate)

        # Второй график: выпадающие списки, диапазон, кнопки
        self.combo_x2 = QComboBox()
        self.combo_y2 = QComboBox()
        controls2.addWidget(self.combo_x2)
        controls2.addWidget(self.combo_y2)
        range_layout2 = QHBoxLayout()
        self.x_min_edit2 = QLineEdit()
        self.x_min_edit2.setPlaceholderText("X min (0 с)")
        self.x_max_edit2 = QLineEdit()
        self.x_max_edit2.setPlaceholderText("X max (6 с)")
        range_layout2.addWidget(self.x_min_edit2)
        range_layout2.addWidget(self.x_max_edit2)
        controls2.addLayout(range_layout2)
        self.btn_parse_plot2 = QPushButton("Построить график сигнала")
        self.btn_parse_plot2.clicked.connect(self.create_parsed_plot2)
        controls2.addWidget(self.btn_parse_plot2)
        self.btn_update_plot2 = QPushButton(
            "Перестроить выбранный график сигнала")
        self.btn_update_plot2.clicked.connect(self.update_plot_by_columns2)
        controls2.addWidget(self.btn_update_plot2)

        main_controls_layout.addLayout(controls1)
        main_controls_layout.addLayout(controls2)
        self.layout.addLayout(main_controls_layout)

        # Три отдельных контейнера для графиков
        self.graph_spectr = QWidget()
        self.graph_signal = QWidget()
        self.graph_modulated = QWidget()
        self.layout.addWidget(self.graph_spectr)
        self.layout.addWidget(self.graph_signal)
        self.layout.addWidget(self.graph_modulated)
        self.current_canvas_spectr = None
        self.current_canvas_signal = None
        self.current_canvas_modulated = None

        # Добавляем поля для ввода t0 и M
        conv_params_layout = QHBoxLayout()
        self.t0_edit = QLineEdit()
        self.t0_edit.setPlaceholderText("t0 (начальное время, например, 0)")
        self.m_edit = QLineEdit()
        self.m_edit.setPlaceholderText("M (кол-во периодов, например, 3)")
        self.n_edit = QLineEdit()
        self.n_edit.setPlaceholderText("Коэффициенты (Nx = Ny), например, 1)")
        conv_params_layout.addWidget(QLabel("t0:"))
        conv_params_layout.addWidget(self.t0_edit)
        conv_params_layout.addWidget(QLabel("M:"))
        conv_params_layout.addWidget(self.m_edit)
        conv_params_layout.addWidget(QLabel("Nx = Ny:"))
        conv_params_layout.addWidget(self.n_edit)
        self.layout.addLayout(conv_params_layout)

        # Кнопка и контейнер для графика свёртки модулированного сигнала
        self.btn_conv_mod = QPushButton("Свертка модулированного сигнала")
        self.btn_conv_mod.clicked.connect(self.create_conv_mod_plot)
        self.layout.addWidget(self.btn_conv_mod)
        # Кнопка и контейнер для графика свёртки оригинального сигнала
        self.btn_conv_orig = QPushButton("Свертка оригинального сигнала")
        self.btn_conv_orig.clicked.connect(self.create_conv_orig_plot)
        self.layout.addWidget(self.btn_conv_orig)

        self.df = None
        self.df2 = None

    def create_parsed_plot(self):
        # Используем DataLoader для загрузки и парсинга .dtx файла
        df = DataLoader.load_from_file(True, self)
        if df is None:
            return
        self.df = df
        self.combo_x.clear()
        self.combo_y.clear()
        self.combo_x.addItems(list(df.columns))
        self.combo_y.addItems(list(df.columns))
        self.combo_y.setCurrentIndex(2)
        # Используем индивидуальные поля диапазона X для первого графика
        x_min = self.x_min_edit1.text() or None
        x_max = self.x_max_edit1.text() or None
        fig = GraphBuilder.create_spectr_plot(df,
                                              x_col=df.columns[0],
                                              y_col=df.columns[2],
                                              x_min=x_min,
                                              x_max=x_max,
                                              title="График спектра")
        if self.current_canvas_spectr is not None:
            self.layout.removeWidget(self.current_canvas_spectr)
            self.current_canvas_spectr.setParent(None)
            self.current_canvas_spectr.deleteLater()
            self.current_canvas_spectr = None
        self.current_canvas_spectr = GraphBuilder.embed_to_widget(
            fig, self.graph_spectr)

    def update_plot_by_columns(self):
        if self.df is None:
            return
        x_col = self.combo_x.currentText()
        y_col = self.combo_y.currentText()
        x_min = self.x_min_edit1.text() or None
        x_max = self.x_max_edit1.text() or None
        fig = GraphBuilder.create_spectr_plot(self.df,
                                              x_col=x_col,
                                              y_col=y_col,
                                              x_min=x_min,
                                              x_max=x_max,
                                              title="График спектра")
        if self.current_canvas_spectr is not None:
            self.layout.removeWidget(self.current_canvas_spectr)
            self.current_canvas_spectr.setParent(None)
            self.current_canvas_spectr.deleteLater()
            self.current_canvas_spectr = None
        self.current_canvas_spectr = GraphBuilder.embed_to_widget(
            fig, self.graph_spectr)

    def create_parsed_plot2(self):
        df2 = DataLoader.load_from_file(False, self)
        if df2 is None:
            return
        self.df2 = df2
        self.combo_x2.clear()
        self.combo_y2.clear()
        self.combo_x2.addItems(list(df2.columns))
        self.combo_y2.addItems(list(df2.columns))
        self.combo_y2.setCurrentIndex(1)
        # Используем индивидуальные поля диапазона X для второго графика
        x_min = self.x_min_edit2.text() or None
        x_max = self.x_max_edit2.text() or None
        fig2 = GraphBuilder.create_spectr_plot(df2,
                                               x_col=df2.columns[0],
                                               y_col=df2.columns[1],
                                               x_min=x_min,
                                               x_max=x_max,
                                               title="График сигнала")
        if self.current_canvas_signal is not None:
            self.layout.removeWidget(self.current_canvas_signal)
            self.current_canvas_signal.setParent(None)
            self.current_canvas_signal.deleteLater()
            self.current_canvas_signal = None
        self.current_canvas_signal = GraphBuilder.embed_to_widget(
            fig2, self.graph_signal)

    def update_plot_by_columns2(self):
        if self.df2 is None:
            return
        x_col = self.combo_x2.currentText()
        y_col = self.combo_y2.currentText()
        x_min = self.x_min_edit2.text() or None
        x_max = self.x_max_edit2.text() or None
        fig2 = GraphBuilder.create_spectr_plot(self.df2,
                                               x_col=x_col,
                                               y_col=y_col,
                                               x_min=x_min,
                                               x_max=x_max,
                                               title="График сигнала")
        if self.current_canvas_signal is not None:
            self.layout.removeWidget(self.current_canvas_signal)
            self.current_canvas_signal.setParent(None)
            self.current_canvas_signal.deleteLater()
            self.current_canvas_signal = None
        self.current_canvas_signal = GraphBuilder.embed_to_widget(
            fig2, self.graph_signal)

    def create_modulated_plot(self):
        # Проверяем, что оба датафрейма загружены
        if self.df is None:
            return
        # Вызываем функцию модуляции
        x_min = self.x_min_edit1.text() or 0
        x_max = self.x_max_edit1.text() or 12500
        y_col_for_mod = self.combo_y.currentText()
        y_col_for_plot = self.combo_y2.currentText()
        mod_signal = modulate_signal(
            self.df,
            y_col=y_col_for_mod,
            x_min=x_min,
            x_max=x_max,
        )
        self.mod_signal = mod_signal  # Сохраняем для свёртки

        x_min_mod = self.x_min_edit2.text() or None
        x_max_mod = self.x_max_edit2.text() or None

        fig = GraphBuilder.create_signal_plot(
            mod_signal,
            self.df2,
            x_col="Сигнал нормированный (-1,1)",
            y_col='Время, с',
            x_min=x_min_mod,
            x_max=x_max_mod)
        if self.current_canvas_modulated is not None:
            self.layout.removeWidget(self.current_canvas_modulated)
            self.current_canvas_modulated.setParent(None)
            self.current_canvas_modulated.deleteLater()
            self.current_canvas_modulated = None
        self.current_canvas_modulated = GraphBuilder.embed_to_widget(
            fig, self.graph_modulated)

    def create_conv_mod_plot(self):
        if not hasattr(self, 'df2') or self.df2 is None or not hasattr(
                self, 'mod_signal'):
            return
        Nx = Ny = float(self.n_edit.text() or 1)
        N = (Nx, Ny)
        S = np.array(self.mod_signal)
        S = z_score_normalize(S)
        y_col = self.combo_y.currentText()
        x_min = self.x_min_edit1.text() or 0
        x_max = self.x_max_edit1.text() or 12500
        t0 = int(self.t0_edit.text() or 0)
        M = int(self.m_edit.text() or 3)
        X_i, Y_i, W, t_end = calculate_conv(N, S, t0, M, self.df, y_col, x_min,
                                            x_max)
        fig = GraphBuilder.plot_conv_mod(X_i, Y_i, M, t0, t_end, W, N[0], True)
        self.conv_window_mod = ConvPlotWindow(fig, self)
        self.conv_window_mod.show()

    def create_conv_orig_plot(self):
        if not hasattr(self, 'df2') or self.df2 is None:
            return
        Nx = Ny = float(self.n_edit.text() or 1)
        N = (Nx, Ny)
        orig_col = [
            col for col in self.df2.columns if col != self.df2.columns[0]
        ][0]
        S = np.array(self.df2[orig_col])
        S = z_score_normalize(S)
        t0 = int(self.t0_edit.text() or 0)
        M = int(self.m_edit.text() or 3)
        y_col = self.combo_y.currentText()
        x_min = self.x_min_edit1.text() or 0
        x_max = self.x_max_edit1.text() or 12500
        X_i, Y_i, W, t_end = calculate_conv(N, S, t0, M, self.df, y_col, x_min,
                                            x_max)
        fig = GraphBuilder.plot_conv_mod(X_i, Y_i, M, t0, t_end, W, N[0],
                                         False)
        self.conv_window_orig = ConvPlotWindow(fig, self)
        self.conv_window_orig.show()
