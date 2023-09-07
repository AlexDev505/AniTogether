from __future__ import annotations

import http
import json
import os
import re
import typing as ty
from functools import wraps
from loguru import logger

import rooms
from exceptions import ParamNotPassed, RoomDoesNotExists, UnknownCommand, \
    NotCompatibleVersion
from version import Version


if ty.TYPE_CHECKING:
    from exceptions import AniTogetherError

    ANSWER = tuple[http.HTTPStatus, dict, bytes]


COMPATIBLE_VERSION = Version.from_str(os.environ["COMPATIBLE_VERSION"])


async def http_handler(path: str, _request_headers):
    if path == "/healthz":
        return (
            http.HTTPStatus.OK,
            {"Access-Control-Allow-Origin": "*"},
            b"OK\n",
        )
    elif check_command("create_room", path):
        return create_room(parse_args(path))
    elif check_command("get_room", path):
        return get_room(parse_args(path))
    if _request_headers["Connection"] != "Upgrade":
        return error(UnknownCommand())


def check_version(fn):
    @wraps(fn)
    def _wrapper(data: dict) -> ANSWER:
        try:
            version = data.get("version")
            if Version.from_str(version) < COMPATIBLE_VERSION:
                raise ValueError("")
        except (ValueError, TypeError) as err:
            logger.debug(f"Request from not compatible version: {version}")
            return error(NotCompatibleVersion())

        return fn(data)

    return _wrapper


@check_version
def create_room(data: dict) -> ANSWER:
    if (title_id := data.get("title_id")) is None:
        return error(ParamNotPassed("title_id"))
    elif (episode := data.get("episode")) is None:
        return error(ParamNotPassed("episode"))

    room_id = rooms.create_room(title_id, episode)
    return answer(room_id=room_id, title_id=title_id, episode=episode)


@check_version
def get_room(data: dict) -> ANSWER:
    if (room_id := data.get("room_id")) is None:
        return error(ParamNotPassed("room_id"))

    try:
        room = rooms.get_room(room_id)
        return answer(room_id=room_id, title_id=room.title_id, episode=room.episode)
    except RoomDoesNotExists as err:
        return error(err)


def answer(*, status: ty.Literal["ok", "fail"] = "ok", **data: ty.Any) -> ANSWER:
    return (
        http.HTTPStatus.OK,
        {"Access-Control-Allow-Origin": "*"},
        json.dumps(dict(status=status, **data)).encode(),
    )


def error(exc: AniTogetherError) -> ANSWER:
    return answer(status="fail", code=exc.code, message=exc.message)


def check_command(command: str, path: str) -> bool:
    return bool(re.fullmatch(rf"/{command}\?.+", path))


def parse_args(path: str) -> dict:
    args = {}
    for match in re.finditer(r"(.+?)=(.+?)(&|$)", path.split("?", maxsplit=1)[1]):
        value = match.group(2)
        if value.isdigit():
            value = int(value)
        args[match.group(1)] = value
    return args
