import os

import sys
from loguru import logger


try:  # Удаление настроек логгера по умолчанию
    logger.remove(0)
except ValueError:
    pass


def formatter(_) -> str:
    return (
        "<lvl><n>[{level.name} </n></lvl>"
        "<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</g>"
        "<lvl><n>]</n></lvl> "
        "<lvl><n>{message}</n></lvl>\n{exception}"
    )


logger.add(
    sys.stdout,
    colorize=True,
    format=formatter,
    level=os.environ.get("LOGGING_LEVEL", "DEBUG"),
)

if loging_file := os.environ.get("LOGGING_FILE"):
    logger.add(loging_file, colorize=False, format=formatter, level="DEBUG")

# Настройка цветов
logger.level("INFO", color="<cyan><bold>")
logger.level("TRACE", color="<lk>")
