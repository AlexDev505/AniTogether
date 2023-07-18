from __future__ import annotations
import typing as ty

from loguru import logger
import mpv
from enum import Enum

if ty.TYPE_CHECKING:
    from PyQt6 import QtWidgets


class SeekType(Enum):
    RELATIVE = "relative"
    ABSOLUTE = "absolute"


class Player:
    def __init__(self, container: QtWidgets.QWidget, volume: int):
        self._player = mpv.MPV(wid=str(int(container.winId())))
        self.volume = volume

        self._duration: float = 0
        self._playback_time: float = 0

        self._player.observe_property("playback-time", self._playback_time_changed)
        self._player.event_callback(mpv.MpvEventID.PLAYBACK_RESTART)(self._start_file)
        self._on_init = None
        self._on_playback_time_changed = None

    def init(self, url: str) -> None:
        self._player.play(url)

    def pause(self) -> None:
        self._player.pause = True

    def play(self) -> None:
        self._player.pause = False

    def seek(self, value: float, seek_type: SeekType = SeekType.RELATIVE) -> None:
        self._player.seek(value, seek_type.value)

    def set_volume(self, value: int) -> None:
        self.volume = value
        self._player.ao_volume = value

    def _start_file(self, _):
        if self._duration != 0:
            return
        self._duration = self._player.wait_for_property("duration")
        self._player.ao_volume = self.volume
        if self._on_init:
            self._on_init()

    def _playback_time_changed(self, _, playback_time):
        if playback_time is not None:
            self._playback_time = round(playback_time, 2)
            if self._on_playback_time_changed:
                self._on_playback_time_changed(playback_time)

    def on_init(self, handler) -> None:
        self._on_init = handler

    def on_playback_time_changed(self, handler):
        self._on_playback_time_changed = handler

    def on_paused_for_cache_change(self, handler):
        self._player.observe_property("paused-for-cache", handler)
        self._player.observe_property("seeking", handler)

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def playback_time(self) -> float:
        return self._playback_time
