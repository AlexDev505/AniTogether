import json
import time

import websockets
import asyncio
import typing as ty
from loguru import logger

if ty.TYPE_CHECKING:
    EVENT_HANDLER = ty.Callable[[dict], ty.Coroutine[ty.Any]]


def dumps(command: str, **data: ty.Any) -> str:
    return json.dumps(dict(command=command, **data))


async def plug(event: dict) -> ty.Any:
    logger.opt(colors=True).warning(
        f"Handler for event <e>{event['type']}</e> is not installed"
    )


class NetworkClient:
    URI = "ws://localhost:8001"

    def __init__(self):
        self._active = True
        self.websocket: websockets.WebSocketClientProtocol | None = None

        self.room_id: str | None = None
        self.me: int | None = None
        self.is_host: bool = False

        self._init_event_handler: EVENT_HANDLER = plug
        self._join_event_handler: EVENT_HANDLER = plug
        self._pause_event_handler: EVENT_HANDLER = plug
        self._play_event_handler: EVENT_HANDLER = plug
        self._seek_event_handler: EVENT_HANDLER = plug
        self._playback_time_request_event_handler: EVENT_HANDLER = plug
        self._playback_time_request_answer_event_handler: EVENT_HANDLER = plug
        self._pause_request_event_handler: EVENT_HANDLER = plug
        self._rewind_back_request_event_handler: EVENT_HANDLER = plug
        self._kick_event_handler: EVENT_HANDLER = plug
        self._leave_room_event_handler: EVENT_HANDLER = plug
        self._error_event_handler: EVENT_HANDLER = plug

        asyncio.create_task(self._listen())

    async def create_room(self) -> None:
        await self.websocket.send(dumps("create"))

    async def join_to_room(self, room_id: str) -> None:
        await self.websocket.send(dumps("join", room_id=room_id))

    async def pause(self) -> None:
        await self.websocket.send(dumps("pause"))

    async def play(self, playback_time: int) -> None:
        await self.websocket.send(
            dumps("play", time=time.time(), playback_time=playback_time)
        )

    async def seek(self, playback_time: int) -> None:
        await self.websocket.send(
            dumps("seek", time=time.time(), playback_time=playback_time)
        )

    async def playback_time_request(self) -> None:
        await self.websocket.send(dumps("playback_time_request"))

    async def playback_time_request_answer(
        self, playback_time: int, user_id: int
    ) -> None:
        await self.websocket.send(
            dumps(
                "playback_time_request_answer",
                time=time.time(),
                playback_time=playback_time,
                user_id=user_id,
            )
        )

    async def pause_request(self) -> None:
        await self.websocket.send(dumps("pause_request"))

    async def rewind_back_request(self) -> None:
        await self.websocket.send(dumps("rewind_back_request"))

    async def kick(self, user_id: int) -> None:
        await self.websocket.send(dumps("kick", user_id=user_id))

    async def leave_room(self) -> None:
        await self.websocket.send(dumps("leave_room"))

    async def _listen(self) -> None:
        while True:
            if not self._active:
                break

            async with websockets.connect(self.URI) as self.websocket:
                try:
                    async for message in self.websocket:
                        asyncio.create_task(self.handle_message(message))
                except websockets.ConnectionClosed:
                    pass

    async def handle_message(self, message: str) -> None:
        event: dict = json.loads(message)

        if event["type"] == "init":
            await self.__init_event_handler(event)
        elif event["type"] == "join":
            await self._join_event_handler(event)
        elif event["type"] == "pause":
            await self._pause_event_handler(event)
        elif event["type"] == "play":
            await self._play_event_handler(event)
        elif event["type"] == "seek":
            await self._seek_event_handler(event)
        elif event["type"] == "playback_time_request":
            await self._playback_time_request_event_handler(event)
        elif event["type"] == "playback_time_request_answer":
            await self._playback_time_request_answer_event_handler(event)
        elif event["type"] == "pause_request":
            await self._pause_request_event_handler(event)
        elif event["type"] == "rewind_back_request":
            await self._rewind_back_request_event_handler(event)
        elif event["type"] == "kick":
            await self._kick_event_handler(event)
        elif event["type"] == "leave_room":
            await self._leave_room_event_handler(event)
        elif event["type"] == "error":
            await self._error_event_handler(event)
        else:
            await plug(event)

    async def __init_event_handler(self, event: dict) -> None:
        self.room_id = event["room_id"]
        self.me = event["me"]
        if self.me == 0:
            self.is_host = True
        await self._init_event_handler(event)

    def install_init_event_handler(self, handler: EVENT_HANDLER) -> None:
        self._init_event_handler = handler

    def install_join_event_handler(self, handler: EVENT_HANDLER) -> None:
        self._join_event_handler = handler

    def install_pause_event_handler(self, handler: EVENT_HANDLER) -> None:
        self._pause_event_handler = handler

    def install_play_event_handler(self, handler: EVENT_HANDLER) -> None:
        self._play_event_handler = handler

    def install_seek_event_handler(self, handler: EVENT_HANDLER) -> None:
        self._seek_event_handler = handler

    def install_playback_time_request_event_handler(
        self, handler: EVENT_HANDLER
    ) -> None:
        self._playback_time_request_event_handler = handler

    def install_playback_time_request_answer_event_handler(
        self, handler: EVENT_HANDLER
    ) -> None:
        self._playback_time_request_answer_event_handler = handler

    def install_pause_request_event_handler(self, handler: EVENT_HANDLER) -> None:
        self._pause_request_event_handler = handler

    def install_rewind_back_request_event_handler(self, handler: EVENT_HANDLER) -> None:
        self._rewind_back_request_event_handler = handler

    def install_kick_event_handler(self, handler: EVENT_HANDLER) -> None:
        self._kick_event_handler = handler

    def install_leave_room_event_handler(self, handler: EVENT_HANDLER) -> None:
        self._leave_room_event_handler = handler

    def install_error_event_handler(self, handler: EVENT_HANDLER) -> None:
        self._error_event_handler = handler

    async def disconnect(self) -> None:
        self._active = False
        await self.websocket.close()
