from __future__ import annotations

import asyncio
import os
import typing as ty
from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel
from qasync import asyncSlot

from anilibria_agent import AnilibriaAgent, AnilibriaAgentException
from history import HistoryManager, TitleFromHistory
from logger import logger
from tools import rounded_image
from widgets import TitleFromHistoryWidget


if ty.TYPE_CHECKING:
    from anilibria import Title
    from PyQt6 import QtGui
    from main_window import MainWindow


anilibria_agent = AnilibriaAgent.get()
history_manager = HistoryManager(os.environ["HISTORY_PATH"])


def setupUiFunctions(main_window: MainWindow) -> None:
    main_window.homePageIsOpen.connect(partial(loadHistory, main_window))
    main_window.scrollArea.verticalScrollBar().valueChanged.connect(
        partial(scrollBarValueChanged, main_window)
    )
    main_window.scrollArea.verticalScrollBar().rangeChanged.connect(
        partial(scrollBarRangeChanged, main_window)
    )
    main_window.__setattr__("history", None)
    main_window.__setattr__("items", None)
    prepareHistoryContainer(main_window)


@asyncSlot()
async def loadHistory(main_window: MainWindow) -> None:
    history = main_window.__getattribute__("history")
    if history is None:
        history = await history_manager.load()
        main_window.__setattr__("history", history)

    if len(history) == 0:
        main_window.historyIsEmptyLabel.show()
        main_window.historyContainer.hide()
    else:
        main_window.historyIsEmptyLabel.hide()
        main_window.historyContainer.show()
        if not main_window.historyContainer.__getattribute__("filled"):
            items = []
            for i, title in enumerate(history):
                items.append(initTitleFromHistoryWidget(main_window, title))
            main_window.__setattr__("items", items)
            fillHistoryContainer(main_window)


async def updateHistory(
    main_window: MainWindow,
    title_id: int,
    episodes_count: int,
    last_watched_episode: int,
) -> None:
    history: list[TitleFromHistory] = main_window.__getattribute__("history")
    title = TitleFromHistory(title_id, episodes_count, last_watched_episode)
    if history and history[0].id == title_id:
        history[0] = title
        await history_manager.save(history)
        item: TitleFromHistoryWidget = main_window.historyContainer.findChild(
            QLabel, "TitleFromHistory"
        )
        item.updateTitle(title)
    else:
        await _updateHistory(main_window, title)


async def _updateHistory(main_window: MainWindow, title: TitleFromHistory) -> None:
    history: list[TitleFromHistory] = main_window.__getattribute__("history")
    exists = False
    for title_from_history in history:
        if title_from_history.id == title.id:
            exists = True
            history.remove(title_from_history)
            break
    history.insert(0, title)
    await history_manager.save(history)

    items = main_window.__getattribute__("items")
    items_per_line = main_window.historyContainer.__getattribute__("items_per_line")
    clearHistoryContainer(main_window)
    if exists:
        for item in items:
            if item.title.id == title.id:
                item.updateTitle(title)
                items.remove(item)
                items.insert(0, item)
    else:
        items.insert(0, initTitleFromHistoryWidget(main_window, title))
        if len(items) <= 4:
            for item in items:
                item.setMaximumWidth(item.maxWidth)

    fillHistoryContainer(main_window)


def prepareHistoryContainer(main_window: MainWindow) -> None:
    main_window.historyContainer.resizeEvent = partial(
        historyContainerResizeEvent, main_window
    )
    main_window.historyContainer.__setattr__("items_per_line", 4)
    main_window.historyContainer.__setattr__("displayed_lines", 2)
    main_window.historyContainer.__setattr__("filled", False)
    for i in range(4):
        main_window.historyContainerLayout.setColumnStretch(i, 1)


def clearHistoryContainer(main_window: MainWindow) -> None:
    for i in range(main_window.historyContainerLayout.count() - 1, -1, -1):
        child = main_window.historyContainerLayout.itemAt(i).widget()  # noqa
        child.hide()
        main_window.historyContainerLayout.removeWidget(child)
    main_window.historyContainer.__setattr__("filled", False)
    logger.trace("History container cleared")


def fillHistoryContainer(main_window: MainWindow) -> None:
    items = main_window.__getattribute__("items")
    items_per_line = main_window.historyContainer.__getattribute__("items_per_line")
    displayed_lines = main_window.historyContainer.__getattribute__("displayed_lines")
    count_to_show = items_per_line * displayed_lines
    x = y = 0
    for i, item in enumerate(items):
        if i == count_to_show:
            break
        item.show()
        main_window.historyContainerLayout.addWidget(item, y, x)
        x += 1
        if x == items_per_line:
            x = 0
            y += 1
    main_window.historyContainer.__setattr__("filled", True)
    logger.trace("History container filled")


def initTitleFromHistoryWidget(
    main_window: MainWindow, title: TitleFromHistory
) -> TitleFromHistoryWidget:
    titleFromHistoryWidget = TitleFromHistoryWidget(main_window.historyContainer, title)
    titleFromHistoryWidget.mousePressEvent = partial(
        titleWidgetMouseEvent, main_window, title
    )
    start_loading_poster(titleFromHistoryWidget, title.id)
    return titleFromHistoryWidget


def start_loading_poster(posterLabel: TitleFromHistoryWidget, title_id: int) -> None:
    """
    Асинхронно запускает загрузку постера.
    :param posterLabel: Контейнер постера.
    :param title_id: ID аниме.
    """
    asyncio.ensure_future(load_poster(posterLabel, title_id))
    logger.opt(colors=True).trace(
        f"Poster of title <y>{title_id}</y> "
        f"for QLabel <y>{id(posterLabel)}</y> loading started"
    )


async def load_poster(posterLabel: TitleFromHistoryWidget, title_id: int) -> None:
    """
    Загружает постер.
    :param posterLabel: Контейнер постера.
    :param title_id: ID аниме.
    """
    try:
        title: Title = await anilibria_agent.get_title(title_id)
    except AnilibriaAgentException as err:
        return logger.opt(colors=True).error(
            f"Title <y>{title_id}</y> getting failed. "
            f"<r>{type(err).__name__}: {err}</r>"
        )

    poster_url = (
        title.posters.original or title.posters.medium or title.posters.small
    ).url
    if not poster_url:
        return logger.opt(colors=True).debug(f"Title <y>{title_id}</y> haven't poster")

    try:
        poster = QPixmap()
        poster.loadFromData(await anilibria_agent.download_resource(poster_url))
        poster = rounded_image(poster, 4)
    except AnilibriaAgentException as err:
        return logger.opt(colors=True).error(
            f"Poster for QLabel <y>{id(posterLabel)}</y> loading failed. "
            f"<r>{type(err).__name__}: {err}</r> (<e>poster</e>=<y>{poster_url}</y>)"
        )

    # Виджет может быть удален до завершения скачивания
    try:
        posterLabel.installPixmap(poster)
        logger.opt(colors=True).trace(
            f"Poster for QLabel <y>{id(posterLabel)}</y> has been loaded."
        )
    except RuntimeError:
        logger.opt(colors=True).trace(f"QLabel <y>{id(posterLabel)}</y> is deleted")


def historyContainerResizeEvent(main_window: MainWindow, _: QtGui.QResizeEvent) -> None:
    if main_window.stackedWidget.currentWidget() != main_window.homePage:
        return

    container = main_window.historyContainer
    history = main_window.__getattribute__("history")
    if not history:
        return

    items_per_line = 4
    k = container.width() / TitleFromHistoryWidget.maxWidth
    # Уменьшаем максимальное растяжение при 4х элементах (почти как в анилибриксе)
    if k > 3.3:
        # На 2 больше за каждые 2 доступных места
        # (4;6) => 6  [6;8) => 8  [8;10) => 10 ...
        items_per_line = int(k) - int(k) % 2 + 2

    old_items_per_line = container.__getattribute__("items_per_line")
    if old_items_per_line == items_per_line:
        if len(history) < 4:
            avWidth = container.width() // items_per_line
            for item in container.children():
                if item.isWidgetType():
                    item.setMaximumWidth(avWidth)
        return

    logger.opt(colors=True).trace(f"Updating history container grid")
    container.__setattr__("items_per_line", items_per_line)

    if old_items_per_line > items_per_line:
        for i in range(items_per_line, old_items_per_line + 1):
            main_window.historyContainerLayout.setColumnStretch(i, 0)
    else:
        for i in range(old_items_per_line, items_per_line):
            main_window.historyContainerLayout.setColumnStretch(i, 1)

    clearHistoryContainer(main_window)
    fillHistoryContainer(main_window)

    logger.opt(colors=True).debug(
        f"History container grid updated: <y>{items_per_line}</y>"
    )


async def openPlayerPage(main_window: MainWindow, title_data: TitleFromHistory) -> None:
    try:
        title: Title = await anilibria_agent.get_title(title_data.id)
    except AnilibriaAgentException as err:
        main_window.stackedWidget.setCurrentWidget(main_window.homePage)
        return logger.opt(colors=True).error(
            f"Title <y>{title_data.id}</y> getting failed. "
            f"<r>{type(err).__name__}: {err}</r>"
        )
    main_window.openPlayerPage(
        title, min(title_data.episodes_count, title_data.last_watched_episode + 1)
    )


def titleWidgetMouseEvent(
    main_window: MainWindow, title_data: TitleFromHistory, event: QtGui.QMouseEvent
) -> None:
    if event.button() == Qt.MouseButton.LeftButton:
        main_window.stackedWidget.setCurrentWidget(main_window.playerPage)
        asyncio.ensure_future(openPlayerPage(main_window, title_data))

    logger.trace("titleWidgetMouseEvent handled")


def scrollBarValueChanged(main_window: MainWindow, value: int) -> None:
    scrollBar = main_window.scrollArea.verticalScrollBar()
    if value == scrollBar.minimum():
        main_window.historyContainer.__setattr__("displayed_lines", 2)
        clearHistoryContainer(main_window)
        fillHistoryContainer(main_window)
    elif value == scrollBar.maximum():
        main_window.historyContainer.__setattr__(
            "displayed_lines",
            main_window.historyContainer.__getattribute__("displayed_lines") + 1,
        )
        clearHistoryContainer(main_window)
        fillHistoryContainer(main_window)
        scrollBar.scroll(0, scrollBar.singleStep() * 2)


def scrollBarRangeChanged(main_window: MainWindow, minimum: int, maximum: int) -> None:
    items = main_window.__getattribute__("items")
    if items and minimum == maximum:
        items = len(items)
        items_per_line = main_window.historyContainer.__getattribute__("items_per_line")
        max_displayed_lines = items // items_per_line + bool(items % items_per_line)
        displayed_lines = main_window.historyContainer.__getattribute__(
            "displayed_lines"
        )
        if displayed_lines < max_displayed_lines:
            displayed_lines += 1
            main_window.historyContainer.__setattr__("displayed_lines", displayed_lines)
            clearHistoryContainer(main_window)
            fillHistoryContainer(main_window)
