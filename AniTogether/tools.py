from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPixmap, QImage, QBrush, QPainter, QWindow


def circle_image(image: QPixmap, size: int) -> QPixmap:
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
