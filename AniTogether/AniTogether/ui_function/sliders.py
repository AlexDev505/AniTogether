"""

Модификации QSlider.

"""

from __future__ import annotations

import typing as ty
from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QStyle


if ty.TYPE_CHECKING:
    from PyQt6.QtGui import QMouseEvent
    from PyQt6.QtWidgets import QSlider


def prepareSlider(slider: QSlider) -> None:
    """
    Изменение функциональности QSlider.
    :param slider: Экземпляр QSlider.
    """
    slider.pressed = False
    slider.mousePressEvent = partial(mousePressEvent, slider)
    slider.mouseMoveEvent = partial(mouseMoveEvent, slider)
    slider.mouseReleaseEvent = partial(mouseReleaseEvent, slider)


def mousePressEvent(slider: QSlider, event: QMouseEvent) -> None:
    """
    Обрабатывает нажатие на слайдер.
    Реализует мгновенное изменения значения, при нажатии.
    :param slider: Отправитель события.
    :param event:
    """
    if event.button() == Qt.MouseButton.LeftButton:
        slider.pressed = True
        slider.setValue(
            QStyle.sliderValueFromPosition(
                slider.minimum(),
                slider.maximum(),
                event.pos().x(),
                slider.width(),
            )
        )


def mouseReleaseEvent(slider, event: QMouseEvent) -> None:
    """
    Обрабатывает отпускание кнопки мыши.
    :param slider: Отправитель события.
    :param event:
    """
    if event.button() == Qt.MouseButton.LeftButton:
        slider.pressed = False
        slider.setValue(
            QStyle.sliderValueFromPosition(
                slider.minimum(),
                slider.maximum(),
                event.pos().x(),
                slider.width(),
            )
        )


def mouseMoveEvent(slider, event: QMouseEvent) -> None:
    """
    Обрабатывает движение мыши, с зажатой левой кнопкой, по слайдеру.
    Стандартный почему-то не всегда реагирует.
    :param slider: Отправитель события.
    :param event:
    """
    if slider.pressed:
        slider.setValue(
            QStyle.sliderValueFromPosition(
                slider.minimum(),
                slider.maximum(),
                event.pos().x(),
                slider.width(),
            )
        )
