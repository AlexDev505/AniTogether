from __future__ import annotations

import re
import typing as ty

from aiohttp import ClientSession
from anilibria import AniLibriaClient, HTTPException
from async_lru import alru_cache
from loguru import logger

from .exceptions import (
    AnilibriaAgentException,
    CantFindAnilibriaMirror,
    ResourceDownloadingFailed,
)


if ty.TYPE_CHECKING:
    from anilibria import Title


class AnilibriaAgent(AniLibriaClient):
    """
    Агент для взаимодействия с анилибрией.
    """

    _instance: AnilibriaAgent | None = None

    def __init__(self):
        super().__init__()

        self.session: ClientSession = ...
        # URl на зеркало анилибрии
        self.anilibria_mirror: str | None = None

    @alru_cache(maxsize=10, ttl=10)
    async def get_title(self, title_id: int) -> Title:
        try:
            return await super().get_title(id=title_id)
        except HTTPException as err:
            err_data = re.fullmatch(
                r"HTTP error with code: (\d+)!\nMessage: (.+)",
                str(err),
                flags=re.MULTILINE,
            )
            if err_data:
                raise AnilibriaAgentException(int(err_data.group(1)), err_data.group(2))
            raise AnilibriaAgentException(0, str(err))

    @alru_cache(maxsize=10, ttl=10)
    async def search_titles(self, query: str) -> list[Title]:
        """
        Выполняет поиск релизов по запросу.
        Использует кэширование: хранит последние 10 запросов в течение 10 секунд.
        :param query: Запрос.
        :return: Список найденных релизов.
        """
        titles = await super().search_titles(search=query, items_per_page=10)
        logger.opt(colors=True).debug(
            f"<y>{len(titles.list)}</y> titles found by request <y>{query}</y>"
        )
        logger.trace(str([title.names.ru for title in titles.list]))
        return titles.list

    async def create_session(self) -> ClientSession:
        if self.session is ... or self.session.closed:
            self.session = ClientSession()

        return self.session

    async def find_anilibria_mirror(self) -> str:
        """
        Ищет доступное зеркало анилибрии.
        Парсинг с darklibria.it
        :return: URL.
        """
        await self.create_session()

        async with self.session.get(
            "https://darklibria.it/redirect/mirror/1"
        ) as response:
            if response.status == 200:
                data = await response.text()
                if match := re.search(r'<link rel="canonical" href="(.+)"/>', data):
                    self.anilibria_mirror = match.group(1)
                    return self.anilibria_mirror
                raise CantFindAnilibriaMirror(response.status, "Mirror link not found")
            raise CantFindAnilibriaMirror(response.status, "")

    @alru_cache(maxsize=30, ttl=120)
    async def download_resource(self, url: str) -> bytes:
        """
        Скачивает файл с сервера анилибрии.
        Использует кэширование: хранит 30 последних запросов в течение 2 минут.
        :param url: Ссылка на файл.
        :return: Постер в виде bytes.
        """
        logger.opt(colors=True).trace(f"Downloading resource: <y>{url}</y>")
        if not self.anilibria_mirror:
            await self.find_anilibria_mirror()

        async with self.session.get(self.anilibria_mirror + url) as response:
            if response.status == 200:
                data = await response.read()
                return data
            raise ResourceDownloadingFailed(response.status, "")

    @classmethod
    async def disconnect(cls) -> None:
        if cls._instance:
            logger.debug("Disconnecting anilibria agent")
            await cls._instance.close()
            logger.debug("Anilibria WS and original HTTPS disconnected")
            if cls._instance.session is not ...:
                await cls._instance.session.close()
                logger.debug("Anilibria mirror HTTPS disconnected")

    @classmethod
    def get(cls) -> AnilibriaAgent:
        if not cls._instance:
            cls._instance = AnilibriaAgent()
        return cls._instance


__all__ = ["AnilibriaAgent"]
