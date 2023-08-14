from __future__ import annotations

import secrets
import typing as ty
from dataclasses import dataclass
from loguru import logger

from exceptions import RoomDoesNotExists, UserNotAMemberOfRoom


if ty.TYPE_CHECKING:
    from websockets import WebSocketServerProtocol as Ws

    ROOM_ID = str
    USER_ID = int


ROOMS: dict[ROOM_ID, Room] = {}


@dataclass
class User:
    ws: Ws
    id: USER_ID


@dataclass
class Room:
    room_id: ROOM_ID
    members: list[User]
    title_id: int
    episode: str
    playing: bool = False

    def get_by_ws(self, ws: Ws) -> User | None:
        for member in self.members:
            if member.ws.id == ws.id:
                return member

    def get_by_id(self, user_id: USER_ID) -> User | None:
        for member in self.members:
            if member.id == user_id:
                return member

    def is_hoster(self, ws: Ws) -> bool:
        return self.members[0].ws.id == ws.id


def generate_room_id() -> ROOM_ID:
    """
    Создаёт случай6ный идентификатор комнаты.
    """
    token_len = 5
    errors = 0
    room_id = secrets.token_urlsafe(token_len)
    while room_id in ROOMS:
        errors += 1
        if errors == 3:
            token_len += 1
            errors = 0
        room_id = secrets.token_urlsafe(token_len)
    return room_id


def get_room(room_id: ROOM_ID) -> Room:
    """
    Возвращает экземпляр комнаты по идентификатору.
    :raises: RoomDoesNotExists
    """
    if not (room := ROOMS.get(room_id)):
        raise RoomDoesNotExists()
    return room


def create_room(ws: Ws, title_id: int, episode: str) -> ROOM_ID:
    """
    Создает новую комнату.
    :return: Идентификатор комнаты.
    """
    room_id = generate_room_id()
    ROOMS[room_id] = Room(room_id, [User(ws=ws, id=0)], title_id, episode)
    logger.opt(colors=True).debug(
        f"Client <r>{ws.id}</r> created room <y>{room_id}</y>"
    )
    return room_id


def join_to_room(ws: Ws, room_id: ROOM_ID) -> Room:
    """
    Подключает клиента к комнате.
    :raises: RoomDoesNotExists
    """
    if not (room := ROOMS.get(room_id)):
        raise RoomDoesNotExists()

    last_user = room.members[-1]
    user = User(ws=ws, id=last_user.id + 1)
    room.members.append(user)
    logger.opt(colors=True).debug(
        f"Client <r>{ws.id}</r> joined to room <y>{room_id}</y>"
    )
    return room


def leave_room(ws: Ws, room_id: ROOM_ID) -> tuple[User, Room, bool]:
    """
    Исключает клиента из комнаты.
    :returns: Экземпляр исключенного клиента,
        экземпляр комнаты,
        был ли исключенный хостером.
    :raises: RoomDoesNotExists, UserNotAMemberOfRoom
    """
    if not (room := ROOMS.get(room_id)):
        raise RoomDoesNotExists()

    hoster_changed = False
    for i, member in enumerate(room.members):
        if member.ws.id == ws.id:
            if i == 0:
                hoster_changed = True
            leaved_user = member
            room.members.remove(member)
            logger.opt(colors=True).debug(
                f"Client <r>{ws.id}</r> left room <y>{room_id}</y>"
            )
            break
    else:
        raise UserNotAMemberOfRoom()

    if len(room.members) == 0:
        delete_room(room_id)
        hoster_changed = False

    return leaved_user, room, hoster_changed


def delete_room(room_id: ROOM_ID):
    """
    Удаляет комнату.
    :return: RoomDoesNotExists
    """
    if not ROOMS.get(room_id):
        raise RoomDoesNotExists()
    logger.opt(colors=True).debug(f"Room <y>{room_id}</y> deleted")
    del ROOMS[room_id]


__all__ = [
    "get_room",
    "create_room",
    "join_to_room",
    "leave_room",
    "Room",
    "User",
    "ROOM_ID",
    "USER_ID",
]
