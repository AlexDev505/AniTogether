from __future__ import annotations

import typing as ty
from functools import partial

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QMainWindow
from qasync import asyncSlot, asyncClose

from logger import logger
from tools import create_loading_movie
from ui import Ui_MainWindow, SearchResultWidget
from ui_function import window_geometry, home_page, anilibria_agent


if ty.TYPE_CHECKING:
    from PyQt6.QtGui import QCloseEvent
    from anilibria import Title


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        logger.trace("Initialization of the main window")
        super().__init__()
        self.setupUi(self)

        self.setMinimumSize(820, 520)

        # Окно без рамок
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowMinimizeButtonHint
        )

        self.frame_6.hide()  # TODO

        self.search_result_widget: SearchResultWidget | None = None

        self.setupSignals()

        # Подготавливаем область, отвечающую за перемещение окна
        window_geometry.prepareDragZone(self, self.topFrame)
        # Подготавливаем области, отвечающие за изменение размеров окна
        window_geometry.prepareSizeGrips(self)

    def setupSignals(self) -> None:
        logger.trace("Setting main window signals")

        # Управление окном
        self.closeAppBtn.clicked.connect(self.close)
        self.maximizeAppBtn.clicked.connect(
            lambda: window_geometry.toggleFullScreen(self)
        )  # Кнопка открытия приложения в полный экран
        self.minimizeAppBtn.clicked.connect(self.showMinimized)

        # Строка поиска релиза
        self.searchLineEdit.textChanged.connect(self.search_titles)
        self.searchLineEdit.focusOutEvent = partial(
            home_page.searchLineEditFocusOutEvent, self
        )

    @asyncSlot()
    async def search_titles(self) -> None:
        query = self.searchLineEdit.text()
        if len(query) == 0:
            return self.close_search_result_widget()
        elif len(query) < 3:
            return

        if not self.searchLineEditStatusLabel.movie():
            movie = create_loading_movie(self.searchLineEdit.height())
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
        """
        Закрывает виджет с результатами поиска релизов.
        """
        if self.search_result_widget:
            self.search_result_widget.delete()
            self.search_result_widget = None

    @asyncClose
    async def closeEvent(self, event: QCloseEvent) -> None:
        """
        Обработчик события закрытия приложения.
        """
        await anilibria_agent.disconnect()
