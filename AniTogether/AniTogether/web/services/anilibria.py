import re
import time
import typing as ty

import orjson
import requests
from loguru import logger

from .tools import pretty_view


DARKLIBRIA_URL = "https://darklibria.it/redirect/mirror/1"
STORAGE_URL = "https://static.wwnd.space"
api_url = "https://api.anilibria.tv/v3"

_mirror_getting: bool = False


class AnilibriaError(Exception):
    def __init__(self, code: int, message: str = ""):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


class AnilibriaApiError(AnilibriaError):
    pass


class AnilibriaMirrorError(AnilibriaError):
    pass


def get_mirror_url() -> str:
    global _mirror_getting
    if _mirror_getting:
        old_api_url = str(api_url)
        while _mirror_getting or old_api_url == api_url:
            time.sleep(0.1)
        return api_url

    _mirror_getting = True

    try:
        response = requests.get(DARKLIBRIA_URL)
        if response.status_code != 200:
            raise AnilibriaMirrorError(response.status_code, "Mirror updating failed")
        response = response.text
        if not (match := re.search(r'<link rel="canonical" href="(.+)"/>', response)):
            raise AnilibriaMirrorError(2, "Could not find mirror link")
        mirror_url = match.group(1) + "/api/v3"
        logger.opt(colors=True).debug(f"New Anilibria api url: <r>{mirror_url}</r>")
        return mirror_url
    except (requests.exceptions.SSLError, requests.ConnectionError) as err:
        raise AnilibriaMirrorError(1, f"Darklibria unavailable: {type(err).__name__}")
    except requests.exceptions.RequestException as err:
        raise AnilibriaMirrorError(0, f"Darklibria unavailable: {type(err).__name__}")
    finally:
        _mirror_getting = False


def _send_request(query: str, *, _retries: int = 0, **data: ty.Any) -> dict:
    global api_url

    logger.opt(colors=True).debug(
        f"Anilibria request: <r>{query}</r> with params {pretty_view(data)}"
    )

    try:
        response = requests.get(f"{api_url}{query}", params=data)
    except (requests.exceptions.SSLError, requests.ConnectionError) as err:
        err = AnilibriaApiError(
            1, f"Anilibria({api_url}) unavailable: {type(err).__name__}"
        )
        if _retries == 3:
            raise err
        else:
            logger.error(f"{type(err).__name__}: {str(err)}")

        api_url = get_mirror_url()
        return _send_request(query, **data, _retries=_retries + 1)
    except requests.exceptions.RequestException as err:
        raise AnilibriaApiError(
            0, f"Anilibria({api_url}) unavailable: {type(err).__name__}"
        )

    try:
        data = orjson.loads(response.text)
    except orjson.JSONDecodeError:
        raise AnilibriaApiError(2, f"Unable to read response: {response.text}")

    if "error" in data:
        raise AnilibriaApiError(data["error"]["code"], data["error"]["message"])

    return data


def get_title(title_id) -> dict:
    return _send_request("/title", id=title_id)


def search_titles(query: str, items_per_page: int = 10) -> list[dict]:
    result = _send_request("/title/search", search=query, items_per_page=items_per_page)
    return result["list"]
