import sys
from src.App import Application
from src.MainWindow import MainWindow


def main():
    app = Application(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
