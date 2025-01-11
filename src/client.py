import asyncio

from aiohttp import ClientSession

from proxies.pool import get_proxy
from src import logger

SOCKET_URL = 'wss://proxy2.wynd.network:4444'
ATTEMPTS = 50


async def connect_to_ws(session: ClientSession, proxy: str):
    connected = False

    logger.logger.info(f"Connecting with proxy: {proxy}")
    async with session.ws_connect(SOCKET_URL, proxy=proxy) as ws:
        async for msg in ws:
            print(f'Connected: {msg}')
            if msg is not None:
                connected = True

    return connected


async def main():
    async with ClientSession() as session:
        for _ in range(ATTEMPTS):
            proxy = await get_proxy()
            try:
                connected = await connect_to_ws(session, proxy.url)
                if connected:
                    break
            except Exception as e:
                print(f'Exception: {e}')


if __name__ == "__main__":
    asyncio.run(main())
