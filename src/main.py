import asyncio

from loguru import logger
from aiohttp import ClientSession

from proxies.pool import get_proxy
from head import device
from client import Connect as connect
from config import cfg


async def run_device(headers):
    async with ClientSession() as session:
        for _ in range(cfg.ATTEMPTS):
            try:
                proxy = await get_proxy()
                logger.info(f'Connecting with proxy: {proxy.url}')
                connection = await connect(session, proxy.url, headers).connect_to_ws()
                if connection:
                    break
            except Exception as e:
                logger.error(f'Proxy failed: {e}')

async def main():
    tasks = []
    for _ in range(cfg.device_count):
        tasks.append(run_device(device.generate_headers()))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
