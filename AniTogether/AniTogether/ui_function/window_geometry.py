"""

Функциональность, позволяющая изменять размеры окна, а так же перемещать его.

"""

from __future__ import annotations

import typing as ty
from functools import partial

from PyQt6.QtCore import QRect, Qt, QChildEvent
from PyQt6.QtWidgets import QSizeGrip
from loguru import logger

from widgets import SideGrip


if ty.TYPE_CHECKING:
    from PyQt6 import QtCore, QtWidgets, QtGui


# Размер областей захвата
SIZE_GRIP_WIDTH = 8


def prepareDragZone(window: QtWidgets.QMainWindow, obj: QtWidgets.QWidget) -> None:
    """
    Подготавливает виджет, отвечающий за перемещение окна.
    :param window: Экземпляр окна.
    :param obj: Виджет.
    """
    obj.mousePressEvent = lambda e: dragZonePressEvent(window, e)
    obj.mouseMoveEvent = lambda e: dragZoneMoveEvent(window, e)
    obj.mouseReleaseEvent = lambda e: dragZoneReleaseEvent(window, e)


def dragZonePressEvent(window: QtWidgets.QMainWindow, event: QtGui.QMouseEvent) -> None:
    """
    Обрабатывает нажатие на виджет, отвечающий за перемещение окна.
    :param window: Экземпляр окна.
    :param event:
    """
    if event.button() == Qt.MouseButton.LeftButton:
        window.__dict__["_drag_pos"] = event.globalPosition().toPoint()


def dragZoneMoveEvent(window: QtWidgets.QMainWindow, event: QtGui.QMouseEvent) -> None:
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


def dragZoneReleaseEvent(
    window: QtWidgets.QMainWindow, event: QtGui.QMouseEvent
) -> None:
    """
    Обрабатывает отпускание кнопки мыши на виджете, отвечающем за перемещение окна.
    :param window: Экземпляр окна.
    :param event:
    """
    if event.button() == Qt.MouseButton.LeftButton:
        window.__dict__["_drag_pos"] = None


def iterGrips(window: QtWidgets.QMainWindow) -> ty.Generator[SideGrip | QSizeGrip]:
    """
    :return: Генератор по областям захвата.
    """
    for grip in window.__getattribute__("cornerGrips"):
        yield grip
    for grip in window.__getattribute__("sideGrips"):
        yield grip


def prepareSizeGrips(window: QtWidgets.QMainWindow) -> None:
    """
    Подготавливает области захвата.
    """
    window.__setattr__("_grip_size", SIZE_GRIP_WIDTH)
    window.sideGrips = [
        SideGrip(window, Qt.Edge.LeftEdge),
        SideGrip(window, Qt.Edge.TopEdge),
        SideGrip(window, Qt.Edge.RightEdge),
        SideGrip(window, Qt.Edge.BottomEdge),
    ]
    window.cornerGrips = [QSizeGrip(window) for i in range(4)]
    for grip in iterGrips(window):
        grip.setStyleSheet("background-color: transparent;")
    window.__setattr__("originalResizeEvent" + __name__, window.resizeEvent)
    window.resizeEvent = partial(resizeEvent, window)
    window.__setattr__("originalEventFilter" + __name__, window.eventFilter)
    window.eventFilter = partial(eventFilter, window)
    window.installEventFilter(window)


def setGripSize(window: QtWidgets.QMainWindow, size: int) -> None:
    """
    Изменяет размер областей захвата.
    """
    if size == window.__getattribute__("_grip_size"):
        return
    window.__setattr__("_grip_size", max(2, size))
    updateGrips(window)


def updateGrips(window: QtWidgets.QMainWindow) -> None:
    """
    Обновляет положение областей захвата.
    """
    grip_size = window.__getattribute__("_grip_size")

    outRect = window.rect()
    inRect = outRect.adjusted(grip_size, grip_size, -grip_size, -grip_size)

    # top left
    window.__getattribute__("cornerGrips")[0].setGeometry(
        QRect(outRect.topLeft(), inRect.topLeft())
    )
    # top right
    window.__getattribute__("cornerGrips")[1].setGeometry(
        QRect(outRect.topRight(), inRect.topRight()).normalized()
    )
    # bottom right
    window.__getattribute__("cornerGrips")[2].setGeometry(
        QRect(inRect.bottomRight(), outRect.bottomRight())
    )
    # bottom left
    window.__getattribute__("cornerGrips")[3].setGeometry(
        QRect(outRect.bottomLeft(), inRect.bottomLeft()).normalized()
    )

    # left edge
    window.__getattribute__("sideGrips")[0].setGeometry(
        0, inRect.top(), grip_size, inRect.height()
    )
    # top edge
    window.__getattribute__("sideGrips")[1].setGeometry(
        inRect.left(), 0, inRect.width(), grip_size
    )
    # right edge
    window.__getattribute__("sideGrips")[2].setGeometry(
        inRect.left() + inRect.width(), inRect.top(), grip_size, inRect.height()
    )
    # bottom edge
    window.__getattribute__("sideGrips")[3].setGeometry(
        grip_size, inRect.top() + inRect.height(), inRect.width(), grip_size
    )


def toggleGrips(window: QtWidgets.QMainWindow, value: bool) -> None:
    """
    Включает / выключает области захвата.
    """
    for grip in iterGrips(window):
        if value:
            grip.show()
        else:
            grip.hide()


def eventFilter(
    window: QtWidgets.QMainWindow, obj: QtCore.QObject, event: QtCore.QEvent
) -> bool:
    if (
        isinstance(event, QChildEvent)
        and event.added()
        and event.child().isWidgetType()
    ):  # Добавление нового виджета
        for grip in iterGrips(window):
            grip.raise_()  # Поднимает области захвата выше всех остальных виджетов
        logger.opt(colors=True).trace(
            f"Grips are updated. Added: {event.child().objectName()}"
        )

    return window.__getattribute__("originalEventFilter" + __name__)(obj, event)


def resizeEvent(window: QtWidgets.QMainWindow, event: QtGui.QResizeEvent):
    """
    Событие изменения размера окна.
    """
    window.__getattribute__("originalResizeEvent" + __name__)(event)
    updateGrips(window)


def toggleFullScreen(window: QtWidgets.QMainWindow) -> None:
    """
    Активирует/выключает полноэкранный режим.
    :param window: Экземпляр окна.
    """
    if not window.isFullScreen():
        logger.debug("Switch to full screen mode")
        window.showFullScreen()
        toggleGrips(window, False)
    else:
        logger.debug("Exit full screen mode")
        window.showNormal()
        toggleGrips(window, True)
