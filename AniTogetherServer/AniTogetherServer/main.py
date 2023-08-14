import asyncio
import http
import os
import signal

import websockets

from logger import logger
from server import server


async def health_check(path: str, _request_headers):
    if path == "/healthz":
        return (
            http.HTTPStatus.OK,
            {"Access-Control-Allow-Origin": "*"},
            b"OK\n",
        )


async def main():
    try:
        loop = asyncio.get_running_loop()
        stop = loop.create_future()
        loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    except NotImplementedError:
        stop = asyncio.Future()

    port = int(os.environ.get("PORT", "8001"))
    async with websockets.serve(server, "", port, process_request=health_check):
        logger.info("Server started")
        await stop  # Запуск бесконечного цикла


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Server stopped")
