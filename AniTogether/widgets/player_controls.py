from functools import partial

from PyQt6.QtWidgets import QFrame

from ui import Ui_PlayerControls
from ui_function import sliders, player_page


class PlayerControlsWidget(Ui_PlayerControls, QFrame):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        self.setParent(parent)
        self.setupSignals(parent)

    def setupSignals(self, parent) -> None:
        sliders.prepareSlider(self.playbackSlider)
        sliders.prepareSlider(self.volumeSlider)

        self.fullscreenBtn.clicked.connect(
            partial(player_page.toggleFullScreen, parent)
        )

    def updateGometry(self) -> None:
        parent_geometry = self.parent().geometry()
        self.setGeometry(
            0,
            parent_geometry.height() - self.height(),
            parent_geometry.width(),
            self.height(),
        )
