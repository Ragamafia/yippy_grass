import asyncio
import json
import random
import uuid
import time

from loguru import logger
from aiohttp import ClientSession, WSMsgType
#from fake_useragent import FakeUserAgent

from proxies.pool import get_proxy
from config import cfg


SOCKET_URL = random.choice(cfg.urls)
ATTEMPTS = 50

BROWSER_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, SOCKET_URL))

#USER_AGENT = FakeUserAgent().random

headers = {"id": "",
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

http_request = {"id": "",
                "origin_action": "HTTP_REQUEST",
                "result": {"url": "",
                           "status": 200,
                           "status_text": "",
                           "headers": {"cf-cache-status": "DYNAMIC",
                                       "cf-ray": "90224205fdc6021e-CDG",
                                       "content-length": "29",
                                       "content-type": "application/json; charset=utf-8",
                                       "date": "Wed, 15 Jan 2025 01:57:56 GMT",
                                       "etag": "W/\"1d-59r+cbUG0HhXFjR4xmDw4JJ70Oo\"", "nel":"{\"success_fraction\":0,\"report_to\":\"cf-nel\",\"max_age\":604800}",
                                       "report-to":"{\"endpoints\":[{\"url\":\"https:\\/\\/a.nel.cloudflare.com\\/report\\/v4?s=9riLXFAH3j7zpoQiJG2BOgWFzSifwtoiR2Xeoi9LVlhEcXd1CYpleXFuIS6iHakRRKJSvqoQfZ%2BsZSCJsynEJzCS9cNsA%2FukLhO%2FtU9cCikb5D%2FxLjBsoCHdSc0KOFnCsQ%3D%3D\"}],\"group\":\"cf-nel\",\"max_age\": 604800}",
                                       "server":"cloudflare", "server-timing":"cfL4;desc=\"?proto=TCP&rtt=4858&min_rtt=4838&rtt_var=1036&sent=5&recv=10&lost=0&retrans=0&sent_bytes=2840&recv_bytes=964&delivery_rate=601070&cwnd=253&unsent_bytes=0&cid=69fa6ba98460f2ba&ts=372&x=0\"", "vary": "Origin", "x-powered-by": "Express"}, "body": "eyJjb2RlIjoiJ2VaV0RnYUFaWkJFQXpRRmInIn0="
                           }
                }

ping = {"id": "", "version": "1.0.0", "action": "PING", "data": {}}

pong = {"id": "", "origin_action": "PONG"}


class Connect:
    session: ClientSession
    proxy: str
    connected: bool

    def __init__(self, session, proxy):
        self.session = session
        self.proxy = proxy

    async def connect_to_ws(self):
        connected = False

        async with self.session.ws_connect(SOCKET_URL, proxy=self.proxy) as self.ws:
            async for message in self.ws:
                message_data = message.__getattribute__('data')
                self.data = json.loads(message_data)
                logger.info(f"<- Messages received: {self.data}")

                if self.data.get('action') == "AUTH":
                    await self.send_headers()

                if self.data.get('action') == "HTTP_REQUEST":
                    if await self.send_http_request():
                        await self.send_ping()

                if self.data.get('action') == "PONG":
                    await self.send_pong()

                connected = True
        return connected

    async def send_headers(self):
        headers['id'] = self.data.get('id')
        await self.ws.send_json(headers)
        logger.info(f" -> Send message: {headers}")

    async def send_http_request(self):
        http_request['id'] = self.data.get('id')
        http_request['result']['url'] = self.data.get('data').get('url')
        await self.ws.send_json(http_request)
        logger.info(f"-> Send message: {http_request}")
        return True

    async def send_ping(self):
        ping['id'] = str(uuid.uuid3(uuid.NAMESPACE_DNS, SOCKET_URL))
        await self.ws.send_json(ping)
        logger.info(f"-> Send message: {ping}")

    async def send_pong(self):
        pong['id'] = self.data.get('id')
        ping['id'] = str(uuid.uuid4())
        await self.ws.send_json(pong)
        logger.info(f'-> Send message: {pong}')

        time.sleep(cfg.request_time_sleep)
        await self.ws.send_json(ping)
        logger.info(f"-> Send message: {ping}")


async def main():
    async with ClientSession() as session:
        for _ in range(ATTEMPTS):
            proxy = await get_proxy()
            logger.info(f"Connecting with proxy: {proxy.url}")
            try:
                connect = await Connect(session, proxy.url).connect_to_ws()
                if connect:
                    break
            except Exception as e:
                logger.error(f"Proxy fail: {e}")


if __name__ == "__main__":
    asyncio.run(main())
