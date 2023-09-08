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
os.environ["VERSION"] = "1.0.0-betta.4"
# Сервер
# os.environ["HOST"] = "localhost:8080"
os.environ["HOST"] = "anitogetherserver.onrender.com"

os.environ["DEBUG"] = "1"


from logger import logger  # noqa


def main() -> None:
    import webview
    from js_api import JSApi
    from web.app import app

    updater_path = os.path.join(
        os.environ["APP_DIR"], f"AniTogetherUpdate.{os.environ['VERSION']}.exe"
    )
    if os.path.isfile(updater_path):
        os.remove(updater_path)
    del updater_path

    def _on_loaded():
        logger.info(f"Загружена страница {window.get_current_url()}")

    def _on_closed():
        logger.info("Application closed\n\n")

    def _on_shown():
        logger.info("Application started")

    logger.info("Launching...")

    js_api = JSApi()
    app.config["TOKEN"] = webview.token
    window = webview.create_window(
        "AniTogether",
        app,
        width=1000,
        height=650,
        frameless=True,
        easy_drag=False,
        min_size=(820, 520),
        background_color="#000",
        js_api=js_api,
    )

    # Добавляем обработчики событий
    window.events.loaded += _on_loaded
    window.events.closed += _on_closed
    window.events.shown += _on_shown

    webview.start(debug=bool(int(os.environ["DEBUG"])))


if __name__ == "__main__":
    main()
