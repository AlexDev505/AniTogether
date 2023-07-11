from __future__ import annotations

import asyncio
import typing as ty
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
    """
    Закрывает сессии агента анилибрии.
    """
    logger.debug("Disconnecting Anilibria agent")
    await anilibria_agent.disconnect()


@alru_cache(maxsize=10, ttl=10)
async def search_titles(
    query: str,
    searchLineEdit: QLineEdit,  # noqa
) -> list[Title]:
    """
    Выполняет поиск релизов по запросу.
    Использует кэширование: хранит последние 10 запросов в течение 10 секунд.
    :param query: Запрос.
    :param searchLineEdit: Строка поиска.
    :return: Список найденных релизов.
    """
    logger.opt(colors=True).debug(f"Search request <e>query</e>=<y>{query}</y>")

    global last_search_use
    current_time = time()
    if current_time - last_search_use < 1:
        logger.trace("Request limit exceeded. Waiting...")
        await asyncio.sleep(1)
        if query != searchLineEdit.text():
            raise SearchQueryUpdated()
    last_search_use = current_time

    titles = await anilibria_agent.search_titles(search=query, items_per_page=10)
    logger.opt(colors=True).debug(
        f"<y>{len(titles.list)}</y> titles found by request <y>{query}</y>"
    )
    logger.trace(str([title.names.ru for title in titles.list]))
    return titles.list


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
        poster: QPixmap = await download_poster(poster_url)
        poster = circle_image(poster, size)  # Помещаем в круг
        # Виджет может быть удален до завершения скачивания
        try:
            posterLabel.setPixmap(poster)
            logger.opt(colors=True).trace(
                f"Poster for QLabel <y>{id(posterLabel)}</y> has been loaded."
            )
        except RuntimeError:
            logger.opt(colors=True).trace(f"QLabel <y>{id(posterLabel)}</y> is deleted")
    except AnilibriaAgentException as err:
        logger.opt(colors=True).error(
            f"Poster for QLabel <y>{id(posterLabel)}</y> loading failed. "
            f"<r>{type(err).__name__}: {err}</r> (<e>poster</e>=<y>{poster_url}</y>)"
        )


@alru_cache(maxsize=30, ttl=120)
async def download_poster(poster_url: str) -> QPixmap:
    """
    Скачивает постер.
    Использует кэширование: хранит 30 последних постеров в течение 2 минут.
    :param poster_url: Ссылка на постер.
    :return: Экземпляр QPixmap.
    """
    logger.opt(colors=True).trace(f"Downloading poster: <y>{poster_url}</y>")
    poster = await anilibria_agent.download_poster(poster_url)
    pixmap = QPixmap()
    pixmap.loadFromData(poster)
    return pixmap


__all__ = ["disconnect", "search_titles", "start_loading_poster"]
