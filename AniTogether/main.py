import atexit
import os
import sys

from PyQt6.QtWidgets import QApplication

from main_window import MainWindow


# CONFIG SETUP
# Путь к директории приложения
os.environ["APP_DIR"] = "../"
# os.environ["APP_DIR"] = os.path.join(os.environ["LOCALAPPDATA"], "AniTogether")
if not os.path.exists(os.environ["APP_DIR"]) and False:  # TODO
    os.mkdir(os.environ["APP_DIR"])
# Путь к файлу отладки
os.environ["DEBUG_PATH"] = os.path.join(os.environ["APP_DIR"], "debug.log")
# Версия приложения
os.environ["VERSION"] = "0.0.0"


from logger import logger  # noqa


@logger.catch
def exception_hook(exception_type, value, __):
    if exception_type is KeyboardInterrupt:
        sys.exit()
    raise Exception from value


sys.excepthook = exception_hook


def main():
    logger.debug("Create application")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    logger.info("Start application")
    app.exec()


def exit_():
    logger.info("Application closed\n\n")


atexit.register(exit_)


if __name__ == '__main__':
    main()
