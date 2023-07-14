from PyQt6.QtWidgets import QFrame

from ui import Ui_PlayerControls
from ui_function import sliders


class PlayerControlsWidget(Ui_PlayerControls, QFrame):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        self.setParent(parent)

        sliders.prepareSlider(self.playbackSlider)
        sliders.prepareSlider(self.volumeSlider)

    def updateGometry(self) -> None:
        parent_geometry = self.parent().geometry()
        self.setGeometry(
            0,
            parent_geometry.height() - self.height(),
            parent_geometry.width(),
            self.height(),
        )
