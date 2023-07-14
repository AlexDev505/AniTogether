from __future__ import annotations

import asyncio
import typing as ty
from functools import partial

from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPixmap
from loguru import logger

from anilibria_agent import AnilibriaAgent, AnilibriaAgentException
from tools import circle_image
from widgets import SearchResultWidget


if ty.TYPE_CHECKING:
    from anilibria import Title
    from main_window import MainWindow
    from anilibria import Title
    from PyQt6 import QtGui
    from main_window import MainWindow


anilibria_agent = AnilibriaAgent.get()
last_search_use: float = 0


def setupUiFunctions(main_window: MainWindow) -> None:
    main_window.__setattr__("searchResultWidget", None)
    main_window.__setattr__("originalResizeEvent" + __name__, main_window.resizeEvent)
    main_window.resizeEvent = partial(resizeEvent, main_window)


def show(main_window: MainWindow, titles: list[Title]) -> None:
    """
    Отображает результаты поиска релизов.
    """
    close(main_window)
    if not len(titles):
        return

    searchResultWidget = SearchResultWidget(main_window)
    main_window.__setattr__("searchResultWidget", searchResultWidget)
    searchResultWidget.show()

    for title in titles:
        foundTitleWidget = searchResultWidget.addTitle()
        foundTitleWidget.title = title
        foundTitleWidget.mousePressEvent = partial(
            titleWidgetMouseEvent, main_window, title
        )
        foundTitleWidget.setTitle(title.names.ru)
        start_loading_poster(
            foundTitleWidget.titleIcon,
            foundTitleWidget.titleIcon.minimumHeight(),
            (title.posters.small or title.posters.medium or title.posters.original).url,
        )

    pos = main_window.centralWidget().mapFromGlobal(
        main_window.searchLineEdit.mapToGlobal(QPoint(0, 0))
    )  # Получаем глобальные координаты строки поиска
    pos.setY(pos.y() + main_window.searchLineEdit.height() + 5)  # Отступ 5px вниз
    searchResultWidget.move(pos)
    searchResultWidget.setMinimumWidth(main_window.searchLineEditFrame.width())
    searchResultWidget.setMaximumWidth(main_window.width() - pos.x() * 2)
    # Через 200 миллисекунд обновляем размер виджета,
    # чтобы большие названия релизов скрылись
    # (функция не срабатывает на элементах, которые еще не отображены)
    QTimer.singleShot(
        200,
        partial(searchResultWidget.setWidth, searchResultWidget.width()),
    )


def start_loading_poster(
    posterLabel: QLabel,  # noqa
    size: int,
    poster_url: str,
) -> None:
    """
    Асинхронно запускает загрузку постера.
    :param posterLabel: Контейнер постера.
    :param size: Размер постера.
    :param poster_url: Ссылка на постер.
    """
    asyncio.ensure_future(load_poster(posterLabel, size, poster_url))
    logger.opt(colors=True).trace(
        f"Poster for QLabel <y>{id(posterLabel)}</y> loading started"
    )


async def load_poster(
    posterLabel: QLabel,  # noqa
    size: int,
    poster_url: str,
) -> None:
    """
    Загружает постер.
    :param posterLabel: Контейнер постера.
    :param size: Размер постера.
    :param poster_url: Ссылка на постер.
    """
    try:
        poster = QPixmap()
        poster.loadFromData(await anilibria_agent.download_resource(poster_url))
    except AnilibriaAgentException as err:
        return logger.opt(colors=True).error(
            f"Poster for QLabel <y>{id(posterLabel)}</y> loading failed. "
            f"<r>{type(err).__name__}: {err}</r> (<e>poster</e>=<y>{poster_url}</y>)"
        )

    poster = circle_image(poster, size)  # Помещаем в круг
    # Виджет может быть удален до завершения скачивания
    try:
        posterLabel.setPixmap(poster)
        logger.opt(colors=True).trace(
            f"Poster for QLabel <y>{id(posterLabel)}</y> has been loaded."
        )
    except RuntimeError:
        logger.opt(colors=True).trace(f"QLabel <y>{id(posterLabel)}</y> is deleted")


def close(main_window: MainWindow) -> None:
    """
    Закрывает виджет с результатами поиска релизов.
    """
    searchResultWidget: SearchResultWidget = main_window.__getattribute__(
        "searchResultWidget"
    )
    if searchResultWidget:
        searchResultWidget.delete()
        main_window.__setattr__("searchResultWidget", None)


def resizeEvent(main_window: MainWindow, event: QtGui.QResizeEvent) -> None:
    if searchResultWidget := main_window.__getattribute__("searchResultWidget"):
        searchResultWidget.setMinimumWidth(main_window.searchLineEditFrame.width())
        searchResultWidget.setMaximumWidth(
            main_window.width() - searchResultWidget.x() * 2
        )  # Ограничиваем максимальный размер, чтобы не выходил за рамки окна
        # Ширина, которая вмещает самое длинное название
        # или растяжение до размеров строки поиска
        width = max(
            searchResultWidget.max_title_widget_width,
            main_window.searchLineEditFrame.width(),
        )
        # Меняем только если это нужно
        if searchResultWidget.width() != width:
            searchResultWidget.setWidth(width)

    main_window.__getattribute__("originalResizeEvent" + __name__)(event)


def titleWidgetMouseEvent(
    main_window: MainWindow, title: Title, event: QtGui.QMouseEvent
) -> None:
    if event.button() == Qt.MouseButton.LeftButton:
        main_window.openPlayerPage(title=title)

    logger.trace("titleWidgetMouseEvent handled")
