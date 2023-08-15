import os


# CONFIG SETUP
# Путь к директории приложения
os.environ["APP_DIR"] = os.path.join(os.environ["LOCALAPPDATA"], "AniTogether")
if not os.path.exists(os.environ["APP_DIR"]):
    os.mkdir(os.environ["APP_DIR"])
# Путь к файлу отладки
os.environ["DEBUG_PATH"] = os.path.join(os.environ["APP_DIR"], "debug.log")
# Путь к файлу истории просмотра
os.environ["HISTORY_PATH"] = os.path.join(os.environ["APP_DIR"], "history.csv")
# Версия приложения
os.environ["VERSION"] = "0.0.0"
# Сервер
os.environ["HOST"] = "localhost:8080"
# os.environ["HOST"] = "anitogetherserver.onrender.com"


import logger  # noqa
from web.app import app  # noqa


app.run(debug=True, port=8080)
