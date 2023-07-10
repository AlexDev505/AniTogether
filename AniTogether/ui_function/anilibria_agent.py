from __future__ import annotations

import asyncio
import typing as ty
from time import time

from async_lru import alru_cache

from anilibria_agent import AnilibriaAgent
from logger import logger


if ty.TYPE_CHECKING:
    from anilibria import Title
    from PyQt6.QtWidgets import QLineEdit

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


__all__ = ["disconnect", "search_titles"]
