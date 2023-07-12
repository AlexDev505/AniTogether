from __future__ import annotations

import typing as ty

from PyQt6.QtCore import Qt

from logger import logger


if ty.TYPE_CHECKING:
    from anilibria import Title
    from PyQt6.QtGui import QFocusEvent, QMouseEvent
    from main_window import MainWindow


def searchLineEditFocusOutEvent(main_window: MainWindow, _: QFocusEvent) -> None:
    """
    Обработчик события выхода из строки поиска релиза.
    Очистка поля ввода и закрытие виджета с результатами поиска.
    """
    main_window.searchLineEdit.clear()
    main_window.closeSearchResultWidget()

    logger.trace("searchLineEditFocusOutEvent handled")


def titleWidgetMouseEvent(
    main_window: MainWindow, title: Title, event: QMouseEvent
) -> None:
    if event.button() == Qt.MouseButton.LeftButton:
        main_window.closeSearchResultWidget()
        main_window.openPlayerPage(title)

    logger.trace("searchLineEditFocusOutEvent handled")
