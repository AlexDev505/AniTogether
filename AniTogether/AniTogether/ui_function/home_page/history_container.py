"""

Функционал раздела "История"

"""

from __future__ import annotations

import asyncio
import os
import typing as ty
from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel
from loguru import logger
from qasync import asyncSlot

from anilibria_agent import AnilibriaAgent, AnilibriaAgentException
from history import HistoryManager, TitleFromHistory
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
    main_window.__setattr__("originalResizeEvent" + __name__, main_window.resizeEvent)
    main_window.resizeEvent = partial(resizeEvent, main_window)
    main_window.__setattr__("history", None)
    main_window.__setattr__("items", None)
    prepareHistoryContainer(main_window)


@asyncSlot()
async def loadHistory(main_window: MainWindow) -> None:
    """
    Загружаем историю просмотра.
    """
    # Если история уже загружена
    if main_window.historyContainer.__getattribute__("filled"):
        return

    logger.debug("Loading history")

    history = await history_manager.load()
    main_window.__setattr__("history", history)

    if len(history) == 0:
        main_window.historyIsEmptyLabel.show()
        main_window.historyContainer.hide()
        logger.debug("History is empty")
    else:
        main_window.historyIsEmptyLabel.hide()
        main_window.historyContainer.show()

        # Создаем виджеты релизов
        items = []
        for i, title in enumerate(history):
            items.append(initTitleFromHistoryWidget(main_window, title))
        main_window.__setattr__("items", items)
        logger.opt(colors=True).debug(
            f"<y>{len(items)}</y> initTitleFromHistoryWidget's created"
        )

        fillHistoryContainer(main_window)


async def updateHistory(
    main_window: MainWindow,
    title_id: int,
    episodes_count: int,
    last_watched_episode: int,
) -> None:
    """
    Обновляет релиз в истории.
    :param main_window:
    :param title_id: ID релиза.
    :param episodes_count: Кол-во эпизодов.
    :param last_watched_episode: Последний просмотренный эпизод.
    :return:
    """
    history: list[TitleFromHistory] = main_window.__getattribute__("history")
    title = TitleFromHistory(title_id, episodes_count, last_watched_episode)
    if history and history[0].id == title_id:  # Если релиз на первом месте в истории
        history[0] = title
        await history_manager.save(history)
        item: TitleFromHistoryWidget = main_window.historyContainer.findChild(
            QLabel, "TitleFromHistory"
        )
        item.updateData(title)
    else:
        await _updateHistory(main_window, title)


async def _updateHistory(main_window: MainWindow, title: TitleFromHistory) -> None:
    """
    Добавляет или обновляет релиз в истории.
    :param main_window:
    :param title: Данные релиза.
    """
    history: list[TitleFromHistory] = main_window.__getattribute__("history")
    exists = False  # Релиз уже существует в истории
    for title_from_history in history:
        if title_from_history.id == title.id:
            exists = True
            history.remove(title_from_history)
            break
    history.insert(0, title)  # Помещаем не первое место
    await history_manager.save(history)

    items = main_window.__getattribute__("items")
    if exists:
        # Поднимаем виджет на первое место
        for item in items:
            if item.title.id == title.id:
                item.updateData(title)
                items.remove(item)
                items.insert(0, item)
        logger.opt(colors=True).debug(f"Release <y>{title.id}</y> moved up in history")
    else:
        # Создаем виджет
        items.insert(0, initTitleFromHistoryWidget(main_window, title))
        logger.opt(colors=True).debug(f"Release <y>{title.id}</y> added to history")
        if len(items) <= 4:
            # Обновляем ограничения размера виджетов
            for item in items:
                item.setMaximumWidth(item.maxWidth)

    clearHistoryContainer(main_window)
    fillHistoryContainer(main_window)


def prepareHistoryContainer(main_window: MainWindow) -> None:
    """
    Подготавливает контейнер истории просмотров.
    """
    main_window.historyContainer.resizeEvent = partial(
        historyContainerResizeEvent, main_window
    )
    main_window.historyContainer.__setattr__("items_per_line", 4)
    main_window.historyContainer.__setattr__("displayed_lines", 2)
    main_window.historyContainer.__setattr__("filled", False)
    for i in range(4):
        main_window.historyContainerLayout.setColumnStretch(i, 1)


def clearHistoryContainer(main_window: MainWindow) -> None:
    """
    Очищает контейнер истории просмотров.
    """
    for i in range(main_window.historyContainerLayout.count() - 1, -1, -1):
        child = main_window.historyContainerLayout.itemAt(i).widget()  # noqa
        child.hide()
        main_window.historyContainerLayout.removeWidget(child)
    main_window.historyContainer.__setattr__("filled", False)
    logger.trace("History container cleared")


def fillHistoryContainer(main_window: MainWindow) -> None:
    """
    Заполняет контейнер истории просмотров.
    """
    items = main_window.__getattribute__("items")
    items_per_line = main_window.historyContainer.__getattribute__("items_per_line")
    displayed_lines = main_window.historyContainer.__getattribute__("displayed_lines")
    count_to_show = items_per_line * displayed_lines
    x = y = 0
    i = 0
    for i, item in enumerate(items):
        if i == count_to_show:
            i -= 1
            break
        item.show()
        main_window.historyContainerLayout.addWidget(item, y, x)
        x += 1
        if x == items_per_line:
            x = 0
            y += 1
    main_window.historyContainer.__setattr__("filled", True)
    logger.opt(colors=True).debug(
        f"History container filled with <y>{i + 1}</y> elements"
    )


def initTitleFromHistoryWidget(
    main_window: MainWindow, title: TitleFromHistory
) -> TitleFromHistoryWidget:
    """
    Создает виджет релиза для контейнера истории просмотра.
    :param main_window:
    :param title:
    :return:
    """
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
    :param title_id: ID релиза.
    """
    asyncio.ensure_future(load_poster(posterLabel, title_id))


async def load_poster(posterLabel: TitleFromHistoryWidget, title_id: int) -> None:
    """
    Загружает постер.
    :param posterLabel: Контейнер постера.
    :param title_id: ID релиза.
    """
    logger.opt(colors=True).trace(
        f"Poster of title <y>{title_id}</y> "
        f"for QLabel <y>{id(posterLabel)}</y> loading started"
    )

    # Получаем данные о релизе
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
        posterLabel.installPoster(poster)
        logger.opt(colors=True).trace(
            f"Poster for QLabel <y>{id(posterLabel)}</y> has been loaded."
        )
    except RuntimeError:
        logger.opt(colors=True).trace(f"QLabel <y>{id(posterLabel)}</y> is deleted")


async def openPlayerPage(main_window: MainWindow, title_data: TitleFromHistory) -> None:
    """
    Получает полные данные о релизе и переходит на страницу плеера
    :param main_window:
    :param title_data:
    :return:
    """
    logger.opt(colors=True).trace(f"Release <y>{title_data.id}</y> loading started")

    try:
        title: Title = await anilibria_agent.get_title(title_data.id)
    except AnilibriaAgentException as err:
        # Возврат на главную страницу
        main_window.stackedWidget.setCurrentWidget(main_window.homePage)
        return logger.opt(colors=True).error(
            f"Title <y>{title_data.id}</y> getting failed. "
            f"<r>{type(err).__name__}: {err}</r>"
        )
    main_window.openPlayerPage(
        title, min(title_data.episodes_count, title_data.last_watched_episode + 1)
    )


def resizeEvent(main_window: MainWindow, event: QtGui.QResizeEvent) -> None:
    """
    Событие изменения размера главного окна.
    """
    main_window.scrollAreaContainer.setMaximumWidth(main_window.width())
    main_window.__getattribute__("originalResizeEvent" + __name__)(event)


def historyContainerResizeEvent(main_window: MainWindow, _: QtGui.QResizeEvent) -> None:
    """
    Событие изменения размера контейнера истории просомтров.
    """
    if main_window.stackedWidget.currentWidget() != main_window.homePage:
        return

    container = main_window.historyContainer
    history = main_window.__getattribute__("history")
    if not history:
        return

    items_per_line = 4
    # Сколько виджетов войдет в линию при максимальном размере
    k = container.width() / TitleFromHistoryWidget.maxWidth
    # Уменьшаем максимальное растяжение при 4х элементах (почти как в анилибриксе)
    if k > 3.3:
        # На 2 больше за каждые 2 доступных места
        # (4;6) => 6  [6;8) => 8  [8;10) => 10 ...
        items_per_line = int(k) - int(k) % 2 + 2

    old_items_per_line = container.__getattribute__("items_per_line")
    if old_items_per_line == items_per_line:
        if len(history) < 4:
            # Ограничиваем максимальный размер элементов
            avWidth = container.width() // items_per_line
            for item in container.children():
                if item.isWidgetType():
                    item.setMaximumWidth(avWidth)
        return

    logger.opt(colors=True).trace(f"Updating history container grid")
    container.__setattr__("items_per_line", items_per_line)

    # Указываем QGridLayout кол-во столбцов
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


def titleWidgetMouseEvent(
    main_window: MainWindow, title_data: TitleFromHistory, event: QtGui.QMouseEvent
) -> None:
    """
    Событие нажатия на виджет релиза.
    :param main_window:
    :param title_data: Данные релиза.
    :param event:
    """
    if event.button() == Qt.MouseButton.LeftButton:
        # Переходим на страницу плеера
        main_window.stackedWidget.setCurrentWidget(main_window.playerPage)
        # Запускаем получение полных данных о релизе
        asyncio.ensure_future(openPlayerPage(main_window, title_data))

    logger.trace("titleWidgetMouseEvent handled")


def scrollBarValueChanged(main_window: MainWindow, value: int) -> None:
    """
    Событие прокрутки главной страницы
    :param main_window:
    :param value: Новое значение полосы прокрутки.
    """
    scrollBar = main_window.scrollArea.verticalScrollBar()
    if value == scrollBar.maximum():  # Конец страницы
        # Увеличиваем кол-во отображаемых строк
        displayed_lines = (
            main_window.historyContainer.__getattribute__("displayed_lines") + 1
        )
        main_window.historyContainer.__setattr__(
            "displayed_lines",
            displayed_lines,
        )
        clearHistoryContainer(main_window)
        fillHistoryContainer(main_window)
        scrollBar.scroll(0, scrollBar.singleStep() * 2)
        logger.opt(colors=True).trace(
            f"displayed_lines changed: <y>{displayed_lines}</y>"
        )
    elif value == scrollBar.minimum():  # Начало страницы
        # Возвращаем исходное ко-во отображаемых строк
        main_window.historyContainer.__setattr__("displayed_lines", 2)
        clearHistoryContainer(main_window)
        fillHistoryContainer(main_window)
        logger.opt(colors=True).trace(f"displayed_lines changed: <y>2</y>")


def scrollBarRangeChanged(main_window: MainWindow, minimum: int, maximum: int) -> None:
    """
    Событие изменения диапазона прокрутки главной страницы.
    (Возможно при изменении высоты окна)
    :param main_window:
    :param minimum: Минимальное значение.
    :param maximum: Максимальное значение.
    """
    items = main_window.__getattribute__("items")
    if items and minimum == maximum:  # Нельзя прокручивать страницу
        # Увеличиваем кол-во отображаемых страниц
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
            logger.opt(colors=True).trace(
                f"displayed_lines changed: <y>{displayed_lines}</y>"
            )
