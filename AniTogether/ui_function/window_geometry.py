"""

Функциональность, позволяющая изменять размеры окна, а так же перемещать его.

"""

from __future__ import annotations

import typing as ty

from PyQt6.QtCore import QEvent, QPoint, QRect, Qt
from loguru import logger


if ty.TYPE_CHECKING:
    from PyQt6.QtWidgets import QMainWindow, QWidget
    from PyQt6.QtGui import QMouseEvent


def prepareDragZone(window: QMainWindow, obj: QWidget) -> None:
    """
    Подготавливает виджет, отвечающий за перемещение окна.
    :param window: Экземпляр окна.
    :param obj: Виджет.
    """
    obj.mousePressEvent = lambda e: dragZonePressEvent(window, e)
    obj.mouseMoveEvent = lambda e: dragZoneMoveEvent(window, e)
    obj.mouseReleaseEvent = lambda e: dragZoneReleaseEvent(window, e)


def dragZonePressEvent(window: QMainWindow, event: QMouseEvent) -> None:
    """
    Обрабатывает нажатие на виджет, отвечающий за перемещение окна.
    :param window: Экземпляр окна.
    :param event:
    """
    if event.button() == Qt.MouseButton.LeftButton:
        window.__dict__["_drag_pos"] = event.globalPosition().toPoint()


def dragZoneMoveEvent(window: QMainWindow, event: QMouseEvent) -> None:
    """
    Обрабатывает движение мыши по виджету, отвечающему за перемещение окна.
    :param window: Экземпляр окна.
    :param event:
    """
    if (
        window.__dict__.get("_drag_pos") is not None
        and window.cursor().shape() == Qt.CursorShape.ArrowCursor
    ):
        if window.isFullScreen():  # Выходим их полноэкранного режима
            screen_width = window.width()  # Ширина экрана
            toggleFullScreen(window)
            geometry = window.geometry()  # Размеры и положение окна

            window.setGeometry(
                int(
                    event.globalPosition().x()
                    - (geometry.width() * event.globalPosition().x() / screen_width)
                ),  # Координата X
                event.globalPosition().toPoint().y(),  # Y
                geometry.width(),
                geometry.height(),
            )

        window.move(
            window.pos()
            + event.globalPosition().toPoint()
            - window.__dict__["_drag_pos"]
        )
        window.__dict__["_drag_pos"] = event.globalPosition().toPoint()


def dragZoneReleaseEvent(window: QMainWindow, event: QMouseEvent) -> None:
    """
    Обрабатывает отпускание кнопки мыши на виджете, отвечающем за перемещение окна.
    :param window: Экземпляр окна.
    :param event:
    """
    if event.button() == Qt.MouseButton.LeftButton:
        window.__dict__["_drag_pos"] = None


def mouseEvent(window: QMainWindow, event: QMouseEvent) -> None:
    """
    Обрабатывает события мыши, для реализации изменения размера окна.
    :param window: Экземпляр окна.
    :param event:
    """
    if window.isFullScreen():
        return

    if event.type() == QEvent.Type.HoverEnter:  # Движение мыши по окну
        if window.__dict__.get("_start_cursor_pos") is None:
            _check_position(window, event)

    if event.type() == QEvent.Type.MouseButtonPress:  # Нажатие
        if event.button() == Qt.MouseButton.LeftButton:
            window.__dict__["_start_cursor_pos"] = window.mapToGlobal(event.pos())
            window.__dict__["_start_window_geometry"] = window.geometry()

    elif event.type() == QEvent.Type.MouseButtonRelease:  # Отпускание
        if event.button() == Qt.MouseButton.LeftButton:
            window.__dict__["_start_cursor_pos"] = None
            _check_position(window, event)

    elif event.type() == QEvent.Type.MouseMove:  # Движение с зажатой кнопкой мыши
        if window.__dict__.get("_start_cursor_pos") is not None:
            if window.cursor().shape() in {Qt.CursorShape.SizeFDiagCursor}:
                _resize_window(window, event)


def _check_position(window: QMainWindow, event: QMouseEvent) -> None:
    """
    Проверяет положение мыши.
    Устанавливает определённый курсор, при наведении на край и обратно.
    :param window: Экземпляр окна.
    :param event:
    """
    rect = window.rect()
    bottom_right = rect.bottomRight()

    if event.position() in QRect(
        QPoint(bottom_right.x() - 30, bottom_right.y() - 30),
        QPoint(bottom_right.x(), bottom_right.y()),
    ):
        window.setCursor(Qt.CursorShape.SizeFDiagCursor)
    else:  # Обычный курсор
        if window.cursor() == Qt.CursorShape.SizeFDiagCursor:
            window.setCursor(Qt.CursorShape.ArrowCursor)


def _resize_window(window: QMainWindow, event: QMouseEvent) -> None:
    """
    Изменяет размер окна.
    :param window: Экземпляр окна.
    :param event:
    """
    geometry = window.__dict__["_start_window_geometry"]
    last = window.mapToGlobal(event.pos()) - window.__dict__["_start_cursor_pos"]
    new_width = geometry.width() + last.x()
    new_height = geometry.height() + last.y()
    window.setGeometry(geometry.x(), geometry.y(), new_width, new_height)


def toggleFullScreen(window: QMainWindow) -> None:
    """
    Активирует/выключает полноэкранный режим.
    :param window: Экземпляр окна.
    """
    if not window.isFullScreen():
        logger.debug("Switch to full screen mode")
        window.showFullScreen()
        # window.resizeWidgetFrame.hide()
    else:
        logger.debug("Exit full screen mode")
        window.showNormal()
        # window.resizeWidgetFrame.show()
