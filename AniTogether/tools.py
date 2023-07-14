"""

Функции, которые используются в различных модулях приложения.

"""

from __future__ import annotations

import typing as ty
from functools import lru_cache

import attrs
from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QPixmap, QImage, QBrush, QPainter, QWindow, QMovie, QColor

from logger import logger


if ty.TYPE_CHECKING:
    from anilibria import Title


def circle_image(image: QPixmap, size: int) -> QPixmap:
    """
    Вписывает картинку в круг.
    :param image: Исходное изображение.
    :param size: Размер выходного изображения(квадрат).
    :return: Экземпляр QPixmap
    """
    image = QImage(image)
    image.convertedTo(QImage.Format.Format_ARGB32)

    img_size = min(image.width(), image.height())
    rect = QRect(
        (image.width() - img_size) // 2,
        (image.height() - img_size) // 2,
        img_size,
        img_size,
    )

    image = image.copy(rect)

    mask_img = QImage(img_size, img_size, QImage.Format.Format_ARGB32)
    mask_img.fill(Qt.GlobalColor.transparent)

    brush = QBrush(image)
    painter = QPainter(mask_img)
    painter.setBrush(brush)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(0, 0, img_size, img_size)
    painter.end()

    pixel_ratio = QWindow().devicePixelRatio()
    pixmap = QPixmap.fromImage(mask_img)
    pixmap.setDevicePixelRatio(pixel_ratio)
    size = int(size * pixel_ratio)
    pixmap = pixmap.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )

    return pixmap


def rounded_image(image: QPixmap, radius: int) -> QPixmap:
    """
    Скругляет углы картинки.
    :param image: Исходное изображение.
    :param radius: Радиус скругления.
    :return: Экземпляр QPixmap
    """
    rounded = QPixmap(image.size())
    rounded.fill(QColor("transparent"))
    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QBrush(image))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(image.rect(), radius, radius)
    return rounded


@lru_cache(maxsize=10)
def create_loading_movie(size: int) -> QMovie:
    """
    Создает экземпляр анимации загрузки.
    :param size: Размер анимации(квадрат).
    :return: Экземпляр QMovie.
    """
    movie = QMovie(":/base/loading.gif")
    movie.setScaledSize(QSize(size, size))
    movie.start()

    logger.opt(colors=True).trace(f"Loading animation size <y>{size}</y> created")

    return movie


def pretty_view(data: ty.Union[dict, list], _indent=0) -> str:
    """
    Преобразует `data` в более удобный для восприятия вид.
    """

    def adapt_value(obj: ty.Any) -> ty.Any:
        if isinstance(obj, (int, float, bool, dict)) or obj is None:
            return obj
        elif obj.__repr__().startswith("{"):
            return obj.__dict__
        elif obj.__repr__().startswith("["):
            return list(obj)
        else:
            return str(obj)

    def tag(t: str, content: ty.Any) -> str:
        return f"<{t}>{content}</{t}>"

    def dict_(content: dict) -> ty.List[str]:
        values = []
        for k, v in content.items():
            k = tag("le", f'"{k}"' if isinstance(k, str) else k)
            v = adapt_value(v)
            if isinstance(v, str):
                v = tag("y", '"%s"' % v.replace("\n", "\\n"))
            elif isinstance(v, (dict, list)):
                v = pretty_view(v, _indent=_indent + 1)
            else:
                v = tag("lc", v)
            values.append(f"{k}: {v}")
        return values

    def list_(content: list) -> ty.List[str]:
        items = []
        for item in content:
            item = adapt_value(item)
            if isinstance(item, str):
                items.append(tag("y", f'"{item}"'))
            elif isinstance(item, (dict, list)):
                items.append(pretty_view(item, _indent=_indent + 1))
            else:
                items.append(tag("lc", item))
        return items

    result = ""

    if isinstance(data, dict):
        if len(data) > 2 or not all(
            isinstance(x, (str, int, float, bool)) or x is None for x in data.values()
        ):
            result = (
                "{\n"
                + "    " * (_indent + 1)
                + f",\n{'    ' * (_indent + 1)}".join(dict_(data))
                + "\n"
                + "    " * _indent
                + "}"
            )
        else:
            result = "{" + ", ".join(dict_(data)) + "}"

    elif isinstance(data, list):
        if len(data) > 15 or not all(
            isinstance(x, (str, int, float, bool)) for x in data
        ):
            result = (
                "[\n"
                + "    " * (_indent + 1)
                + f",\n{'    ' * (_indent + 1)}".join(list_(data))
                + "\n"
                + "    " * _indent
                + "]"
            )
        else:
            result = "[" + ", ".join(list_(data)) + "]"

    return tag("w", result)


def debug_title_data(title: Title) -> str:
    """
    Преобразует экземпляр релиза в читаемый формат для DEBUG записи.
    :param title: Экземпляр релиза.
    :return: Строка.
    """
    return pretty_view(
        dict(
            name=title.names.ru,
            type=title.type.string,
            episodes_count=title.type.episodes,
        )
    )


def asdict(obj) -> dict | list:
    """
    Преобразует attrs класс в словарь.
    """
    if isinstance(obj, list):
        return [asdict(x) for x in obj]
    elif isinstance(obj, dict):
        return {k: asdict(obj[k]) for k in obj}

    if hasattr(obj.__class__, "__attrs_attrs__"):
        attrs_attrs: tuple[attrs.Attribute] = obj.__class__.__attrs_attrs__
        return {
            attr.name: asdict(obj.__getattribute__(attr.name)) for attr in attrs_attrs
        }
    return obj


def trace_title_data(title: Title) -> str:
    """
    Преобразует экземпляр релиза в читаемый формат для TRACE записи.
    :param title: Экземпляр релиза.
    :return: Строка.
    """
    return pretty_view(asdict(title))
