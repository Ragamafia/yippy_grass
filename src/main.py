import asyncio

from loguru import logger
from aiohttp import ClientSession

from proxies.pool import get_proxy
from client import Connect
from base import user_devices
from config import cfg


devices = user_devices.get_devices(cfg.device_count)


async def run_device(user_agent):
    async with ClientSession() as session:
        for _ in range(cfg.ATTEMPTS):
            try:
                proxy = await get_proxy()
                logger.info(f'Connecting with proxy: {proxy.url}')
                connection = await Connect(session, proxy.url, user_agent).connect_to_ws()
                if connection:
                    break
            except Exception as e:
                logger.error(f'Proxy failed: {proxy} - {e}')


async def main():
    tasks = []
    for i in devices:
        tasks.append(run_device(i))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
