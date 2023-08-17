from __future__ import annotations

from datetime import datetime
import json
import typing as ty

import websockets
from loguru import logger

import rooms
from exceptions import (
    AniTogetherError,
    UserNotAMemberOfRoom,
    UnknownCommand,
    IncorrectMessage,
    ParamNotPassed,
)


if ty.TYPE_CHECKING:
    from websockets import WebSocketServerProtocol
    from rooms import Room, ROOM_ID


async def ws_handler(websocket: WebSocketServerProtocol):
    logger.opt(colors=True).debug(f"New client: <r>{websocket.id}</r>")
    try:
        message = await websocket.recv()
        data: dict = json.loads(message)
        assert type(data) is dict
        assert "command" in data

        if data.get("command") == "join":
            await join_to_room(websocket, data)
        else:
            await error(websocket, UnknownCommand())

    except (json.JSONDecodeError, AssertionError):
        await error(websocket, IncorrectMessage())
    except websockets.ConnectionClosedOK:
        pass
    finally:
        logger.opt(colors=True).debug(f"Client <r>{websocket.id}</r> disconnected")


async def join_to_room(websocket: WebSocketServerProtocol, data: dict) -> None:
    if not (room_id := data.get("room_id")):
        return await error(websocket, ParamNotPassed("room_id"))

    try:
        room = rooms.join_to_room(websocket, room_id)
    except AniTogetherError as err:
        return await error(websocket, err)

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
            await error(websocket, IncorrectMessage())
            continue

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
        elif data.get("command") == "server_time_request":
            await server_time_request(websocket, data)
        else:
            await error(websocket, UnknownCommand())


async def pause(websocket: WebSocketServerProtocol, room: Room) -> None:
    if not room.is_hoster(websocket):
        return

    room.playing = False
    await broadcast(websocket, room, "pause")
    logger.opt(colors=True).debug(f"<y>{room.room_id}</y>: paused")


async def play(websocket: WebSocketServerProtocol, room: Room, data: dict) -> None:
    if not room.is_hoster(websocket):
        return

    if (send_time := data.get("time")) is None:
        return await error(websocket, ParamNotPassed("time"))
    elif (playback_time := data.get("playback_time")) is None:
        return await error(websocket, ParamNotPassed("playback_time"))

    room.playing = True
    await broadcast(
        websocket, room, "play", time=send_time, playback_time=playback_time
    )
    logger.opt(colors=True).debug(
        f"<y>{room.room_id}</y>: playing playback_time={playback_time} time={send_time}"
    )


async def seek(websocket: WebSocketServerProtocol, room: Room, data: dict) -> None:
    if not room.is_hoster(websocket):
        return

    if (send_time := data.get("time")) is None:
        return await error(websocket, ParamNotPassed("time"))
    elif (playback_time := data.get("playback_time")) is None:
        return await error(websocket, ParamNotPassed("playback_time"))

    room.playing = False
    await broadcast(
        websocket, room, "seek", time=send_time, playback_time=playback_time
    )
    logger.opt(colors=True).debug(
        f"<y>{room.room_id}</y>: seeking playback_time={playback_time} time={send_time}"
    )


async def set_episode(
    websocket: WebSocketServerProtocol, room: Room, data: dict
) -> None:
    if not room.is_hoster(websocket):
        return

    if (episode := data.get("episode")) is None:
        return await error(websocket, ParamNotPassed("episode"))

    room.episode = episode
    await broadcast(websocket, room, "set_episode", episode=episode)
    logger.opt(colors=True).debug(
        f"<y>{room.room_id}</y>: setting episode to {episode}"
    )


async def playback_time_request(websocket: WebSocketServerProtocol, room: Room) -> None:
    user = room.get_by_ws(websocket)
    await send(room.members[0].ws, "playback_time_request", user_id=user.id)
    logger.opt(colors=True).debug(
        f"<y>{room.room_id}</y>: playback request from {user.id}({user.ws.id})"
    )


async def playback_time_request_answer(
    websocket: WebSocketServerProtocol, room: Room, data: dict
) -> None:
    if not room.is_hoster(websocket):
        return

    if (send_time := data.get("time")) is None:
        return await error(websocket, ParamNotPassed("time"))
    elif (playback_time := data.get("playback_time")) is None:
        return await error(websocket, ParamNotPassed("playback_time"))
    elif (user_id := data.get("user_id")) is None:
        return await error(websocket, ParamNotPassed("user_id"))
    if not (user := room.get_by_id(user_id)):
        return await error(websocket, UserNotAMemberOfRoom())

    await send(
        user.ws,
        "playback_time_request_answer",
        time=send_time,
        playback_time=playback_time,
        playing=room.playing,
    )
    logger.opt(colors=True).debug(
        f"<y>{room.room_id}</y>: playback request answer to {user.id}({user.ws.id}) "
        f"playback_time={playback_time} time={send_time}"
    )


async def pause_request(websocket: WebSocketServerProtocol, room: Room) -> None:
    user = room.get_by_ws(websocket)
    await send(room.members[0].ws, "pause_request", sender=user.id)
    logger.opt(colors=True).debug(
        f"<y>{room.room_id}</y>: pause request from {user.id}({user.ws.id})"
    )


async def rewind_back_request(websocket: WebSocketServerProtocol, room: Room) -> None:
    user = room.get_by_ws(websocket)
    await send(room.members[0].ws, "rewind_back_request", sender=user.id)
    logger.opt(colors=True).debug(
        f"<y>{room.room_id}</y>: rewind back request from {user.id}({user.ws.id})"
    )


async def leave_room(websocket: WebSocketServerProtocol, room_id: ROOM_ID) -> None:
    leaved_user, room, hoster_changed = rooms.leave_room(websocket, room_id)
    await broadcast(websocket, room, "leave_room", user_id=leaved_user.id)
    if hoster_changed:
        await send(room.members[0].ws, "hoster_promotion")
        logger.opt(colors=True).debug(
            f"<y>{room.room_id}</y>: {room.members[0].id}({room.members[0].ws.id}) "
            "is new hoster"
        )


async def server_time_request(websocket: WebSocketServerProtocol, data: dict) -> None:
    if (client_time := data.get("time")) is None:
        return await error(websocket, ParamNotPassed("time"))
    await send(
        websocket,
        "server_time_request_answer",
        client_time=client_time,
        server_time=datetime.utcnow().timestamp(),
    )


async def error(
    websocket: WebSocketServerProtocol,
    exc: AniTogetherError,
) -> None:
    """
    Send an error message.
    """
    await send(websocket, "error", code=exc.code, message=exc.message)
    logger.opt(colors=True).debug(
        f"<r>{websocket.id}</r> raises error: <bold>{type(exc).__name__}: {exc}</bold>"
    )


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
