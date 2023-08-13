from __future__ import annotations

import time
import typing as ty
from ctypes import windll, Structure, c_long, byref

from loguru import logger


if ty.TYPE_CHECKING:
    import webview


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


def query_mouse_position() -> tuple[int, int]:
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return pt.x, pt.y


def resize(window: webview.Window, size_grip):
    state_left = windll.user32.GetKeyState(0x01)

    # Определяем начальное положение курсора, окна и его размер
    start_x, start_y = query_mouse_position()
    start_win_x = window.x
    start_win_y = window.y
    start_width = window.width
    start_height = window.height

    logger.debug(f"Resize started: {size_grip}")

    while True:
        # Пользователь отпустил кнопку мыши
        if windll.user32.GetKeyState(0x01) != state_left:
            logger.debug("Resize finished")
            break

        current_x, current_y = query_mouse_position()

        # Определяем изменение значений в зависимости от области захвата
        delta_width = delta_height = delta_x = delta_y = 0
        # Обычное изменение размера окна
        if "bottom" in size_grip:
            delta_height = current_y - start_y
        if "right" in size_grip:
            delta_width = current_x - start_x
        # Изменение положения размера окна
        if "top" in size_grip:
            delta_y = current_y - start_y
            delta_height = -delta_y
            if start_height + delta_height < window.min_size[1]:
                continue
        if "left" in size_grip:
            delta_x = current_x - start_x
            delta_width = -delta_x
            if start_width + delta_width < window.min_size[0]:
                continue

        if delta_x or delta_y:
            # Изменяем положение окна
            window.move(start_win_x + delta_x, start_win_y + delta_y)
        # Изменяем размер окна
        window.resize(start_width + delta_width, start_height + delta_height)

        time.sleep(0.005)


def move_to_cursor(window: webview.Window) -> None:
    user32 = windll.user32
    screen_width = user32.GetSystemMetrics(0)
    mouse_x = query_mouse_position()[0]
    window_width = window.width
    window.move(int(mouse_x - (window_width * mouse_x / screen_width)), 0)


def drag_window(window: webview.Window) -> None:
    state_left = windll.user32.GetKeyState(0x01)

    # Определяем начальное положение курсора и окна
    start_x, start_y = query_mouse_position()
    start_win_x = window.x
    start_win_y = window.y

    logger.debug(f"Drag started")

    while True:
        # Пользователь отпустил кнопку мыши
        if windll.user32.GetKeyState(0x01) != state_left:
            logger.debug("Drag finished")
            break

        current_x, current_y = query_mouse_position()

        delta_x = current_x - start_x
        delta_y = current_y - start_y

        window.move(start_win_x + delta_x, start_win_y + delta_y)

        time.sleep(0.005)
