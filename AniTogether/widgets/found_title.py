from __future__ import annotations

import typing as ty

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame

from ui import Ui_FoundTitle


if ty.TYPE_CHECKING:
    from PyQt6 import QtCore, QtGui


class FoundTitleWidget(QFrame, Ui_FoundTitle):
    titleChanged: QtCore.pyqtBoundSignal = pyqtSignal()

    widgetHeight: int = 0
    hMargin: int = 0

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.original_title: str = ""
        self.charWidth: int = 1

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
        self.charWidth = self.titleLabel.fontMetrics().boundingRect(
            title
        ).width() / len(title)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        allowed_chars = int(self.titleLabel.width() // self.charWidth)
        if allowed_chars < len(self.original_title):
            self.titleLabel.setText(self.original_title[: allowed_chars - 3] + "...")
        else:
            self.titleLabel.setText(self.original_title)
