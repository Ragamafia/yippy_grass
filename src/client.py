import asyncio
import json
import random
import uuid

from aiohttp import ClientSession
#from fake_useragent import FakeUserAgent

from loguru import logger
from proxies.pool import get_proxy
from config import cfg


SOCKET_URL = random.choice(cfg.urls)
ATTEMPTS = 50

BROWSER_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, SOCKET_URL))
#USER_AGENT = FakeUserAgent().random

response = {"id": "",
                      "origin_action": "AUTH",
                      "result": {"browser_id": BROWSER_ID,
                                 "user_id": "2rKa9HOuohobeY3DEfxFx2xWj7I",
                                 "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                                 "timestamp": 1736645161,
                                 "device_type": "extension",
                                 "version": "4.26.2",
                                 "extension_id": "ilehaonighjijnmpnagapkhpcdbhclfg"
                                 }
                      }

auth_false = {"action":"LOGS",
              "data":f"onErrorOccured, 2263, , net::ERR_TUNNEL_CONNECTION_FAILED"}

auth_again = {"action":"LOGS",
              "data":"RPC encountered error for message {\"id\":\"10uYKq6BbLdxsCEiZDfrt\",\"action\":\"HTTP_REQUEST\",\"data\":{\"url\":\"https://api.getgrass.io/e65c798e44045cf3241e5bdc52aff12c/EIrlvjc15yLgVtiz\",\"method\":\"GET\",\"headers\":{\"Accept\":\"*/*\",\"Host\":\"api.getgrass.io\",\"User-Agent\":\"wynd.network/3.0.1\"},\"body\":null,\"authenticated\":false}}: TypeError: Failed to fetch, TypeError: Failed to fetch\n    at Object.performHttpRequest [as HTTP_REQUEST] (chrome-extension://ilehaonighjijnmpnagapkhpcdbhclfg/background.js:691:46)\n    at async WebSocket.<anonymous> (chrome-extension://ilehaonighjijnmpnagapkhpcdbhclfg/background.js:820:24)"}


async def connect_to_ws(session: ClientSession, proxy: str):
    logger.info(f"Connecting with proxy: {proxy}")
    connected = False

    async with session.ws_connect(SOCKET_URL, proxy=proxy) as ws:
        async for msg in ws:
            if msg is not None:
                logger.info(f"Websocket connect: {msg}")
                msg_attr = msg.__getattribute__('data')
                msg_attr_dict = json.loads(msg_attr)
                id = msg_attr_dict.get('id')
                response['id'] = id

                connected = True

                await ws.send_json(response)

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
                ...

if __name__ == "__main__":
    asyncio.run(main())
