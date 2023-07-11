from __future__ import annotations

import typing as ty
from functools import lru_cache

from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QMainWindow
from qasync import asyncSlot, asyncClose

from logger import logger
from ui import Ui_MainWindow, SearchResultWidget
from ui_function import window_geometry, anilibria_agent


if ty.TYPE_CHECKING:
    from PyQt6.QtGui import QCloseEvent
    from anilibria import Title


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        logger.trace("Initialization of the main window")
        super().__init__()
        self.setupUi(self)

        # Окно без рамок
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinimizeButtonHint
        )

        self.frame_6.hide()

        self.setupSignals()

        self.search_result_widget: SearchResultWidget | None = None

        # self.searchLineEditStatusLabel.setMovie(movie)
        # movie.frameChanged.connect(
        #     lambda: self.joinToRoomBtn.setIcon(QIcon(movie.currentPixmap()))
        # )
        # movie.start()

    def setupSignals(self) -> None:
        logger.trace("Setting main window signals")
        self.closeAppBtn.clicked.connect(self.close)
        self.maximizeAppBtn.clicked.connect(
            lambda: window_geometry.toggleFullScreen(self)
        )  # Кнопка открытия приложения в полный экран
        self.minimizeAppBtn.clicked.connect(self.showMinimized)

        # Подготавливаем область, отвечающую за перемещение окна
        window_geometry.prepareDragZone(self, self.topFrame)

        self.searchLineEdit.textChanged.connect(self.search_titles)

    @asyncSlot()
    async def search_titles(self) -> None:
        query = self.searchLineEdit.text()
        if len(query) == 0:
            return self.close_search_result_widget()
        elif len(query) < 3:
            return

        if not self.searchLineEditStatusLabel.movie():
            movie = self.create_loading_movie(self.searchLineEdit.height())
            self.searchLineEditStatusLabel.setMovie(movie)
            self.searchLineEditStatusLabel.setMinimumSize(movie.scaledSize())

        try:
            titles: list[Title] = await anilibria_agent.search_titles(
                query, self.searchLineEdit
            )
        except anilibria_agent.SearchQueryUpdated:
            return

        self.searchLineEditStatusLabel.clear()

        self.close_search_result_widget()

        if not len(titles):
            return

        self.search_result_widget = SearchResultWidget(self)
        self.search_result_widget.setMinimumWidth(self.searchLineEdit.width())
        self.search_result_widget.show()
        for title in titles:
            title_widget = self.search_result_widget.addTitle()
            title_widget.setTitle(title.names.ru)
            anilibria_agent.start_loading_poster(
                title_widget.titleIcon,
                title_widget.titleIcon.minimumHeight(),
                (
                    title.posters.small
                    or title.posters.medium
                    or title.posters.original
                ).url,
            )
        pos = self.centralWidget().mapFromGlobal(
            self.searchLineEdit.mapToGlobal(QPoint(0, 0))
        )
        pos.setY(pos.y() + self.searchLineEdit.height() + 5)
        self.search_result_widget.move(pos)

    def close_search_result_widget(self) -> None:
        if self.search_result_widget:
            self.search_result_widget.delete()
            self.search_result_widget = None

    @asyncClose
    async def closeEvent(self, event: QCloseEvent) -> None:
        await anilibria_agent.disconnect()

    @staticmethod
    @lru_cache()
    def create_loading_movie(size: int) -> QMovie:
        movie = QMovie(":/base/loading.gif")
        movie.setScaledSize(QSize(size, size))
        movie.start()
        return movie
