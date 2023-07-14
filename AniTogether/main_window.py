from __future__ import annotations

import typing as ty

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMainWindow
from loguru import logger
from qasync import asyncClose

from anilibria_agent import AnilibriaAgent
from ui import Ui_MainWindow
from ui_function import window_geometry, home_page, player_page


if ty.TYPE_CHECKING:
    from PyQt6 import QtCore, QtGui
    from anilibria import Title


class MainWindow(QMainWindow, Ui_MainWindow):
    # Страница плеера открыта
    playerPageIsOpen: QtCore.pyqtBoundSignal = pyqtSignal()
    homePageIsOpen: QtCore.pyqtBoundSignal = pyqtSignal()

    def __init__(self):
        logger.trace("Initialization of the main window")
        super().__init__()
        self.setupUi(self)

        self.setMinimumSize(820, 520)

        # Окно без рамок
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinimizeButtonHint
        )

        self.setupUiFunctions()

        # Подготавливаем область, отвечающую за перемещение окна
        window_geometry.prepareDragZone(self, self.topFrame)
        # Подготавливаем области, отвечающие за изменение размеров окна
        window_geometry.prepareSizeGrips(self)

        self.openHomePage()

    def setupUiFunctions(self) -> None:
        logger.trace("Setting main window signals")

        # Управление окном
        self.closeAppBtn.clicked.connect(self.close)
        self.maximizeAppBtn.clicked.connect(
            lambda: window_geometry.toggleFullScreen(self)
        )  # Кнопка открытия приложения в полный экран
        self.minimizeAppBtn.clicked.connect(self.showMinimized)

        home_page.setupUiFunctions(self)
        player_page.setupUiFunctions(self)

    def openHomePage(self) -> None:
        home_page.openHomePage(self)

    def openPlayerPage(self, title: Title, episode_number: int = 1) -> None:
        player_page.openPlayerPage(self, title, episode_number)

    def resizeEvent(self, _: QtGui.QResizeEvent) -> None:
        self.scrollAreaContainer.setMaximumWidth(self.width())

    @asyncClose
    async def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        Обработчик события закрытия приложения.
        """
        await AnilibriaAgent.disconnect()
