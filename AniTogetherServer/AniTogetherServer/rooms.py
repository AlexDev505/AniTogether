from __future__ import annotations

import secrets
import typing as ty
from dataclasses import dataclass


if ty.TYPE_CHECKING:
    from websockets import WebSocketServerProtocol as Ws

    ROOM_ID = str
    USER_ID = int


ROOMS: dict[ROOM_ID, Room] = {}


@dataclass
class User:
    ws: Ws
    id: USER_ID
    muted: bool


@dataclass
class Room:
    room_id: ROOM_ID
    members: list[User]
    mute_new_members: bool

    def get_by_ws(self, ws: Ws) -> User | None:
        for member in self.members:
            if member.ws.id == ws.id:
                return member

    def get_by_id(self, user_id: USER_ID) -> User | None:
        for member in self.members:
            if member.id == user_id:
                return member


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


def get_room(room_id: ROOM_ID) -> Room:
    if not (room := ROOMS.get(room_id)):
        raise KeyError("Комната не существует")
    return room


def create_room(ws: Ws, mute_new_members: bool) -> ROOM_ID:
    room_id = generate_room_id()
    ROOMS[room_id] = Room(room_id, [User(ws=ws, id=0, muted=False)], mute_new_members)
    return room_id


def join_room(ws: Ws, room_id: ROOM_ID) -> Room:
    if not (room := ROOMS.get(room_id)):
        raise KeyError("Комната не существует")

    last_user = room.members[-1]
    user = User(ws=ws, id=last_user.id + 1, muted=room.mute_new_members)
    room.members.append(user)
    return room


def leave_room(ws: Ws, room_id: ROOM_ID) -> tuple[User, Room]:
    if not (room := ROOMS.get(room_id)):
        raise KeyError("Комната не существует")

    for member in room.members:
        if member.ws.id == ws.id:
            leaved_user = member
            room.members.remove(member)
            break
    else:
        raise RuntimeError("You are not a member of the room")

    if len(room.members) == 0:
        delete_room(room_id)

    return leaved_user, room


def delete_room(room_id: ROOM_ID) -> bool:
    if not (room := ROOMS.get(room_id)):
        raise KeyError("Комната не существует")
    del ROOMS[room_id]
    return True


__all__ = [
    "get_room",
    "create_room",
    "join_room",
    "leave_room",
    "Room",
    "User",
    "ROOM_ID",
    "USER_ID",
]
