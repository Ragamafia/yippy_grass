import asyncio

from websockets_proxy import Proxy, proxy_connect


CHECKER_URL = 'wss://proxy2.wynd.network:4444'


async def main():
    proxy = Proxy.from_url("http://kEUXJtHGBGFP:RNW78Fm5@pool.proxy.market:10997")

    async with proxy_connect(CHECKER_URL, proxy=proxy) as ws:
        async for message in ws:
            ip_with_proxy = message
            print(f"Action: {ip_with_proxy}")


if __name__ == "__main__":
    asyncio.run(main())