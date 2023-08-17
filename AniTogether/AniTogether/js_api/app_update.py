from __future__ import annotations

import os
import time
import typing as ty

import orjson
import requests
from loguru import logger
from ctypes import windll


if ty.TYPE_CHECKING:
    import webview


@logger.catch
def update_app(window: webview.Window) -> dict | None:
    logger.info("App updating started")

    try:
        logger.debug("Getting last release")
        last_release = get_last_release()
    except (requests.RequestException, orjson.JSONDecodeError, IndexError) as err:
        logger.error(f"Getting last release failed. {type(err).__name__}: {err}")
        return dict(message="не удалось получить информацию о релизах")

    last_version = last_release["tag_name"]
    logger.opt(colors=True).debug(f"Last release: <y>{last_release['html_url']}</y>")
    if last_version == os.environ["VERSION"]:
        logger.debug("The same version is installed now")
        return dict(message="новейшая версия уже установлена")

    updater_file_name = f"AniTogetherUpdate.{last_version}.exe"
    for asset in last_release["assets"]:
        if updater_file_name == asset["name"]:
            updater_url = asset["browser_download_url"]
            break
    else:
        logger.opt(colors=True).error(f"File <y>{updater_file_name}</y>")
        return dict(message="не удалось получить файлы обновления")

    updater_path = os.path.join(os.environ["APP_DIR"], updater_file_name)
    logger.opt(colors=True).debug(
        f"Downloading updater file. <y>url={updater_url} path={updater_path}</y>"
    )
    if not download_updater(updater_url, updater_path):
        return dict(message="ошибка при скачивании файлов обновления")

    logger.info("Running updater")
    windll.shell32.ShellExecuteW(None, "runas", updater_path, None, None, 1)
    logger.info("Closing app")
    window.destroy()


def get_last_release() -> dict:
    """
    :raises: requests.RequestException, orjson.JSONDecodeError, IndexError
    """
    response = requests.get(
        "https://api.github.com/repos/AlexDev505/AniTogether/releases"
    )
    if response.status_code != 200:
        raise requests.RequestException(f"Response status code: {response.status_code}")
    releases = orjson.loads(response.text)
    return releases[0]


def download_updater(updater_url: str, updater_path: str, _retries: int = 0) -> bool:
    try:
        response = requests.get(updater_url)
        if response.status_code != 200:
            logger.error(
                "Updater downloading failed. "
                f"Response status code {response.status_code}"
            )
            return False
        with open(updater_path, "wb") as file:
            file.write(response.content)
        return True
    except IOError as err:
        logger.error(
            f"Updater downloading failed on {_retries} retry. "
            f"{type(err).__name__}: {err}"
        )
        if _retries == 3:
            return False
        time.sleep(10 * _retries)
        return download_updater(updater_url, updater_path, _retries + 1)
