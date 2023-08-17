"""

Модуль, обеспечивающий работу с сохраненной историей просмотра.

"""

import csv
import os
from dataclasses import dataclass


DELIMITER = ";"  # Разделитель данных
DATA_LIMIT = 24  # Лимит сохраненных релизов
FILE_PATH = os.environ["HISTORY_PATH"]


@dataclass
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


if not os.path.exists(FILE_PATH):
    with open(FILE_PATH, "w") as f:
        f.write(DELIMITER.join(TitleFromHistory.fields()))


def load() -> list[TitleFromHistory]:
    """
    Считывает данные из файла.
    :return: Список экземпляров TitleFromHistory.
    """
    result = []
    count = 0
    errors = False  # Были ли обнаружены некорректные записи
    headers_checked = False  # Были ли проверены заголовки

    with open(FILE_PATH, newline="") as af:
        row: dict
        for row in csv.DictReader(af, delimiter=DELIMITER):
            try:
                count += 1
                if count > DATA_LIMIT:
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
                _fix_headers()
                return load()  # Запускаем чтение заново

    if errors:
        # Перезаписываем файл, оставляя только корректные записи
        save(result)

    return result


def save(data: list[TitleFromHistory]) -> None:
    with open(FILE_PATH, "w", newline="") as af:
        writer = csv.DictWriter(af, TitleFromHistory.fields(), delimiter=DELIMITER)
        writer.writeheader()
        for line in data:
            writer.writerow(line.to_dict())


def update(
    title_id: int, *, last_watched_episode: int, episodes_count: int = 0
) -> None:
    history = load()

    try:
        item = next(filter(lambda item_: item_.id == title_id, history))
        history.remove(item)
        if not (item.last_watched_episode == 0 and last_watched_episode < 2):
            item.last_watched_episode = last_watched_episode
    except StopIteration:
        item = TitleFromHistory(title_id, episodes_count, 0)

    history.insert(0, item)
    save(history)


def remove(title_id: int) -> None:
    history = load()

    try:
        item = next(filter(lambda item_: item_.id == title_id, history))
        history.remove(item)
        save(history)
    except StopIteration:
        pass


def _fix_headers() -> None:
    """
    Перезаписывает заголовки.
    """
    # Считываем данные без их валидации
    with open(FILE_PATH, newline="") as af:
        data = [row for row in csv.reader(af, delimiter=DELIMITER)]
        data = data[1:]  # Исключаем строку заголовков
    with open(FILE_PATH, "w", newline="") as af:
        writer = csv.writer(af, delimiter=DELIMITER)
        # Записываем корректные заголовки
        writer.writerow(TitleFromHistory.fields())
        for line in data:
            writer.writerow(line)
