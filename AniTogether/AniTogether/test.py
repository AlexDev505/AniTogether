import asyncio
import anilibria

import locale
import sys

import mpv
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

client = anilibria.AniLibriaClient()


async def main():
    title = (await client.search_titles(search=["адский рай"])).list[0]
    print(title)

    await client.close()


asyncio.run(main())


# URL = "https://cache.libria.fun/videos/media/ts/9520/1/1080/2c461de4505541e4e2f84a6e3ef5f6c0.m3u8"
#
#
# class Test(QMainWindow):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#
#         self.setGeometry(100, 100, 400, 260)
#         self.container = QWidget(self)
#         self.setCentralWidget(self.container)
#
#         self.player = mpv.MPV(
#             wid=str(int(self.container.winId())),
#             log_handler=None,
#             loglevel="debug",
#             input_default_bindings=True,
#             input_vo_keyboard=True,
#         )
#
#         @self.player.event_callback(mpv.MpvEventID.START_FILE)
#         def my_f_binding(*args):
#             print("start", args)
#
#         self.player.play(URL)
#
#         self.paused = False
#
#     def keyPressEvent(self, event):
#         if event.key() == Qt.Key.Key_Right:
#             self.player.seek(10)
#         elif event.key() == Qt.Key.Key_Left:
#             self.player.seek(-10)
#         elif event.key() == Qt.Key.Key_Space:
#             self.paused = not self.paused
#             self.player._set_property("pause", self.paused)
#             # print(self.player.osd.)
#         event.accept()
#
#
# app = QApplication(sys.argv)
#
#
# locale.setlocale(locale.LC_NUMERIC, "C")
# win = Test()
# win.show()
# sys.exit(app.exec())
