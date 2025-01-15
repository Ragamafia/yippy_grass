import asyncio
import json
import random
import uuid

from aiohttp import ClientSession, WSMsgType
#from fake_useragent import FakeUserAgent

from loguru import logger
from proxies.pool import get_proxy
from config import cfg


SOCKET_URL = random.choice(cfg.urls)
ATTEMPTS = 50

BROWSER_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, SOCKET_URL))

#USER_AGENT = FakeUserAgent().random
#PING_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, SOCKET_URL))

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
#{"id":"ku-A6U29tG3hbBTzKOMuM","action":"HTTP_REQUEST","data":{"url":"https://api.getgrass.io/e65c798e44045cf3241e5bdc52aff12c/Jr3UU3LfZYfbIBHs","method":"GET","headers":{"Accept":"*/*","Host":"api.getgrass.io","User-Agent":"wynd.network/3.0.1"},"body":null,"authenticated":false}}
#{"id":"ku-A6U29tG3hbBTzKOMuM","origin_action":"HTTP_REQUEST","result":{"url":"https://api.getgrass.io/e65c798e44045cf3241e5bdc52aff12c/Jr3UU3LfZYfbIBHs","status":200,"status_text":"","headers":{"cf-cache-status":"DYNAMIC","cf-ray":"90224205fdc6021e-CDG","content-length":"29","content-type":"application/json; charset=utf-8","date":"Wed, 15 Jan 2025 01:57:56 GMT","etag":"W/\"1d-59r+cbUG0HhXFjR4xmDw4JJ70Oo\"","nel":"{\"success_fraction\":0,\"report_to\":\"cf-nel\",\"max_age\":604800}","report-to":"{\"endpoints\":[{\"url\":\"https:\\/\\/a.nel.cloudflare.com\\/report\\/v4?s=9riLXFAH3j7zpoQiJG2BOgWFzSifwtoiR2Xeoi9LVlhEcXd1CYpleXFuIS6iHakRRKJSvqoQfZ%2BsZSCJsynEJzCS9cNsA%2FukLhO%2FtU9cCikb5D%2FxLjBsoCHdSc0KOFnCsQ%3D%3D\"}],\"group\":\"cf-nel\",\"max_age\":604800}","server":"cloudflare","server-timing":"cfL4;desc=\"?proto=TCP&rtt=4858&min_rtt=4838&rtt_var=1036&sent=5&recv=10&lost=0&retrans=0&sent_bytes=2840&recv_bytes=964&delivery_rate=601070&cwnd=253&unsent_bytes=0&cid=69fa6ba98460f2ba&ts=372&x=0\"","vary":"Origin","x-powered-by":"Express"},"body":"eyJjb2RlIjoiJ2VaV0RnYUFaWkJFQXpRRmInIn0="}}

http_request = {"id":"",
                "origin_action":"HTTP_REQUEST",
                "result":{"url":"",
                          "status":200,
                          "status_text":"",
                          "headers":{"cf-cache-status":"DYNAMIC",
                                     "cf-ray":"90224205fdc6021e-CDG",
                                     "content-length":"29",
                                     "content-type":"application/json; charset=utf-8",
                                     "date":"Wed, 15 Jan 2025 01:57:56 GMT",
                                     "etag":"W/\"1d-59r+cbUG0HhXFjR4xmDw4JJ70Oo\"","nel":"{\"success_fraction\":0,\"report_to\":\"cf-nel\",\"max_age\":604800}",
                                     "report-to":"{\"endpoints\":[{\"url\":\"https:\\/\\/a.nel.cloudflare.com\\/report\\/v4?s=9riLXFAH3j7zpoQiJG2BOgWFzSifwtoiR2Xeoi9LVlhEcXd1CYpleXFuIS6iHakRRKJSvqoQfZ%2BsZSCJsynEJzCS9cNsA%2FukLhO%2FtU9cCikb5D%2FxLjBsoCHdSc0KOFnCsQ%3D%3D\"}],\"group\":\"cf-nel\",\"max_age\":604800}",
                                     "server":"cloudflare","server-timing":"cfL4;desc=\"?proto=TCP&rtt=4858&min_rtt=4838&rtt_var=1036&sent=5&recv=10&lost=0&retrans=0&sent_bytes=2840&recv_bytes=964&delivery_rate=601070&cwnd=253&unsent_bytes=0&cid=69fa6ba98460f2ba&ts=372&x=0\"","vary":"Origin","x-powered-by":"Express"},"body":"eyJjb2RlIjoiJ2VaV0RnYUFaWkJFQXpRRmInIn0="
                          }
                }

ping = {"id":"","version":"1.0.0","action":"PING","data":{}}

pong = {"id":"","origin_action":"PONG"}


class Connect:

    def __init__(self, session: ClientSession, proxy: str):

        self.session = session
        self.proxy = proxy


    async def connect_to_ws(self):
        connected = False
        print('test')

        async with self.session.ws_connect(SOCKET_URL, proxy=self.proxy) as self.ws:
            logger.info(f"Connecting with proxy: {self.proxy}")
            async for msg in self.ws:
                if msg is not None:
                    logger.info(f"<- Messages received: {msg}")
                    message_data = msg.__getattribute__('data')
                    self.data = json.loads(message_data)

                    if self.data.get('action') == "HTTP_REQUEST":
                        await self.send_http_request()

                    await self.send_headers()

                connected = True

        return connected


    async def send_headers(self):
        id = self.data.get('id')
        headers['id'] = id
        logger.info(f"-> Send message: {headers}")
        await self.ws.send_json(headers)


    async def send_http_request(self):
        id = self.data.get('id')
        url = self.data.get('url')
        http_request['id'] = id
        http_request['url'] = url
        logger.info(f"-> Send message: {http_request}")
        await self.ws.send_json(http_request)


    async def send_ping(self):
        ping['id'] = str(uuid.uuid3(uuid.NAMESPACE_DNS, SOCKET_URL))
        logger.info(f"-> Send message: {ping}")
        await self.ws.send_json(ping)


async def main():
    async with ClientSession() as session:
        for _ in range(ATTEMPTS):
            proxy = await get_proxy()
            try:
                print(f'выполнение {_}')
                connect = await Connect.connect_to_ws(session, proxy.url)
                if connect:
                    break
            except Exception as e:
                ...

#
# if __name__ == "__main__":
#     asyncio.run(main())
