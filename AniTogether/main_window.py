from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow

from logger import logger
from ui import Ui_MainWindow
from ui_function import window_geometry


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        logger.trace("Initialization of the main window")
        super().__init__()
        self.setupUi(self)

        # Окно без рамок
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinimizeButtonHint
        )

        self.setupSignals()

    def setupSignals(self) -> None:
        logger.trace("Setting main window signals")
        self.closeAppBtn.clicked.connect(self.close)
        self.maximizeAppBtn.clicked.connect(
            lambda: window_geometry.toggleFullScreen(self)
        )  # Кнопка открытия приложения в полный экран
        self.minimizeAppBtn.clicked.connect(self.showMinimized)

        # Подготавливаем область, отвечающую за перемещение окна
        window_geometry.prepareDragZone(self, self.topFrame)
