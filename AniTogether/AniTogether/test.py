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
# Путь к файлу с временными данными
os.environ["TEMP_PATH"] = os.path.join(os.environ["APP_DIR"], "temp.txt")
# Версия приложения
os.environ["VERSION"] = "1.0.0-betta.3"
# Сервер
os.environ["HOST"] = "localhost:8080"
# os.environ["HOST"] = "anitogetherserver.onrender.com"

os.environ["CONSOLE"] = "1"


import logger  # noqa
from web.app import app  # noqa


app.run(debug=True, port=8080)
