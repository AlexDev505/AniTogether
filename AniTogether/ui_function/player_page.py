from __future__ import annotations

import asyncio
import typing as ty

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from qasync import asyncSlot

from anilibria_agent import AnilibriaAgent, AnilibriaAgentException
from logger import logger


if ty.TYPE_CHECKING:
    from PyQt6 import QtWidgets
    from main_window import MainWindow


anilibria_agent = AnilibriaAgent.get()


@asyncSlot()
async def playerPageIsOpen(main_window: MainWindow) -> None:
    if main_window.current_episode.preview:
        asyncio.ensure_future(
            load_episode_preview(
                main_window.previewLabel,
                main_window.current_episode.preview,
                main_window.current_episode_number,
            )
        )
        logger.opt(colors=True).trace(
            f"Preview for episode <y>{main_window.current_episode_number}</y> "
            "loading started"
        )


async def load_episode_preview(
    previewLabel: QtWidgets.QLabel, url: str, episode_number: int
) -> None:
    try:
        preview = QPixmap()
        preview.loadFromData(await anilibria_agent.download_resource(url))
    except AnilibriaAgentException as err:
        return logger.opt(colors=True).error(
            f"Preview for episode <y>{episode_number}</y> loading failed. "
            f"<r>{type(err).__name__}: {err}</r> (<e>preview</e>=<y>{url}</y>)"
        )

    preview = preview.scaled(
        previewLabel.parent().size(), Qt.AspectRatioMode.KeepAspectRatio
    )
    previewLabel.setPixmap(preview)
    logger.opt(colors=True).trace(
        f"Preview for episode <y>{episode_number}</y> has been loaded."
    )


def toggleFullScreen(main_window: MainWindow) -> None:
    if main_window.topFrame.isHidden():
        main_window.topFrame.show()
        if not main_window.__getattribute__("__was_fullscreen"):
            main_window.maximizeAppBtn.click()
    else:
        main_window.topFrame.hide()
        if main_window.isFullScreen():
            main_window.__setattr__("__was_fullscreen", True)
        else:
            main_window.maximizeAppBtn.click()
            main_window.__setattr__("__was_fullscreen", False)


def leavePlayerPage(main_window: MainWindow) -> None:
    main_window.current_title = None
    main_window.current_episode_number = 0
    main_window.current_episode = None
    main_window.playerControlsWidget.hide()
    main_window.openHomePage()
