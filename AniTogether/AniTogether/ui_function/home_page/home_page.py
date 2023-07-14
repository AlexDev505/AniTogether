"""

Функционал главной страницы.

"""

from __future__ import annotations

import typing as ty

from loguru import logger

from . import history_container, titles_searching


if ty.TYPE_CHECKING:
    from main_window import MainWindow


def setupUiFunctions(main_window: MainWindow) -> None:
    titles_searching.setupUiFunctions(main_window)
    history_container.setupUiFunctions(main_window)


def openHomePage(main_window: MainWindow) -> None:
    logger.debug("Opening the home page")
    main_window.stackedWidget.setCurrentWidget(main_window.homePage)
    main_window.homePageIsOpen.emit()
    logger.debug("Home page is open")
