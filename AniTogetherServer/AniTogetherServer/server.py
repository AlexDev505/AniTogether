from __future__ import annotations

import json
import typing as ty

import websockets

import rooms


if ty.TYPE_CHECKING:
    from websockets import WebSocketServerProtocol
    from rooms import Room, ROOM_ID


async def server(websocket: WebSocketServerProtocol):
    try:
        message = await websocket.recv()
        data: dict = json.loads(message)
        assert type(data) is dict
        assert "command" in data

        if data.get("command") == "create":
            await create_room(websocket, data)
        elif data.get("command") == "join":
            await join_room(websocket, data)
        else:
            await error(websocket, "unknown command")

    except (json.JSONDecodeError, AssertionError):
        await error(websocket, "Incorrect message format")
    except websockets.ConnectionClosedOK:
        pass


async def create_room(websocket: WebSocketServerProtocol, data: dict) -> None:
    if not (mute_new_members := data.get("mute_new_members")):
        return await error(websocket, "mute_new_members not passed")
    room_id = rooms.create_room(websocket, mute_new_members)

    try:
        await send(websocket, "init", room_id=room_id, me=0, members=[0])
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

    user = room.members[-1]

    try:
        await send(
            websocket,
            "init",
            room_id=room_id,
            me=user.id,
            members=[member.id for member in room.members],
        )
        await broadcast(websocket, room, "join", user_id=user.id)
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
        elif data.get("command") == "pause_request":
            await pause_request(websocket, room)
        elif data.get("command") == "rewind_back_request":
            await rewind_back_request(websocket, room)
        elif data.get("command") == "kick":
            await kick(websocket, room, data)
        elif data.get("command") == "mute":
            await set_mute(websocket, room, data, True)
        elif data.get("command") == "unmute":
            await set_mute(websocket, room, data, False)
        elif data.get("command") == "leave_room":
            await leave_room(websocket, room_id)
        else:
            await error(websocket, "unknown command")


async def pause(websocket: WebSocketServerProtocol, room: Room) -> None:
    await broadcast(websocket, room, "pause")


async def play(websocket: WebSocketServerProtocol, room: Room, data: dict) -> None:
    if not (send_time := data.get("time")):
        return await error(websocket, "time not passed")
    elif not (playback_time := data.get("playback_time")):
        return await error(websocket, "playback_time not passed")

    await broadcast(
        websocket, room, "play", time=send_time, playback_time=playback_time
    )


async def seek(websocket: WebSocketServerProtocol, room: Room, data: dict) -> None:
    if not (send_time := data.get("time")):
        return await error(websocket, "time not passed")
    elif not (playback_time := data.get("playback_time")):
        return await error(websocket, "playback_time not passed")

    await broadcast(
        websocket, room, "seek", time=send_time, playback_time=playback_time
    )


async def playback_time_request(websocket: WebSocketServerProtocol, room: Room) -> None:
    user = room.get_by_ws(websocket)
    await send(room.members[0].ws, "playback_time_request", user_id=user.id)


async def playback_time_request_answer(
    websocket: WebSocketServerProtocol, room: Room, data: dict
) -> None:
    if not (send_time := data.get("time")):
        return await error(websocket, "time not passed")
    elif not (playback_time := data.get("playback_time")):
        return await error(websocket, "playback_time not passed")
    elif not (user_id := data.get("user_id")):
        return await error(websocket, "user_id not passed")

    if not (user := room.get_by_id(user_id)):
        return await error(websocket, "Пользователь не найден")

    await send(
        user.ws,
        "playback_time_request_answer",
        time=send_time,
        playback_time=playback_time,
    )


async def pause_request(websocket: WebSocketServerProtocol, room: Room) -> None:
    user = room.get_by_ws(websocket)
    if user.muted:
        return await error(websocket, "Вы не можете отправлять сигналы")
    await send(room.members[0].ws, "pause_request")


async def rewind_back_request(websocket: WebSocketServerProtocol, room: Room) -> None:
    user = room.get_by_ws(websocket)
    if user.muted:
        return await error(websocket, "Вы не можете отправлять сигналы")
    await send(room.members[0].ws, "rewind_back_request")


async def kick(websocket: WebSocketServerProtocol, room: Room, data: dict) -> None:
    if not (user_id := data.get("user_id")):
        return await error(websocket, "user_id not passed")

    if not (user := room.get_by_id(user_id)):
        return await error(websocket, "Пользователь не найден")

    await broadcast(websocket, room, "kick", exclude_sender=False, user_id=user_id)
    room.members.remove(user)


async def set_mute(
    websocket: WebSocketServerProtocol, room: Room, data: dict, value: bool
) -> None:
    if not (user_id := data.get("user_id")):
        return await error(websocket, "user_id not passed")

    if not (user := room.get_by_id(user_id)):
        return await error(websocket, "Пользователь не найден")

    user.muted = value


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
    room: Room,
    event_type: str,
    exclude_sender: bool = True,
    **data: ty.Any,
) -> None:
    event = dict(type=event_type, **data)
    await websockets.broadcast(
        (
            member.ws
            for member in room.members
            if member.ws.id != websocket.id or not exclude_sender
        ),
        json.dumps(event),
    )


async def send(
    websocket: WebSocketServerProtocol, event_type: str, **data: ty.Any
) -> None:
    event = dict(type=event_type, **data)
    await websocket.send(json.dumps(event))
