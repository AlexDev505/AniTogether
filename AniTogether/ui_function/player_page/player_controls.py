from __future__ import annotations

import typing as ty
from functools import partial

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
    playerControlsWidget = PlayerControlsWidget(main_window)
    main_window.__setattr__("playerControlsWidget", playerControlsWidget)
    playerControlsWidget.homeBtn.clicked.connect(partial(leavePlayerPage, main_window))
    playerControlsWidget.fullscreenBtn.clicked.connect(
        partial(toggleFullScreen, main_window)
    )
    return playerControlsWidget


def show(main_window: MainWindow, title: Title, episode_number: int) -> None:
    playerControlsWidget = main_window.__getattribute__("playerControlsWidget")
    if not playerControlsWidget:
        playerControlsWidget = create(main_window)
    playerControlsWidget.show()
    playerControlsWidget.updateGometry()

    playerControlsWidget.titleLabel.setText(title.names.ru)
    playerControlsWidget.episodeNumberLabel.setText(f"{episode_number} серия")


def toggleFullScreen(main_window: MainWindow) -> None:
    if main_window.topFrame.isHidden():
        main_window.topFrame.show()
        if not main_window.__getattribute__("__was_fullscreen"):
            main_window.maximizeAppBtn.click()
    else:
        main_window.topFrame.hide()
        if main_window.isFullScreen():
            main_window.__setattr__("__was_fullscreen", True)
        else:
            main_window.maximizeAppBtn.click()
            main_window.__setattr__("__was_fullscreen", False)


def leavePlayerPage(main_window: MainWindow) -> None:
    main_window.__setattr__("current_title", None)
    main_window.__setattr__("current_episode_number", None)
    main_window.__setattr__("current_episode", None)
    main_window.__setattr__("episodes_count", None)
    main_window.__getattribute__("playerControlsWidget").hide()
    main_window.openHomePage()


def resizeEvent(main_window: MainWindow, event: QtGui.QResizeEvent) -> None:
    if main_window.stackedWidget.currentWidget() == main_window.playerPage:
        if playerControlsWidget := main_window.__getattribute__("playerControlsWidget"):
            playerControlsWidget.updateGometry()

    main_window.__getattribute__("originalResizeEvent" + __name__)(event)
