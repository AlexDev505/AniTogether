from functools import lru_cache

from PyQt6.QtCore import Qt, QRect, QSize
from PyQt6.QtGui import QPixmap, QImage, QBrush, QPainter, QWindow, QMovie

from logger import logger


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
