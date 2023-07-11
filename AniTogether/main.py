import asyncio
import atexit
import os
import sys
from functools import partial

import qasync


# CONFIG SETUP
# Путь к директории приложения
os.environ["APP_DIR"] = os.path.join(os.environ["LOCALAPPDATA"], "AniTogether")
if not os.path.exists(os.environ["APP_DIR"]):
    os.mkdir(os.environ["APP_DIR"])
# Путь к файлу отладки
os.environ["DEBUG_PATH"] = os.path.join(os.environ["APP_DIR"], "debug.log")
# Версия приложения
os.environ["VERSION"] = "0.0.0"


from logger import logger  # noqa

from main_window import MainWindow  # noqa


# Настройка обработчика ошибок


@logger.catch
def exception_hook(exception_type, value, __):
    if exception_type is KeyboardInterrupt:
        sys.exit()
    raise Exception from value


sys.excepthook = exception_hook


def close_future(future, loop):
    loop.call_later(10, future.cancel)
    future.cancel()


async def main():
    logger.debug("Creating application")

    loop = asyncio.get_event_loop()
    future = asyncio.Future()

    app = qasync.QApplication.instance()
    if hasattr(app, "aboutToQuit"):
        getattr(app, "aboutToQuit").connect(partial(close_future, future, loop))

    window = MainWindow()
    window.show()

    logger.info("Starting application")

    await future
    return True


def exit_():
    logger.info("Application closed\n\n")


atexit.register(exit_)


if __name__ == "__main__":
    try:
        qasync.run(main())
    except asyncio.exceptions.CancelledError:
        sys.exit(0)
