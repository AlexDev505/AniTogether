import webview
from loguru import logger

from .window_geometry import resize, move_to_cursor, drag_window
from .app_update import update_app


class JSApi:
    def __init__(self):
        self._full_screen = False
        self._was_full_screen = False

    @property
    def _window(self) -> webview.Window:
        return webview.windows[0]

    def close_app(self) -> None:
        self._window.destroy()

    def minimize_app(self) -> None:
        self._window.minimize()

    def toggle_full_screen_app(self) -> None:
        self._window.toggle_fullscreen()
        self._full_screen = not self._full_screen

    def toggle_player_full_screen_app(self, value: bool) -> None:
        print(value, self._was_full_screen)
        if value:
            if self._full_screen:
                self._was_full_screen = True
            else:
                self.toggle_full_screen_app()
                self._was_full_screen = False
            logger.debug("Switch to player full screen mode")
        else:
            if not self._was_full_screen:
                self.toggle_full_screen_app()
            logger.debug("Exit player full screen mode")

    def drag_window(self) -> None:
        if self._full_screen:
            self.toggle_full_screen_app()
            move_to_cursor(self._window)
        drag_window(self._window)

    def resize_drag(self, size_grip: str) -> None:
        resize(self._window, size_grip)

    def update_app(self) -> dict:
        return update_app(self._window) or {}
