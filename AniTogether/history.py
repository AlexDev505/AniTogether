import asyncio
import os
from dataclasses import dataclass

import aiocsv
import aiofiles


@dataclass()
class TitleFromHistory:
    id: int
    episodes_count: int
    last_watched_episode: int

    @classmethod
    def fields(cls) -> list[str]:
        return list(cls.__dict__.get("__dataclass_fields__").keys())

    def to_dict(self) -> dict[str, int]:
        return {k: self.__getattribute__(k) for k in self.fields()}


class HistoryManager:
    DELIMITER = ";"

    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                f.write(self.DELIMITER.join(TitleFromHistory.fields()))

    async def load(self) -> list[TitleFromHistory]:
        result = []
        count = 0
        errors = False
        headers_checked = False
        async with aiofiles.open(self.file_path, newline="") as af:
            async for row in aiocsv.AsyncDictReader(af, delimiter=self.DELIMITER):
                try:
                    if not headers_checked:
                        if set(row.keys()) != set(TitleFromHistory.fields()):
                            raise RuntimeError()
                        headers_checked = True
                    title = TitleFromHistory(**{k: int(v) for k, v in row.items()})
                    count += 1
                    if count > 24:  # Считываем максимум 24 строки
                        errors = True
                        break
                    result.append(title)
                except (ValueError, TypeError) as err:
                    errors = True
                except RuntimeError:
                    await self._fix_headers()
                    return await self.load()
        if errors:
            asyncio.ensure_future(self.save(result))
        return result

    async def save(self, data: list[TitleFromHistory]) -> None:
        async with aiofiles.open(self.file_path, "w", newline="") as af:
            writer = aiocsv.AsyncDictWriter(
                af, TitleFromHistory.fields(), delimiter=self.DELIMITER
            )
            await writer.writeheader()
            for line in data:
                await writer.writerow(line.to_dict())

    async def _fix_headers(self) -> None:
        async with aiofiles.open(self.file_path, newline="") as af:
            data = [
                row async for row in aiocsv.AsyncReader(af, delimiter=self.DELIMITER)
            ][1:]
        async with aiofiles.open(self.file_path, "w", newline="") as af:
            writer = aiocsv.AsyncWriter(af, delimiter=self.DELIMITER)
            await writer.writerow(TitleFromHistory.fields())
            fields_count = len(TitleFromHistory.fields())
            for line in data:
                if len(line) == fields_count:
                    await writer.writerow(line)
