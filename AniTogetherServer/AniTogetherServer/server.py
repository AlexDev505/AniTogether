from __future__ import annotations

import json
import typing as ty

import websockets

import rooms
from loguru import logger


if ty.TYPE_CHECKING:
    from websockets import WebSocketServerProtocol
    from rooms import Room, ROOM_ID


async def server(websocket: WebSocketServerProtocol):
    logger.opt(colors=True).debug(f"New client: <r>{websocket.id}</r>")
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
            await error(websocket, 4, "unknown command")

    except (json.JSONDecodeError, AssertionError):
        await error(websocket, 4, "Incorrect message format")
    except (websockets.ConnectionClosedOK, ConnectionResetError):
        pass
    finally:
        logger.opt(colors=True).debug(f"Client <r>{websocket.id}</r> disconnected")


async def create_room(websocket: WebSocketServerProtocol, data: dict) -> None:
    if (title_id := data.get("title_id")) is None:
        return await error(websocket, 1, "title_id not passed")
    elif (episode := data.get("episode")) is None:
        return await error(websocket, 1, "episode not passed")

    room_id = rooms.create_room(websocket, title_id, episode)

    try:
        await send(
            websocket,
            "init",
            room_id=room_id,
            me=0,
            members=[0],
            title_id=title_id,
            episode=episode,
        )
        await room_handler(websocket, room_id)
    finally:
        await leave_room(websocket, room_id)


async def join_room(websocket: WebSocketServerProtocol, data: dict) -> None:
    if not (room_id := data.get("room_id")):
        return await error(websocket, 1, "room_id not passed")

    try:
        room = rooms.join_room(websocket, room_id)
    except KeyError as err:
        return await error(websocket, 5, str(err))

    user = room.members[-1]

    try:
        await send(
            websocket,
            "init",
            room_id=room_id,
            me=user.id,
            members=[member.id for member in room.members],
            title_id=room.title_id,
            episode=room.episode,
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
            await error(websocket, 4, "Incorrect message format")
            continue

        logger.trace(f"Command from user {websocket.id}: {data}")

        if data.get("command") == "pause":
            await pause(websocket, room)
        elif data.get("command") == "play":
            await play(websocket, room, data)
        elif data.get("command") == "seek":
            await seek(websocket, room, data)
        elif data.get("command") == "set_episode":
            await set_episode(websocket, room, data)
        elif data.get("command") == "playback_time_request":
            await playback_time_request(websocket, room)
        elif data.get("command") == "playback_time_request_answer":
            await playback_time_request_answer(websocket, room, data)
        elif data.get("command") == "pause_request":
            await pause_request(websocket, room)
        elif data.get("command") == "rewind_back_request":
            await rewind_back_request(websocket, room)
        elif data.get("command") == "leave_room":
            await leave_room(websocket, room_id)
        else:
            await error(websocket, 4, "unknown command")


async def pause(websocket: WebSocketServerProtocol, room: Room) -> None:
    if not room.is_hoster(websocket):
        return

    room.playing = False
    await broadcast(websocket, room, "pause")


async def play(websocket: WebSocketServerProtocol, room: Room, data: dict) -> None:
    if not room.is_hoster(websocket):
        return

    if (send_time := data.get("time")) is None:
        return await error(websocket, 1, "time not passed")
    elif (playback_time := data.get("playback_time")) is None:
        return await error(websocket, 1, "playback_time not passed")

    room.playing = True
    await broadcast(
        websocket, room, "play", time=send_time, playback_time=playback_time
    )


async def seek(websocket: WebSocketServerProtocol, room: Room, data: dict) -> None:
    if not room.is_hoster(websocket):
        return

    if (send_time := data.get("time")) is None:
        return await error(websocket, 1, "time not passed")
    elif (playback_time := data.get("playback_time")) is None:
        return await error(websocket, 1, "playback_time not passed")

    room.playing = False
    await broadcast(
        websocket, room, "seek", time=send_time, playback_time=playback_time
    )


async def set_episode(
    websocket: WebSocketServerProtocol, room: Room, data: dict
) -> None:
    if not room.is_hoster(websocket):
        return

    if (episode := data.get("episode")) is None:
        return await error(websocket, 3, "episode not passed")

    room.episode = episode
    await broadcast(websocket, room, "set_episode", episode=episode)


async def playback_time_request(websocket: WebSocketServerProtocol, room: Room) -> None:
    user = room.get_by_ws(websocket)
    await send(room.members[0].ws, "playback_time_request", user_id=user.id)


async def playback_time_request_answer(
    websocket: WebSocketServerProtocol, room: Room, data: dict
) -> None:
    if not room.is_hoster(websocket):
        return

    if (send_time := data.get("time")) is None:
        return await error(websocket, 1, "time not passed")
    elif (playback_time := data.get("playback_time")) is None:
        return await error(websocket, 1, "playback_time not passed")
    elif (user_id := data.get("user_id")) is None:
        return await error(websocket, 1, "user_id not passed")

    if not (user := room.get_by_id(user_id)):
        return await error(websocket, 2, "Пользователь не найден")

    await send(
        user.ws,
        "playback_time_request_answer",
        time=send_time,
        playback_time=playback_time,
        playing=room.playing,
    )


async def pause_request(websocket: WebSocketServerProtocol, room: Room) -> None:
    user = room.get_by_ws(websocket)
    await send(room.members[0].ws, "pause_request", sender=user.id)


async def rewind_back_request(websocket: WebSocketServerProtocol, room: Room) -> None:
    user = room.get_by_ws(websocket)
    await send(room.members[0].ws, "rewind_back_request", sender=user.id)


async def leave_room(websocket: WebSocketServerProtocol, room_id: ROOM_ID) -> None:
    leaved_user, room, hoster_changed = rooms.leave_room(websocket, room_id)
    await broadcast(websocket, room, "leave_room", user_id=leaved_user.id)
    if hoster_changed:
        await send(room.members[0].ws, "hoster_promotion")


async def error(websocket: WebSocketServerProtocol, code: int, message: str) -> None:
    """
    Send an error message.
    """
    await send(websocket, "error", code=code, message=message)


async def broadcast(
    websocket: WebSocketServerProtocol,
    room: Room,
    event_type: str,
    exclude_sender: bool = True,
    **data: ty.Any,
) -> None:
    event = dict(type=event_type, **data)
    try:
        websockets.broadcast(
            (
                member.ws
                for member in room.members
                if member.ws.id != websocket.id or not exclude_sender
            ),
            json.dumps(event),
        )
    except ConnectionResetError:
        pass


async def send(
    websocket: WebSocketServerProtocol, event_type: str, **data: ty.Any
) -> None:
    event = dict(type=event_type, **data)
    await websocket.send(json.dumps(event))
