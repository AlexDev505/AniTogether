from __future__ import annotations

import secrets
import typing as ty
from dataclasses import dataclass


if ty.TYPE_CHECKING:
    from websockets import WebSocketServerProtocol as Ws

    ROOM_ID = str
    USER_ID = int


ROOMS: dict[ROOM_ID, list[User]] = {}


@dataclass
class User:
    ws: Ws
    id: USER_ID
    username: str

    def to_dict(self) -> dict:
        return dict(id=self.id, username=self.username)


def generate_room_id() -> ROOM_ID:
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


def get_room(room_id: ROOM_ID) -> list[User]:
    if not (room := ROOMS.get(room_id)):
        raise KeyError("Room not found")
    return room


def create_room(ws: Ws, username: str) -> ROOM_ID:
    room_id = generate_room_id()
    user = User(ws=ws, id=0, username=username)
    ROOMS[room_id] = [user]
    return room_id


def join_room(ws: Ws, username: str, room_id: ROOM_ID) -> list[User]:
    if not (room := ROOMS.get(room_id)):
        raise KeyError("Room not found")

    last_user = room[-1]
    user = User(ws=ws, id=last_user.id + 1, username=username)
    room.append(user)
    return room


def leave_room(ws: Ws, room_id: ROOM_ID) -> tuple[User, list[User]]:
    if not (room := ROOMS.get(room_id)):
        raise KeyError("Room not found")

    for user in room:
        if user.ws.id == ws.id:
            leaved_user = user
            room.remove(user)
            break
    else:
        raise RuntimeError("You are not a member of the room")

    if len(room) == 0:
        delete_room(room_id)

    return leaved_user, room


def delete_room(room_id: ROOM_ID) -> bool:
    if not (room := ROOMS.get(room_id)):
        raise KeyError("Room not found")
    del ROOMS[room_id]
    return True


__all__ = [
    "get_room",
    "create_room",
    "join_room",
    "leave_room",
    "User",
    "ROOM_ID",
    "USER_ID",
]
