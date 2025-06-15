from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QComboBox, QLineEdit, QHBoxLayout, QSizePolicy
from src.GraphBuilder import GraphBuilder, DataLoader
from src.ParsesFiles import ParseFiles
from PySide6.QtWidgets import QFileDialog, QDialog
from scipy import signal as sig

from src.calculate_mode_signal_and_conv import calculate_conv, min_max_normalize, z_score_normalize, modulate_signal
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QScrollArea
from PySide6.QtCore import Qt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from src.ConvPlotWindow import ConvPlotWindow


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Анализ спектров, сигналов и их сверток")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.scroll_layout = QVBoxLayout()
        scroll_content = QWidget()
        scroll_content.setLayout(self.scroll_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_content)

        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(scroll_area)

        main_controls_layout = QHBoxLayout()
        controls1 = QVBoxLayout()
        controls2 = QVBoxLayout()

        self.combo_x = QComboBox()
        self.combo_y = QComboBox()
        controls1.addWidget(self.combo_x)
        controls1.addWidget(self.combo_y)
        range_layout1 = QHBoxLayout()
        self.x_min_edit1 = QLineEdit()
        self.x_min_edit1.setPlaceholderText("Минимальная частота (0 Гц)")
        self.x_max_edit1 = QLineEdit()
        self.x_max_edit1.setPlaceholderText("Максимальная частота (12500 Гц)")
        range_layout1.addWidget(self.x_min_edit1)
        range_layout1.addWidget(self.x_max_edit1)
        controls1.addLayout(range_layout1)
        self.btn_parse_plot = QPushButton(
            "Построить график спектра из файла .dtx")
        self.btn_parse_plot.clicked.connect(self.create_parsed_plot)
        controls1.addWidget(self.btn_parse_plot)
        self.btn_update_plot = QPushButton(
            "Перестроить выбранный график спектра")
        self.btn_update_plot.clicked.connect(self.update_plot_by_columns)
        controls1.addWidget(self.btn_update_plot)
        self.btn_modulate = QPushButton(
            "Построить смоделированный сигнал из спектра")
        self.btn_modulate.clicked.connect(self.create_modulated_plot)
        controls1.addWidget(self.btn_modulate)

        self.combo_x2 = QComboBox()
        self.combo_y2 = QComboBox()
        controls2.addWidget(self.combo_x2)
        controls2.addWidget(self.combo_y2)
        range_layout2 = QHBoxLayout()
        self.x_min_edit2 = QLineEdit()
        self.x_min_edit2.setPlaceholderText("Начальное время (0 с)")
        self.x_max_edit2 = QLineEdit()
        self.x_max_edit2.setPlaceholderText("Конечное время (6 с)")
        range_layout2.addWidget(self.x_min_edit2)
        range_layout2.addWidget(self.x_max_edit2)
        controls2.addLayout(range_layout2)
        self.btn_parse_plot2 = QPushButton(
            "Построить график оригинального сигнала")
        self.btn_parse_plot2.clicked.connect(self.create_parsed_plot2)
        controls2.addWidget(self.btn_parse_plot2)
        self.btn_update_plot2 = QPushButton(
            "Перестроить выбранный график оригинального сигнала")
        self.btn_update_plot2.clicked.connect(self.update_plot_by_columns2)
        controls2.addWidget(self.btn_update_plot2)

        main_controls_layout.addLayout(controls1)
        main_controls_layout.addLayout(controls2)
        self.scroll_layout.addLayout(main_controls_layout)

        self.graph_spectr_layout = QVBoxLayout()
        self.graph_signal_layout = QVBoxLayout()
        self.graph_modulated_layout = QVBoxLayout()
        self.graph_spectr = QWidget()
        self.graph_signal = QWidget()
        self.graph_modulated = QWidget()
        self.graph_spectr.setLayout(self.graph_spectr_layout)
        self.graph_signal.setLayout(self.graph_signal_layout)
        self.graph_modulated.setLayout(self.graph_modulated_layout)
        self.scroll_layout.addWidget(self.graph_spectr)
        self.scroll_layout.addWidget(self.graph_signal)
        self.scroll_layout.addWidget(self.graph_modulated)
        self.current_canvas_spectr = None
        self.current_canvas_signal = None
        self.current_canvas_modulated = None

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
        self.scroll_layout.addLayout(conv_params_layout)

        self.btn_conv_mod = QPushButton("Свертка смоделированного сигнала")
        self.btn_conv_mod.clicked.connect(self.create_conv_mod_plot)
        self.scroll_layout.addWidget(self.btn_conv_mod)
        self.btn_conv_orig = QPushButton("Свертка оригинального сигнала")
        self.btn_conv_orig.clicked.connect(self.create_conv_orig_plot)
        self.scroll_layout.addWidget(self.btn_conv_orig)

        self.df = None
        self.df2 = None

        self.graph_spectr_layout.setContentsMargins(0, 0, 0, 0)
        self.graph_signal_layout.setContentsMargins(0, 0, 0, 0)
        self.graph_modulated_layout.setContentsMargins(0, 0, 0, 0)
        self.graph_spectr_layout.setSpacing(0)
        self.graph_signal_layout.setSpacing(0)
        self.graph_modulated_layout.setSpacing(0)
        self.graph_spectr.setSizePolicy(QSizePolicy.Expanding,
                                        QSizePolicy.Minimum)
        self.graph_signal.setSizePolicy(QSizePolicy.Expanding,
                                        QSizePolicy.Minimum)
        self.graph_modulated.setSizePolicy(QSizePolicy.Expanding,
                                           QSizePolicy.Minimum)

    def show_error(self, message: str, title: str = "Ошибка") -> None:
        """Показывает окно с ошибкой пользователю."""
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()

    def get_float_from_lineedit(self,
                                lineedit: QLineEdit,
                                default: float = 0.0,
                                name: str = "значение",
                                type_number: str = 'int') -> float:
        """
        Безопасно получает float или int из QLineEdit, показывает ошибку при неверном вводе.
        :param lineedit: QLineEdit для чтения значения
        :param default: значение по умолчанию
        :param name: имя параметра для сообщения об ошибке
        :param type_number: 'int' или 'float'
        :return: число (float или int)
        """
        try:
            if type_number == 'int':
                return int(lineedit.text())
            elif type_number == 'float':
                return float(lineedit.text())
        except ValueError:
            self.show_error(
                f"Некорректный ввод для {name}. Введите число. По умолчанию будет использовано {default}."
            )
            return default

    def clear_and_add_canvas(self, layout: QVBoxLayout,
                             current_canvas_attr: str, fig,
                             parent_widget: QWidget) -> None:
        """
        Очищает старый canvas и добавляет новый для графика.
        :param layout: QVBoxLayout, куда добавляется canvas
        :param current_canvas_attr: имя атрибута для хранения текущего canvas
        :param fig: matplotlib.figure.Figure
        :param parent_widget: QWidget, родительский виджет для canvas
        """
        current_canvas = getattr(self, current_canvas_attr)
        if current_canvas is not None:
            layout.removeWidget(current_canvas)
            current_canvas.setParent(None)
            current_canvas.deleteLater()
            setattr(self, current_canvas_attr, None)
        new_canvas = GraphBuilder.embed_to_widget(fig, parent_widget)
        layout.addWidget(new_canvas)
        setattr(self, current_canvas_attr, new_canvas)

    def create_parsed_plot(self) -> None:
        """Загружает спектр из файла и строит график спектра."""
        df = DataLoader.load_from_file(True, self)
        if df is None:
            self.show_error("Не удалось загрузить файл или файл пустой.")
            return
        self.df = df
        self.combo_x.clear()
        self.combo_y.clear()
        self.combo_x.addItems(list(df.columns))
        self.combo_y.addItems(list(df.columns))
        self.combo_y.setCurrentIndex(2)
        x_min = self.get_float_from_lineedit(self.x_min_edit1, 0,
                                             'Минимальная частота', 'int')
        x_max = self.get_float_from_lineedit(self.x_max_edit1, 12500,
                                             'Максимальная частота', 'int')
        fig = GraphBuilder.create_spectr_plot(df,
                                              x_col=df.columns[0],
                                              y_col=df.columns[2],
                                              x_min=x_min,
                                              x_max=x_max,
                                              title="График спектра")
        self.clear_and_add_canvas(self.graph_spectr_layout,
                                  'current_canvas_spectr', fig,
                                  self.graph_spectr)

    def update_plot_by_columns(self) -> None:
        """Перестраивает график спектра по выбранным столбцам и диапазону."""
        if self.df is None:
            self.show_error("Сначала загрузите данные для спектра.")
            return
        x_col = self.combo_x.currentText()
        y_col = self.combo_y.currentText()
        x_min = self.get_float_from_lineedit(self.x_min_edit1, 0,
                                             'Минимальная частота', 'int')
        x_max = self.get_float_from_lineedit(self.x_max_edit1, 12500,
                                             'Максимальная частота', 'int')
        fig = GraphBuilder.create_spectr_plot(self.df,
                                              x_col=x_col,
                                              y_col=y_col,
                                              x_min=x_min,
                                              x_max=x_max,
                                              title="График спектра")
        self.clear_and_add_canvas(self.graph_spectr_layout,
                                  'current_canvas_spectr', fig,
                                  self.graph_spectr)

    def create_parsed_plot2(self) -> None:
        """Загружает сигнал из файла и строит график оригинального сигнала."""
        df2 = DataLoader.load_from_file(False, self)
        if df2 is None:
            self.show_error("Не удалось загрузить файл или файл пустой.")
            return
        self.df2 = df2
        self.combo_x2.clear()
        self.combo_y2.clear()
        self.combo_x2.addItems(list(df2.columns))
        self.combo_y2.addItems(list(df2.columns))
        self.combo_y2.setCurrentIndex(1)
        x_min = self.get_float_from_lineedit(self.x_min_edit2, 0,
                                             'Начальное время', 'float')
        x_max = self.get_float_from_lineedit(self.x_max_edit2, 6,
                                             'Конечное время', 'float')
        fig2 = GraphBuilder.create_spectr_plot(
            df2,
            x_col=df2.columns[0],
            y_col=df2.columns[1],
            x_min=x_min,
            x_max=x_max,
            title="График оригинального сигнала")
        self.clear_and_add_canvas(self.graph_signal_layout,
                                  'current_canvas_signal', fig2,
                                  self.graph_signal)

    def update_plot_by_columns2(self) -> None:
        """Перестраивает график оригинального сигнала по выбранным столбцам и диапазону."""
        if self.df2 is None:
            self.show_error("Сначала загрузите данные для сигнала.")
            return
        x_col = self.combo_x2.currentText()
        y_col = self.combo_y2.currentText()
        x_min = self.get_float_from_lineedit(self.x_min_edit2, 0,
                                             'Начальное время', 'float')
        x_max = self.get_float_from_lineedit(self.x_max_edit2, 6,
                                             'Конечное время', 'float')
        fig2 = GraphBuilder.create_spectr_plot(
            self.df2,
            x_col=x_col,
            y_col=y_col,
            x_min=x_min,
            x_max=x_max,
            title="График оригинального сигнала")
        self.clear_and_add_canvas(self.graph_signal_layout,
                                  'current_canvas_signal', fig2,
                                  self.graph_signal)

    def create_modulated_plot(self) -> None:
        """Строит график смоделированного сигнала на основе спектра."""
        if self.df is None:
            self.show_error("Сначала загрузите спектр.")
            return
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
        self.mod_signal = mod_signal
        x_min_mod = self.x_min_edit2.text() or None
        x_max_mod = self.x_max_edit2.text() or None
        fig = GraphBuilder.create_signal_plot(
            mod_signal,
            self.df2,
            x_col='Время, с',
            y_col="Сигнал нормированный [-1,1]",
            x_min=x_min_mod,
            x_max=x_max_mod)
        self.clear_and_add_canvas(self.graph_modulated_layout,
                                  'current_canvas_modulated', fig,
                                  self.graph_modulated)

    def create_conv_mod_plot(self) -> None:
        """Строит график свёртки смоделированного сигнала."""
        if not hasattr(self, 'mod_signal'):
            self.show_error(
                "Сначала постройте график смоделированного сигнала.")
            return
        Nx = Ny = self.get_float_from_lineedit(self.n_edit, 1, "Nx = Ny",
                                               'float')
        N = (Nx, Ny)
        S = np.array(self.mod_signal)
        S = z_score_normalize(S)
        y_col = self.combo_y.currentText()
        x_min = self.x_min_edit1.text() or 0
        x_max = self.x_max_edit1.text() or 12500
        t0 = self.get_float_from_lineedit(self.t0_edit, 0, "t0", 'int')
        M = self.get_float_from_lineedit(self.m_edit, 3, "M", 'int')
        try:
            X_i, Y_i, W, t_end = calculate_conv(N, S, t0, M, self.df, y_col,
                                                x_min, x_max)
        except ValueError as e:
            self.show_error(
                f"Ошибка вычисления свёртки: {str(e)}.\nВозможно, выбран некорректный диапазон или t0 слишком велик. Попробуйте уменьшить t0 или M"
            )
            return
        fig = GraphBuilder.plot_conv_mod(X_i, Y_i, M, t0, t_end, W, N[0], True)

        # --- Новый функционал: callback для перестроения по частоте (смоделированный сигнал) ---
        def recalc_conv_mod(freq: float):
            try:
                X_i, Y_i, _, t_end = calculate_conv(N,
                                                    S,
                                                    t0,
                                                    M,
                                                    self.df,
                                                    y_col,
                                                    x_min,
                                                    x_max,
                                                    force_W=freq)
                return GraphBuilder.plot_conv_mod(X_i, Y_i, M, t0, t_end, freq,
                                                  N[0], True)
            except Exception as e:
                self.show_error(f"Ошибка пересчёта свёртки: {e}")
                return None

        self.conv_window_mod = ConvPlotWindow(fig,
                                              self,
                                              recalc_callback=recalc_conv_mod,
                                              default_freq=W)
        self.conv_window_mod.show()

    def create_conv_orig_plot(self) -> None:
        """Строит график свёртки оригинального сигнала."""
        if not hasattr(self, 'df2') or self.df2 is None:
            self.show_error("Сначала постройте график оригинального сигнала.")
            return
        Nx = Ny = self.get_float_from_lineedit(self.n_edit, 1, "Nx = Ny",
                                               'float')
        N = (Nx, Ny)
        orig_col = [
            col for col in self.df2.columns if col != self.df2.columns[0]
        ][0]
        S = np.array(self.df2[orig_col])
        S = z_score_normalize(S)
        t0 = self.get_float_from_lineedit(self.t0_edit, 0, "t0", 'int')
        M = self.get_float_from_lineedit(self.m_edit, 3, "M", 'int')
        y_col = self.combo_y.currentText()
        x_min = self.x_min_edit1.text() or 0
        x_max = self.x_max_edit1.text() or 12500
        try:
            X_i, Y_i, W, t_end = calculate_conv(N, S, t0, M, self.df, y_col,
                                                x_min, x_max)
        except ValueError as e:
            self.show_error(
                f"Ошибка вычисления свёртки: {str(e)}.\nВозможно, выбран некорректный диапазон или t0 слишком велик. Попробуйте уменьшить t0 или M"
            )
            return
        fig = GraphBuilder.plot_conv_mod(X_i, Y_i, M, t0, t_end, W, N[0],
                                         False)

        # --- Новый функционал: callback для перестроения по частоте ---
        def recalc_conv_orig(freq: float):
            try:
                # freq — это W, частота для свёртки
                X_i, Y_i, _, t_end = calculate_conv(N,
                                                    S,
                                                    t0,
                                                    M,
                                                    self.df,
                                                    y_col,
                                                    x_min,
                                                    x_max,
                                                    force_W=freq)
                return GraphBuilder.plot_conv_mod(X_i, Y_i, M, t0, t_end, freq,
                                                  N[0], False)
            except Exception as e:
                self.show_error(f"Ошибка пересчёта свёртки: {e}")
                return None

        # --- Передаём callback и частоту по умолчанию ---
        self.conv_window_orig = ConvPlotWindow(
            fig, self, recalc_callback=recalc_conv_orig, default_freq=W)
        self.conv_window_orig.show()
