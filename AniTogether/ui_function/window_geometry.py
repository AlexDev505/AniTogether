"""

Функциональность, позволяющая изменять размеры окна, а так же перемещать его.

"""

from __future__ import annotations

import typing as ty
from functools import partial

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QSizeGrip, QFrame
from loguru import logger


if ty.TYPE_CHECKING:
    from PyQt6.QtGui import QMouseEvent, QResizeEvent


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


class SideGrip(QFrame):
    """
    Боковые области, для изменения размеров окна.
    """

    def __init__(self, parent: QMainWindow, edge: Qt.Edge):
        """
        :param parent: Главное окно.
        :param edge: Сторона.
        """
        QFrame.__init__(self, parent)
        self.setObjectName("sideGrip")
        if edge == Qt.Edge.LeftEdge:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
            self.resizeFunc = self.resizeLeft
        elif edge == Qt.Edge.TopEdge:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
            self.resizeFunc = self.resizeTop
        elif edge == Qt.Edge.RightEdge:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
            self.resizeFunc = self.resizeRight
        else:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
            self.resizeFunc = self.resizeBottom
        self.mouse_pos = None

    def resizeLeft(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() - delta.x())
        geo = window.geometry()
        geo.setLeft(geo.right() - width)
        window.setGeometry(geo)

    def resizeTop(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() - delta.y())
        geo = window.geometry()
        geo.setTop(geo.bottom() - height)
        window.setGeometry(geo)

    def resizeRight(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() + delta.x())
        window.resize(width, window.height())

    def resizeBottom(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() + delta.y())
        window.resize(window.width(), height)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.mouse_pos is not None:
            delta = event.pos() - self.mouse_pos
            self.resizeFunc(delta)

    def mouseReleaseEvent(self, event):
        self.mouse_pos = None


def prepareSizeGrips(window: QMainWindow) -> None:
    window.__setattr__("_grip_size", 8)
    window.sideGrips = [
        SideGrip(window, Qt.Edge.LeftEdge),
        SideGrip(window, Qt.Edge.TopEdge),
        SideGrip(window, Qt.Edge.RightEdge),
        SideGrip(window, Qt.Edge.BottomEdge),
    ]
    window.cornerGrips = [QSizeGrip(window) for i in range(4)]
    for grip in window.cornerGrips:
        grip.setStyleSheet("background-color: transparent;")
    for grip in window.sideGrips:
        grip.setStyleSheet("background-color: transparent;")
    window.resizeEvent = partial(resizeEvent, window)


def setGripSize(window: QMainWindow, size: int) -> None:
    if size == window.__getattribute__("_grip_size"):
        return
    window.__setattr__("_grip_size", max(2, size))
    updateGrips(window)


def updateGrips(window: QMainWindow) -> None:
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


def resizeEvent(window: QMainWindow, event: QResizeEvent):
    QMainWindow.resizeEvent(window, event)
    updateGrips(window)


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
