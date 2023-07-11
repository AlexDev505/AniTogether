from __future__ import annotations

import typing as ty

from logger import logger


if ty.TYPE_CHECKING:
    from main_window import MainWindow
    from PyQt6.QtGui import QFocusEvent


def searchLineEditFocusOutEvent(main_window: MainWindow, _: QFocusEvent) -> None:
    """
    Обработчик события выхода из строки поиска релиза.
    Очистка поля ввода и закрытие виджета с результатами поиска.
    """
    main_window.searchLineEdit.clear()
    main_window.close_search_result_widget()

    logger.trace("searchLineEditFocusOutEvent handled")
