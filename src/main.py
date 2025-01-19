import asyncio

from loguru import logger
from aiohttp import ClientSession

from client import Connect as connect
from head import device
from proxies.pool import get_proxy
from config import cfg


async def main():
    async with ClientSession() as session:
        for _ in range(cfg.ATTEMPTS):
            proxy = await get_proxy()
            logger.info(f"Connecting with proxy: {proxy.url}")

            headers = device.generate_headers()
            try:
                connection = await connect(session, proxy.url, headers).connect_to_ws()
                if connection:
                    break

            except Exception as e:
                logger.error(f"Proxy fail: {e}")

if __name__ == "__main__":
    asyncio.run(main())
