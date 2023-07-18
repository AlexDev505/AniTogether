import asyncio
import locale
from functools import partial

import qasync
import sys
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtWidgets import *

from logger import logger
from player import Player
from tools import create_loading_movie
from widgets import PlayerControlsWidget


URL = (
    "https://cache.libria.fun/videos/media/ts/9520/1/1080/"
    "2c461de4505541e4e2f84a6e3ef5f6c0.m3u8"
)


def seconds_view(seconds: int, min_parts: int = 1) -> str:
    result = f"{seconds%60}".rjust(2, "0")
    if seconds >= 60 or min_parts > 1:
        result = f"{seconds%3600//60}:".rjust(3, "0") + result
    if seconds >= 3600 or min_parts > 2:
        result = f"{seconds//3600}:" + result
    return result


class Test(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("*{background:transparent}")

        self.setMinimumSize(820, 520)
        self.setGeometry(100, 100, 400, 260)
        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)
        self.cw_l = QHBoxLayout(self.cw)

        self.container = QFrame(self.cw)
        self.cw_l.addWidget(self.container)

        self.volume = 50

        self.loading_label = QLabel(self)
        self.loading_label.setMovie(create_loading_movie(100))

        self.player_controls = PlayerControlsWidget(self)

        self.player_controls.volumeSlider.setValue(self.volume // 10)
        self.player_controls.volumeSlider.valueChanged.connect(self.set_volume)
        self.player_controls.volumeBtn.clicked.connect(
            partial(self.player_controls.volumeSlider.setValue, 0)
        )
        self.player_controls.playBtn.clicked.connect(self.toggle_paused)

        self.player_controls.volumeSlider.setEnabled(False)
        self.player_controls.volumeBtn.setEnabled(False)
        self.player_controls.playBtn.setEnabled(False)

        self.player = Player(self.container, self.volume)

        self.player.on_init(self.on_init)
        self.player.on_playback_time_changed(self.on_playback_time_changed)
        self.player.on_paused_for_cache_change(self.on_paused_for_cache_change)

        self.player.init(URL)
        self.time_view_parts = 1
        self._duration = ""

        self.paused = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Right:
            self.player.seek(10)
        elif event.key() == Qt.Key.Key_Left:
            self.player.seek(-10)
        elif event.key() == Qt.Key.Key_Space:
            self.toggle_paused()
        event.accept()

    def toggle_paused(self) -> None:
        if self.paused:
            self.play()
        else:
            self.pause()
        self.paused = not self.paused

    def play(self) -> None:
        self.player_controls.playBtn.setIcon(QIcon(":/base/pause.svg"))
        print(f"playing: {self.player.playback_time}")
        self.player.play()

    def pause(self) -> None:
        self.player_controls.playBtn.setIcon(QIcon(":/base/play.svg"))
        self.player.pause()
        print(f"paused")

    def set_volume(self, value) -> None:
        self.volume = value * 10
        if self.volume == 0:
            icon = QIcon(":/base/volume_muted.svg")
        elif self.volume < 40:
            icon = QIcon(":/base/volume_low.svg")
        elif self.volume < 70:
            icon = QIcon(":/base/volume_medium.svg")
        else:
            icon = QIcon(":/base/volume_height.svg")
        self.player_controls.volumeBtn.setIcon(icon)
        self.player.set_volume(self.volume)

    def on_init(self):
        self.player_controls.playBtn.setIcon(QIcon(":/base/pause.svg"))
        self.player_controls.playbackSlider.setMaximum(int(self.player.duration))
        self._duration = seconds_view((int(self.player.duration)))
        self.time_view_parts = self._duration.count(":") + 1
        self.player_controls.volumeSlider.setEnabled(True)
        self.player_controls.volumeBtn.setEnabled(True)
        self.player_controls.playBtn.setEnabled(True)

    def on_playback_time_changed(self, playback_time):
        self.player_controls.playbackLabel.setText(
            f"{seconds_view(int(playback_time), self.time_view_parts)} / "
            f"{self._duration}"
        )
        self.player_controls.playbackSlider.setValue(int(playback_time))

    def on_paused_for_cache_change(self, _, value: bool) -> None:
        print(_, value)
        if value:
            self.loading_label.show()
            self.loading_label.setMovie(create_loading_movie(100))
        elif value is False:
            self.loading_label.hide()
            self.loading_label.clear()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.player_controls.updateGometry()
        self.loading_label.setGeometry(
            int(self.width() / 2 - 50), int(self.height() / 2 - 50), 100, 100
        )


@logger.catch
def exception_hook(exception_type, value, __):
    if exception_type is KeyboardInterrupt:
        sys.exit()
    raise Exception from value


sys.excepthook = exception_hook


def close_future(future, loop):
    loop.call_later(10, future.cancel)
    future.cancel()


def sync_main():
    app = QApplication([])
    window = Test()
    window.show()
    app.exec()


async def main():
    loop = asyncio.get_event_loop()
    future = asyncio.Future()

    app = qasync.QApplication.instance()
    if hasattr(app, "aboutToQuit"):
        getattr(app, "aboutToQuit").connect(partial(close_future, future, loop))

    locale.setlocale(locale.LC_NUMERIC, "C")
    window = Test()
    window.show()

    await future


if __name__ == "__main__":
    # sync_main()
    try:
        qasync.run(main())
    except asyncio.exceptions.CancelledError:
        sys.exit(0)
