import json
import typing as ty

import requests
from loguru import logger

from .tools import pretty_view


STORAGE_URL = "https://static.wwnd.space"
API_URL = "https://api.anilibria.tv/v3"


class AnilibriaError(Exception):
    def __init__(self, code: int, message: str = ""):
        super().__init__(f"code: {code}; message: {message}")
        self.code = code
        self.message = message


class AnilibriaApiError(AnilibriaError):
    pass


class AnilibriaResourceError(AnilibriaError):
    pass


class PosterSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    ORIGINAL = "original"


def _send_request(query: str, **data: ty.Any) -> dict:
    logger.opt(colors=True).debug(
        f"Anilibria request: <r>{query}</r> with params {pretty_view(data)}"
    )
    try:
        response = requests.get(f"{API_URL}{query}", params=data).json()
    except (requests.exceptions.RequestException, json.JSONDecodeError):
        raise AnilibriaApiError(0, "Anilibria api unavailable")
    if "error" in response:
        raise AnilibriaApiError(response["error"]["code"], response["error"]["message"])
    return response


def _download_resource(url: str) -> bytes:
    logger.opt(colors=True).debug(f"Anilibria resource downloading: <r>{url}</r>")
    response = requests.get(f"{STORAGE_URL}{url}")
    if response.status_code != 200:
        raise AnilibriaResourceError(response.status_code, "Resource unavailable")
    return response.content


def get_title(title_id) -> dict:
    return _send_request("/title", id=title_id)


def search_titles(query: str, items_per_page: int = 10) -> list[dict]:
    result = _send_request("/title/search", search=query, items_per_page=items_per_page)
    return result["list"]


def get_poster(title: dict, size: PosterSize = PosterSize.ORIGINAL) -> bytes:
    poster_url = title["posters"][size.value]["url"]
    return _download_resource(poster_url)
