"""

Функционал виджета управления плеером.

"""

from __future__ import annotations

import typing as ty
from functools import partial

from loguru import logger

from widgets import PlayerControlsWidget


if ty.TYPE_CHECKING:
    from anilibria import Title
    from PyQt6 import QtGui
    from main_window import MainWindow


def setupUiFunctions(main_window: MainWindow) -> None:
    main_window.__setattr__("playerControlsWidget", None)
    main_window.__setattr__("originalResizeEvent" + __name__, main_window.resizeEvent)
    main_window.resizeEvent = partial(resizeEvent, main_window)


def create(main_window: MainWindow) -> PlayerControlsWidget:
    """
    Создает виджет управления плеером.
    :return: Экземпляр PlayerControlsWidget.
    """
    playerControlsWidget = PlayerControlsWidget(main_window)
    # Устанавливаем обработчики на кнопки
    playerControlsWidget.homeBtn.clicked.connect(partial(leavePlayerPage, main_window))
    playerControlsWidget.fullscreenBtn.clicked.connect(
        partial(toggleFullScreen, main_window)
    )

    main_window.__setattr__("playerControlsWidget", playerControlsWidget)
    logger.trace("PlayerControlsWidget created")

    return playerControlsWidget


def show(main_window: MainWindow, title: Title, episode_number: int) -> None:
    """
    Отображает виджет управления плеером.
    :param main_window:
    :param title: Релиз.
    :param episode_number: Номер эпизода.
    """
    playerControlsWidget = main_window.__getattribute__("playerControlsWidget")
    if not playerControlsWidget:
        playerControlsWidget = create(main_window)  # Создаем виджет
    playerControlsWidget.show()
    playerControlsWidget.updateGometry()

    # Заполняем данные о релизе
    playerControlsWidget.titleLabel.setText(title.names.ru)
    playerControlsWidget.episodeNumberLabel.setText(f"{episode_number} серия")


def toggleFullScreen(main_window: MainWindow) -> None:
    """
    Включение / выключение полноэкранного режима плеера.
    """
    if main_window.topFrame.isHidden():  # Верхняя панель скрыта
        main_window.topFrame.show()  # Показываем верхнюю панель
        # До перехода приложение не было в полноэкранном режиме
        if not main_window.__getattribute__("__was_fullscreen"):
            main_window.maximizeAppBtn.click()  # Выход из полноэкранного режима
        logger.debug("Exit player full screen mode")
    else:
        main_window.topFrame.hide()
        if main_window.isFullScreen():  # Приложение уже в полноэкранном режиме
            main_window.__setattr__("__was_fullscreen", True)
        else:
            main_window.maximizeAppBtn.click()  # Переход в полноэкранный режим
            main_window.__setattr__("__was_fullscreen", False)
        logger.debug("Switch to player full screen mode")


def leavePlayerPage(main_window: MainWindow) -> None:
    """
    Возвращает на домашнюю страницу.
    Очищает страницу плеера.
    """
    logger.trace("Clearing player data")
    main_window.__setattr__("current_title", None)
    main_window.__setattr__("current_episode_number", None)
    main_window.__setattr__("current_episode", None)
    main_window.__setattr__("episodes_count", None)
    main_window.__getattribute__("playerControlsWidget").hide()
    main_window.previewLabel.clear()  # Удаляем превью
    main_window.openHomePage()


def resizeEvent(main_window: MainWindow, event: QtGui.QResizeEvent) -> None:
    """
    Событие изменения размера главного окна.
    """
    if main_window.stackedWidget.currentWidget() == main_window.playerPage:
        if playerControlsWidget := main_window.__getattribute__("playerControlsWidget"):
            # Обновляем положение и размеры виджета управления плеером
            playerControlsWidget.updateGometry()

    main_window.__getattribute__("originalResizeEvent" + __name__)(event)
