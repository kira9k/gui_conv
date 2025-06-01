from PySide6.QtWidgets import QApplication


class Application(QApplication):
    """
    Класс-обёртка над QApplication для запуска Qt-приложения.
    """

    def __init__(self, args: list[str]) -> None:
        """
        Инициализация приложения.
        :param args: список аргументов командной строки
        """
        super().__init__(args)
