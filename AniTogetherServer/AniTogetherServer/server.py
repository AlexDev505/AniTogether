from __future__ import annotations

import json
import typing as ty

import websockets

import rooms


if ty.TYPE_CHECKING:
    from websockets import WebSocketServerProtocol
    from rooms import User, ROOM_ID

    ROOM = list[User]


async def server(websocket: WebSocketServerProtocol):
    try:
        message = await websocket.recv()
        data: dict = json.loads(message)
        assert type(data) is dict
        assert "command" in data

        if data.get("command") == "create":
            await create_room(websocket)
        elif data.get("command") == "join":
            await join_room(websocket, data)
        else:
            await error(websocket, "unknown command")

    except (json.JSONDecodeError, AssertionError):
        await error(websocket, "Incorrect message format")
    except websockets.ConnectionClosedOK:
        pass


async def create_room(websocket: WebSocketServerProtocol) -> None:
    room_id = rooms.create_room(websocket)

    try:
        await send(websocket, "init", room_id=room_id)
        await room_handler(websocket, room_id)
    finally:
        await leave_room(websocket, room_id)


async def join_room(websocket: WebSocketServerProtocol, data: dict) -> None:
    if not (room_id := data.get("room_id")):
        return await error(websocket, "room_id not passed")

    try:
        room = rooms.join_room(websocket, room_id)
    except KeyError as err:
        raise ValueError(str(err))

    try:
        await broadcast(
            websocket,
            room,
            "join",
            exclude_sender=False,
            members=[member.id for member in room],
        )
        await room_handler(websocket, room_id)
    finally:
        await leave_room(websocket, room_id)


async def room_handler(websocket: WebSocketServerProtocol, room_id: ROOM_ID) -> None:
    room = rooms.get_room(room_id)

    async for message in websocket:
        try:
            data: dict = json.loads(message)
            assert type(data) is dict
            assert "command" in data
        except (json.JSONDecodeError, AssertionError):
            await error(websocket, "Incorrect message format")
            continue

        if data.get("command") == "pause":
            await pause(websocket, room)
        elif data.get("command") == "play":
            await play(websocket, room, data)
        elif data.get("command") == "seek":
            await seek(websocket, room, data)
        elif data.get("command") == "playback_time_request":
            await playback_time_request(websocket, room)
        elif data.get("command") == "playback_time_request_answer":
            await playback_time_request_answer(websocket, room, data)
        elif data.get("command") == "kick":
            await kick(websocket, room, data)
        else:
            await error(websocket, "unknown command")


async def pause(websocket: WebSocketServerProtocol, room: ROOM) -> None:
    await broadcast(websocket, room, "pause")


async def play(websocket: WebSocketServerProtocol, room: ROOM, data: dict) -> None:
    if not (send_time := data.get("time")):
        return await error(websocket, "time not passed")
    elif not (playback_time := data.get("playback_time")):
        return await error(websocket, "playback_time not passed")

    await broadcast(
        websocket, room, "play", time=send_time, playback_time=playback_time
    )


async def seek(websocket: WebSocketServerProtocol, room: ROOM, data: dict) -> None:
    if not (send_time := data.get("time")):
        return await error(websocket, "time not passed")
    elif not (playback_time := data.get("playback_time")):
        return await error(websocket, "playback_time not passed")

    await broadcast(
        websocket, room, "seek", time=send_time, playback_time=playback_time
    )


async def playback_time_request(websocket: WebSocketServerProtocol, room: ROOM) -> None:
    for member in room:
        if member.ws.id == websocket.id:
            user = member
            break
    else:
        return await error(websocket, "You are not a member of the room")

    await send(room[0].ws, "playback_time_request", user_id=user.id)


async def playback_time_request_answer(
    websocket: WebSocketServerProtocol, room: ROOM, data: dict
) -> None:
    if not (send_time := data.get("time")):
        return await error(websocket, "time not passed")
    elif not (playback_time := data.get("playback_time")):
        return await error(websocket, "playback_time not passed")
    elif not (user_id := data.get("user_id")):
        return await error(websocket, "user_id not passed")

    for member in room:
        if member.id == user_id:
            user = member
            break
    else:
        return await error(websocket, "user not found")

    await send(
        user.ws,
        "playback_time_request_answer",
        time=send_time,
        playback_time=playback_time,
    )


async def kick(websocket: WebSocketServerProtocol, room: ROOM, data: dict) -> None:
    if not (user_id := data.get("user_id")):
        return await error(websocket, "user_id not passed")

    for member in room:
        if member.id == user_id:
            user = member
            break
    else:
        return await error(websocket, "User not found")

    await broadcast(websocket, room, "kick", exclude_sender=False, user_id=user_id)
    room.remove(user)


async def leave_room(websocket: WebSocketServerProtocol, room_id: ROOM_ID) -> None:
    leaved_user, room = rooms.leave_room(websocket, room_id)
    await broadcast(websocket, room, "leave_room", user_id=leaved_user.id)


async def error(websocket: WebSocketServerProtocol, message: str) -> None:
    """
    Send an error message.
    """
    await send(websocket, "error", message=message)


async def broadcast(
    websocket: WebSocketServerProtocol,
    room: ROOM,
    event_type: str,
    exclude_sender: bool = True,
    **data: ty.Any,
) -> None:
    event = dict(type=event_type, **data)
    await websockets.broadcast(
        (
            member.ws
            for member in room
            if member.ws.id != websocket.id or not exclude_sender
        ),
        json.dumps(event),
    )


async def send(
    websocket: WebSocketServerProtocol, event_type: str, **data: ty.Any
) -> None:
    event = dict(type=event_type, **data)
    await websocket.send(json.dumps(event))
