from __future__ import annotations

import typing as ty
from functools import partial

from PyQt6.QtCore import Qt, QPoint, QTimer, QChildEvent
from PyQt6.QtWidgets import QMainWindow
from qasync import asyncSlot, asyncClose

from logger import logger
from tools import create_loading_movie, debug_title_data, trace_title_data
from ui import Ui_MainWindow
from ui_function import window_geometry, home_page, anilibria_agent
from widgets import SearchResultWidget, PlayerControlsWidget


if ty.TYPE_CHECKING:
    from PyQt6.QtGui import QCloseEvent, QResizeEvent
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

        self.searchResultWidget: SearchResultWidget | None = None
        self.current_title: Title | None = None
        self.playerControlsWidget: PlayerControlsWidget | None = None

        self.setupSignals()

        # Подготавливаем область, отвечающую за перемещение окна
        window_geometry.prepareDragZone(self, self.topFrame)
        # Подготавливаем области, отвечающие за изменение размеров окна
        window_geometry.prepareSizeGrips(self)
        self.installEventFilter(self)

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

    def openHomePage(self) -> None:
        logger.debug("Opening the home page")
        self.stackedWidget.setCurrentWidget(self.homePage)
        logger.debug("Home page is open")

    def openPlayerPage(self, title: Title) -> None:
        logger.debug("Opening the player page")
        logger.opt(colors=True).debug(debug_title_data(title))
        logger.opt(colors=True).trace(trace_title_data(title))

        self.current_title = title

        if not self.playerControlsWidget:
            self.playerControlsWidget = PlayerControlsWidget(self)
        self.playerControlsWidget.show()
        # self.chi
        self.playerControlsWidget.updateGometry()

        self.stackedWidget.setCurrentWidget(self.playerPage)
        logger.debug("Player page is open")

    @asyncSlot()
    async def search_titles(self) -> None:
        query = self.searchLineEdit.text()
        if len(query) == 0:
            return self.closeSearchResultWidget()
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

        self.closeSearchResultWidget()

        if not len(titles):
            return

        self.searchResultWidget = SearchResultWidget(self)
        self.searchResultWidget.show()
        for title in titles:
            foundTitleWidget = self.searchResultWidget.addTitle()
            foundTitleWidget.title = title
            foundTitleWidget.mousePressEvent = partial(
                home_page.titleWidgetMouseEvent, self, title
            )
            foundTitleWidget.setTitle(title.names.ru)
            anilibria_agent.start_loading_poster(
                foundTitleWidget.titleIcon,
                foundTitleWidget.titleIcon.minimumHeight(),
                (
                    title.posters.small
                    or title.posters.medium
                    or title.posters.original
                ).url,
            )
        pos = self.centralWidget().mapFromGlobal(
            self.searchLineEdit.mapToGlobal(QPoint(0, 0))
        )  # Получаем глобальные координаты строки поиска
        pos.setY(pos.y() + self.searchLineEdit.height() + 5)  # Отступ 5px вниз
        self.searchResultWidget.move(pos)
        self.searchResultWidget.setMinimumWidth(self.searchLineEditFrame.width())
        self.searchResultWidget.setMaximumWidth(self.width() - pos.x() * 2)
        # Через 200 миллисекунд обновляем размер виджета,
        # чтобы большие названия релизов скрылись
        # (функция не срабатывает на элементах, которые еще не отображены)
        QTimer.singleShot(
            200,
            partial(self.searchResultWidget.setWidth, self.searchResultWidget.width()),
        )

    def closeSearchResultWidget(self) -> None:
        """
        Закрывает виджет с результатами поиска релизов.
        """
        if self.searchResultWidget:
            self.searchResultWidget.delete()
            self.searchResultWidget = None

    def resizeEvent(self, _: QResizeEvent) -> None:
        if self.searchResultWidget:
            self.searchResultWidget.setMinimumWidth(self.searchLineEditFrame.width())
            self.searchResultWidget.setMaximumWidth(
                self.width() - self.searchResultWidget.x() * 2
            )  # Ограничиваем максимальный размер, чтобы не выходил за рамки окна
            # Ширина, которая вмещает самое длинное название
            # или растяжение до размеров строки поиска
            width = max(
                self.searchResultWidget.max_title_widget_width,
                self.searchLineEditFrame.width(),
            )
            # Меняем только если это нужно
            if self.searchResultWidget.width() != width:
                self.searchResultWidget.setWidth(width)
        if self.stackedWidget.currentWidget() == self.playerPage:
            if self.playerControlsWidget:
                self.playerControlsWidget.updateGometry()

    def eventFilter(self, obj, event) -> bool:
        if isinstance(event, QChildEvent):
            pass

        return super(MainWindow, self).eventFilter(obj, event)

    @asyncClose
    async def closeEvent(self, event: QCloseEvent) -> None:
        """
        Обработчик события закрытия приложения.
        """
        await anilibria_agent.disconnect()
