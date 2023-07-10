import re

from aiohttp import ClientSession
from anilibria import AniLibriaClient


class AnilibriaAgent(AniLibriaClient):
    def __init__(self):
        super().__init__()

        self.session: ClientSession = ...
        self.anilibria_mirror: str | None = None

    async def create_session(self) -> ClientSession:
        if self.session is ... or self.session.closed:
            self.session = ClientSession()

        return self.session

    async def find_anilibria_mirror(self) -> str:
        await self.create_session()

        async with self.session.get(
            "https://darklibria.it/redirect/mirror/1"
        ) as response:
            if response.status == 200:
                data = await response.text()
                if match := re.search(r'<link rel="canonical" href="(.+)"/>', data):
                    self.anilibria_mirror = match.group(1)
                    return self.anilibria_mirror
            raise RuntimeError("Не удалось получить зеркало анилибрии")

    async def download_poster(self, poster_url: str) -> bytes:
        if not self.anilibria_mirror:
            await self.find_anilibria_mirror()

        async with self.session.get(self.anilibria_mirror + poster_url) as response:
            if response.status == 200:
                data = await response.read()
                return data
            raise RuntimeError("Не удалось получить постер")


__all__ = ["AnilibriaAgent"]
