import asyncio

from aiohttp import ClientSession

from proxies import get_proxy
from logger import logger

SOCKET_URL = 'wss://proxy2.wynd.network:4444'
ATTEMPTS = 3


async def connect_to_ws(session: ClientSession, proxy: str):
    logger.info(f"Connecting with proxy: {proxy}")
    async with session.ws_connect(SOCKET_URL, proxy=proxy) as ws:
        async for msg in ws:
            print(msg)


async def main():
    proxy = await get_proxy()

    async with ClientSession() as session:
        for _ in range(ATTEMPTS):
            try:
                await connect_to_ws(session, proxy.url)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    asyncio.run(main())
