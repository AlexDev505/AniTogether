import asyncio
import os
import signal

import websockets

from logger import logger
from ws_server import ws_handler


os.environ["COMPATIBLE_VERSION"] = '1.0.0-betta.4'


from http_server import http_handler  # noqa


async def main():
    try:
        loop = asyncio.get_running_loop()
        stop = loop.create_future()
        loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
    except NotImplementedError:
        stop = asyncio.Future()

    port = int(os.environ.get("PORT", "8001"))
    async with websockets.serve(ws_handler, "", port, process_request=http_handler):
        logger.info("Server started")
        await stop  # Запуск бесконечного цикла


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Server stopped")
