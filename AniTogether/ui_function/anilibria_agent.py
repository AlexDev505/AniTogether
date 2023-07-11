from __future__ import annotations

import asyncio
import typing as ty
from contextlib import suppress
from time import time

from PyQt6.QtGui import QPixmap
from async_lru import alru_cache

from anilibria_agent import AnilibriaAgent, AnilibriaAgentException
from logger import logger
from tools import circle_image


if ty.TYPE_CHECKING:
    from anilibria import Title
    from PyQt6.QtWidgets import QLineEdit, QLabel

anilibria_agent = AnilibriaAgent()
last_search_use: float = 0


class SearchQueryUpdated(Exception):
    pass


async def disconnect() -> None:
    logger.debug("Disconnecting Anilibria agent")
    await anilibria_agent.close()


@alru_cache(maxsize=10, ttl=10)
async def search_titles(
    query: str,
    searchLineEdit: QLineEdit,  # noqa
) -> list[Title]:
    global last_search_use
    current_time = time()
    if current_time - last_search_use < 1:
        await asyncio.sleep(1)
        if query != searchLineEdit.text():
            raise SearchQueryUpdated()
    last_search_use = current_time

    titles = await anilibria_agent.search_titles(search=query, items_per_page=10)
    logger.trace(str([title.names.ru for title in titles.list]))
    return titles.list


def start_loading_poster(
    posterLabel: QLabel,  # noqa
    size: tuple[int, int],
    poster_url: str,
) -> None:
    asyncio.ensure_future(load_poster(posterLabel, size, poster_url))


async def load_poster(
    posterLabel: QLabel,  # noqa
    size: int,
    poster_url: str,
) -> None:
    try:
        poster: QPixmap = await download_poster(poster_url)
        poster = circle_image(poster, size)
        with suppress(RuntimeError):  # Виджет может быть удален
            posterLabel.setPixmap(poster)
    except AnilibriaAgentException as err:
        logger.opt(colors=True).error(
            f"не удалось скачать постер <y>{poster_url}</y>: "
            f"<r>{type(err).__name__}: {err}</r>"
        )


@alru_cache(maxsize=30, ttl=120)
async def download_poster(poster_url: str) -> QPixmap:
    poster = await anilibria_agent.download_poster(poster_url)
    pixmap = QPixmap()
    pixmap.loadFromData(poster)
    return pixmap


__all__ = ["disconnect", "search_titles", "start_loading_poster"]
