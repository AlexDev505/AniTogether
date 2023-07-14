from __future__ import annotations

import typing as ty

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtWidgets import QLabel

from ui import Ui_TitleFromHistory


if ty.TYPE_CHECKING:
    from PyQt6 import QtGui
    from history import TitleFromHistory


class TitleFromHistoryWidget(Ui_TitleFromHistory, QLabel):
    """
    Виджет релиза, отображаемый в разделе "История"
    """

    maxWidth = 350
    maxHeight = 500
    # Коэффициент для вычисления пропорциональной высоты от ширины
    K = maxHeight / maxWidth

    def __init__(self, parent, title: TitleFromHistory):
        super().__init__()
        self.setupUi(self)
        self.setParent(parent)
        self.setMaximumSize(self.maxWidth, self.maxHeight)

        # Оригинальный
        self.original_poster: QtGui.QPixmap | None = None
        self.title: TitleFromHistory = ...
        self.updateData(title)

    def updateData(self, title: TitleFromHistory) -> None:
        """
        Обновляет отображаемые данные релиза.
        :param title: Новые данные о релизе.
        """
        self.title = title
        # Отображаем текстовый прогресс просмотра
        if title.last_watched_episode == 0:
            self.watchProgressLabel.setText("Ни одного эпизода")
        elif title.last_watched_episode == title.episodes_count:
            self.watchProgressLabel.setText("Все эпизоды")
        else:
            self.watchProgressLabel.setText(
                f"{title.last_watched_episode} из {title.episodes_count}"
            )
        # Отображаем визуальный прогресс просмотра
        self.watchProgressSlider.setMaximum(title.episodes_count)
        self.watchProgressSlider.setValue(title.last_watched_episode)

    def installPoster(self, pixmap: QtGui.QPixmap) -> None:
        """
        Устанавливает постер релиза.
        :param pixmap: Изображение.
        """
        self.original_poster = pixmap
        self.showPoster()

    def showPoster(self) -> None:
        """
        Отображает постер нужного размера.
        """
        self.setPixmap(
            self.original_poster.scaled(
                self.size(), transformMode=Qt.TransformationMode.SmoothTransformation
            )
        )

    def resizeEvent(self, _: QtGui.QResizeEvent) -> None:
        """
        Событие изменения размера.
        """
        # Устанавливаем высоту, пропорциональную ширине
        self.setMinimumHeight(int(self.width() * self.K))
        self.setMaximumHeight(int(self.width() * self.K))

        # Изменяем размера постера
        if self.original_poster:
            self.showPoster()

        # Изменяем размер виджетов, отображающих прогресс просмотра
        rect = QRect(
            0,
            self.height() - self.watchProgressSlider.height(),
            self.width(),
            self.watchProgressSlider.height(),
        )
        self.watchProgressSlider.setGeometry(rect)
        self.watchProgressLabel.setGeometry(rect)
