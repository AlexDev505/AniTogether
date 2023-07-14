from __future__ import annotations

import typing as ty

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtWidgets import QLabel

from ui import Ui_TitleFromHistory


if ty.TYPE_CHECKING:
    from PyQt6 import QtGui
    from history import TitleFromHistory


class TitleFromHistoryWidget(Ui_TitleFromHistory, QLabel):
    maxWidth = 350
    maxHeight = 500
    K = maxHeight / maxWidth

    def __init__(self, parent, title: TitleFromHistory):
        super().__init__()
        self.setupUi(self)
        self.setParent(parent)
        self.setMaximumSize(self.maxWidth, self.maxHeight)

        self.title: TitleFromHistory = ...
        self.original_pixmap: QtGui.QPixmap | None = None
        self.updateTitle(title)

    def updateTitle(self, title: TitleFromHistory) -> None:
        self.title = title
        if title.last_watched_episode == 0:
            self.watchProgressLabel.setText("Ни одного эпизода")
        elif title.last_watched_episode == title.episodes_count:
            self.watchProgressLabel.setText("Все эпизоды")
        else:
            self.watchProgressLabel.setText(
                f"{title.last_watched_episode} из {title.episodes_count}"
            )
        self.watchProgressSlider.setMaximum(title.episodes_count)
        self.watchProgressSlider.setValue(title.last_watched_episode)

    def installPixmap(self, pixmap: QtGui.QPixmap) -> None:
        self.original_pixmap = pixmap
        self.setPixmap(
            self.original_pixmap.scaled(
                self.size(), transformMode=Qt.TransformationMode.SmoothTransformation
            )
        )

    def resizeEvent(self, _: QtGui.QResizeEvent) -> None:
        self.setMinimumHeight(int(self.width() * self.K))
        self.setMaximumHeight(int(self.width() * self.K))
        if self.original_pixmap:
            self.setPixmap(
                self.original_pixmap.scaled(
                    self.size(),
                    transformMode=Qt.TransformationMode.SmoothTransformation,
                )
            )
        rect = QRect(
            0,
            self.height() - self.watchProgressSlider.height(),
            self.width(),
            self.watchProgressSlider.height(),
        )
        self.watchProgressSlider.setGeometry(rect)
        self.watchProgressLabel.setGeometry(rect)
