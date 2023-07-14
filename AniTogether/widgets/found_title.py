from __future__ import annotations

import typing as ty

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame

from ui import Ui_FoundTitle


if ty.TYPE_CHECKING:
    from PyQt6 import QtCore, QtGui


class FoundTitleWidget(QFrame, Ui_FoundTitle):
    """
    Виджет релиза, отображаемый в результатах поиска релизов.
    """

    # Название релиза изменено
    titleChanged: QtCore.pyqtBoundSignal = pyqtSignal()

    # Значения, которые использует контейнер результатов поиска
    # для вычисления своих размеров.
    # Определяются при первой инициализации экземпляра
    widgetHeight: int = 0
    hMargin: int = 0

    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        self.setParent(parent)

        # Оригинальное название релиза
        self.original_title: str = ""
        # Средняя ширина символа.
        # Определяется при изменении названия релиза.
        self.averageCharWidth: int = 1

        if self.widgetHeight == 0:
            margins = self.foundTitleLayout.contentsMargins()
            self.__class__.widgetHeight = (
                self.titleIcon.minimumHeight() + margins.top() * 2
            )
            self.__class__.hMargin = margins.left()

    def setTitle(self, title: str) -> None:
        """
        Изменяет название релиза.
        :param title: Название.
        """
        self.original_title = title
        self.titleLabel.setText(title)
        self.titleChanged.emit()
        self.averageCharWidth = self.titleLabel.fontMetrics().boundingRect(
            title
        ).width() / len(title)

    def resizeEvent(self, _: QtGui.QResizeEvent) -> None:
        """
        Событие изменения размера виджета.
        """
        allowed_chars_count = int(self.titleLabel.width() // self.averageCharWidth)
        if allowed_chars_count < len(self.original_title):
            self.titleLabel.setText(
                self.original_title[: allowed_chars_count - 3] + "..."
            )
        else:
            self.titleLabel.setText(self.original_title)
