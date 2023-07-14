from __future__ import annotations

import asyncio
import typing as ty
from functools import partial
from time import time

from loguru import logger
from qasync import asyncSlot

from anilibria_agent import AnilibriaAgent
from tools import create_loading_movie
from . import search_result


if ty.TYPE_CHECKING:
    from PyQt6 import QtGui
    from main_window import MainWindow


anilibria_agent = AnilibriaAgent.get()
last_search_use: float = 0


class SearchQueryUpdated(Exception):
    pass


def setupUiFunctions(main_window: MainWindow) -> None:
    main_window.searchLineEdit.textChanged.connect(partial(search, main_window))
    main_window.searchLineEdit.focusOutEvent = partial(
        searchLineEditFocusOutEvent, main_window
    )
    search_result.setupUiFunctions(main_window)


@asyncSlot()
async def search(main_window: MainWindow) -> None:
    """
    Выполняет поиск релизов.
    """
    query = main_window.searchLineEdit.text()
    if len(query) == 0:
        return search_result.close(main_window)
    elif len(query) < 3:
        return

    logger.opt(colors=True).debug(f"Search request <e>query</e>=<y>{query}</y>")

    showLoadingMovie(main_window)
    await waitRequestsLimit()
    if main_window.searchLineEdit.text() != query:
        return
    global last_search_use
    last_search_use = time()

    titles = await anilibria_agent.search_titles(query)

    hideLoadingMovie(main_window)
    if main_window.stackedWidget.currentWidget() != main_window.homePage:
        return

    search_result.show(main_window, titles)


def showLoadingMovie(main_window: MainWindow) -> None:
    """
    Включает анимацию загрузки в строке поиска.
    """
    if not main_window.searchLineEditStatusLabel.movie():
        movie = create_loading_movie(main_window.searchLineEdit.height())
        main_window.searchLineEditStatusLabel.setMovie(movie)
        main_window.searchLineEditStatusLabel.setMinimumSize(movie.scaledSize())


def hideLoadingMovie(main_window: MainWindow) -> None:
    """
    Выключает анимацию загрузки в строке поиска.
    """
    main_window.searchLineEditStatusLabel.clear()


async def waitRequestsLimit() -> None:
    """
    Задерживает запрос, если превышен лимит.
    """
    global last_search_use
    if time() - last_search_use < 1:
        logger.trace("Requests limit exceeded. Waiting...")
        await asyncio.sleep(1)


def searchLineEditFocusOutEvent(main_window: MainWindow, _: QtGui.QFocusEvent) -> None:
    """
    Обработчик события выхода из строки поиска релиза.
    Очистка поля ввода и закрытие виджета с результатами поиска.
    """
    main_window.searchLineEdit.clear()
    search_result.close(main_window)

    logger.trace("searchLineEditFocusOutEvent handled")
