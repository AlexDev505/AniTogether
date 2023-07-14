"""

Модуль, обеспечивающий работу с сохраненной историей просмотра.

"""

import asyncio
import os
from dataclasses import dataclass

import aiocsv
import aiofiles


@dataclass()
class TitleFromHistory:
    """
    Модель, хранения данных о релизе в истории просмотра.
    """

    id: int
    episodes_count: int
    last_watched_episode: int

    @classmethod
    def fields(cls) -> list[str]:
        """
        :return: Поля, которые хранятся в истории.
        """
        return list(cls.__dict__.get("__dataclass_fields__").keys())

    def to_dict(self) -> dict[str, int]:
        """
        Преобразует модель в словарь.
        :return: Словарь {<название поля>: <значение>, ...}
        """
        return {k: self.__getattribute__(k) for k in self.fields()}


class HistoryManager:
    """
    Интерфейс взаимодействия с сохраненной историей.
    """

    DELIMITER = ";"  # Разделитель данных
    DATA_LIMIT = 24  # Лимит сохраненных релизов

    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                f.write(self.DELIMITER.join(TitleFromHistory.fields()))

    async def load(self) -> list[TitleFromHistory]:
        """
        Считывает данные из файла.
        :return: Список экземпляров TitleFromHistory.
        """
        result = []
        count = 0
        errors = False  # Были ли обнаружены некорректные записи
        headers_checked = False  # Были ли проверены заголовки

        async with aiofiles.open(self.file_path, newline="") as af:
            async for row in aiocsv.AsyncDictReader(af, delimiter=self.DELIMITER):
                try:
                    count += 1
                    if count > self.DATA_LIMIT:
                        errors = True
                        break

                    if not headers_checked:
                        if set(row.keys()) != set(TitleFromHistory.fields()):
                            raise KeyError()
                        headers_checked = True

                    title = TitleFromHistory(**{k: int(v) for k, v in row.items()})

                    result.append(title)
                except (ValueError, TypeError):  # Некорректные записи
                    errors = True
                except KeyError:  # Некорректные заголовки
                    await self._fix_headers()
                    return await self.load()  # Запускаем чтение заново

        if errors:
            # Перезаписываем файл, оставляя только корректные записи
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
        """
        Перезаписывает заголовки.
        """
        # Считываем данные без их валидации
        async with aiofiles.open(self.file_path, newline="") as af:
            data = [
                row async for row in aiocsv.AsyncReader(af, delimiter=self.DELIMITER)
            ]
            data = data[1:]  # Исключаем строку заголовков
        async with aiofiles.open(self.file_path, "w", newline="") as af:
            writer = aiocsv.AsyncWriter(af, delimiter=self.DELIMITER)
            # Записываем корректные заголовки
            await writer.writerow(TitleFromHistory.fields())
            for line in data:
                await writer.writerow(line)
