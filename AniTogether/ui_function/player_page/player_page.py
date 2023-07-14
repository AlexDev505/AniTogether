"""

Функционал страницы плеера.

"""

from __future__ import annotations

import asyncio
import typing as ty

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from loguru import logger
from qasync import asyncSlot

from anilibria_agent import AnilibriaAgent, AnilibriaAgentException
from tools import debug_title_data, trace_title_data
from ui_function.home_page.history_container import updateHistory
from . import player_controls


if ty.TYPE_CHECKING:
    from anilibria import Title
    from PyQt6 import QtWidgets
    from main_window import MainWindow


anilibria_agent = AnilibriaAgent.get()


def setupUiFunctions(main_window: MainWindow) -> None:
    main_window.__setattr__("current_title", None)
    main_window.__setattr__("current_episode_number", None)
    main_window.__setattr__("current_episode", None)
    main_window.__setattr__("episodes_count", None)
    # main_window.playerPageIsOpen.connect(partial(playerPageIsOpen, main_window))
    player_controls.setupUiFunctions(main_window)


def openPlayerPage(main_window: MainWindow, title: Title, episode_number: int) -> None:
    """
    Открывает страницу плеера и отображает данные о релизе.
    :param main_window:
    :param title: Релиз.
    :param episode_number: Номер отображаемого эпизода.
    """
    logger.debug("Opening the player page")
    logger.opt(colors=True).debug(debug_title_data(title))
    logger.opt(colors=True).trace(trace_title_data(title))

    main_window.__setattr__("current_title", title)
    main_window.__setattr__("current_episode_number", episode_number)
    episodes = title.player.list
    # Серии могут храниться в списке или в словаре
    current_episode = (
        episodes[episode_number - 1]
        if isinstance(episodes, list)
        else episodes[str(episode_number)]
    )
    main_window.__setattr__("current_episode", current_episode)
    # title.type.episodes может быть None
    episodes_count = title.type.episodes or len(title.player.list)
    main_window.__setattr__("episodes_count", episodes_count)

    # Отображаем виджет управляющий плеером
    player_controls.show(main_window, title, episode_number)

    main_window.stackedWidget.setCurrentWidget(main_window.playerPage)
    main_window.playerPageIsOpen.emit()

    # Запуск обновления истории просмотров
    asyncio.ensure_future(
        updateHistory(main_window, title.id, episodes_count, episode_number - 1)
    )

    if current_episode.preview:
        # Запуск загрузки превью эпизода
        asyncio.ensure_future(
            load_episode_preview(
                main_window.previewLabel,
                current_episode.preview,
                episode_number,
            )
        )

    logger.debug("Player page is open")


@asyncSlot()
async def playerPageIsOpen(main_window: MainWindow) -> None:
    ...


async def load_episode_preview(
    previewLabel: QtWidgets.QLabel, url: str, episode_number: int
) -> None:
    """
    Загружает превью эпизода.
    :param previewLabel: Контейнер для превью.
    :param url: Ссылка на превью.
    :param episode_number: Номер эпизода.
    """
    logger.opt(colors=True).trace(
        f"Preview for episode <y>{episode_number}</y> loading started"
    )

    try:
        preview = QPixmap()
        # Скачивание превью
        preview.loadFromData(await anilibria_agent.download_resource(url))
    except AnilibriaAgentException as err:
        return logger.opt(colors=True).error(
            f"Preview for episode <y>{episode_number}</y> loading failed. "
            f"<r>{type(err).__name__}: {err}</r> (<e>preview</e>=<y>{url}</y>)"
        )

    preview = preview.scaled(
        previewLabel.parent().size(),
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    previewLabel.setPixmap(preview)

    logger.opt(colors=True).trace(
        f"Preview for episode <y>{episode_number}</y> has been loaded."
    )
