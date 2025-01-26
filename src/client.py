import json
import random
import uuid
import time

from loguru import logger
from aiohttp import ClientSession

from config import cfg


SOCKET_URL = random.choice(cfg.urls)

auth = {
    "id": "",
    "origin_action": "AUTH",
    "result": {
        "browser_id": "",
        "user_id": "",
        #"user_agent": "",
        "timestamp": 1736645161,
        "device_type": "extension",
        "version": "4.26.2",
        "extension_id": "ilehaonighjijnmpnagapkhpcdbhclfg"
    }
        }

http_request = {
    "id": "",
    "action": "HTTP_REQUEST",
    "data": {
        "url": "",
        "method": "GET",
        "headers": {},
    },
    "body": None,
    "authenticated": False
}

ping = {"id": "", "version": "1.0.0", "action": "PING", "data": {}}

pong = {"id": "", "origin_action": "PONG"}


class Connect:
    session: ClientSession
    proxy: str
    user_agent: dict
    auth: dict
    http_request: dict
    ping: dict
    pong: dict

    def __init__(self, session, user_agent, proxy):
        self.session = session
        self.user_agent = user_agent
        self.proxy = proxy

    async def connect_to_ws(self):
        connected = False

        kwargs = {

            "headers": {
                "User-Agent": self.user_agent.get("user_agent"),
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
            }
        }

        try:
            async with self.session.ws_connect(SOCKET_URL, proxy=self.proxy, **kwargs) as self.ws:
                async for message in self.ws:

                    message_data = message.__getattribute__('data')
                    self.data = json.loads(message_data)
                    logger.info(f"<- Received: {self.data}")

                    if self.data.get('action') == "AUTH":
                        await self.send_auth()

                    elif self.data.get('action') == "HTTP_REQUEST":
                        url = self.data.get("data").get("url")
                        async with self.session.get(url, **kwargs) as response:
                            body = await response.text()
                            print(body)

                        # if await self.send_http_request():
                        #     await self.send_ping()

                    elif self.data.get('action') == "PONG":
                        await self.send_pong()

                    connected = True
            return connected

        except Exception as e:
            logger.error(f"<- Connect error: {e} - {self.data}")

    async def send_auth(self):
        auth["id"] = self.data.get("id")
        auth["result"]["browser_id"] = self.user_agent.get("device_id")
        auth["result"]["user_id"] = self.user_agent.get("user_id")
        auth["result"]["user_agent"] = self.user_agent.get("user_agent")

        await self.ws.send_json(auth)
        logger.info(f" -> Sending: {auth}")

    async def send_http_request(self):
        http_request["id"] = self.data.get("id")
        http_request["data"]["url"] = self.data.get("data").get("url")
        http_request["data"]["headers"] = self.user_agent

        await self.ws.send_json(http_request)
        logger.info(f"-> Sending: {http_request}")
        return True

    async def send_ping(self):
        ping["id"] = str(uuid.uuid3(uuid.NAMESPACE_DNS, SOCKET_URL))
        await self.ws.send_json(ping)
        logger.info(f"-> Sending: {ping}")

    async def send_pong(self):
        pong["id"] = self.data.get("id")
        ping["id"] = str(uuid.uuid4())
        await self.ws.send_json(pong)
        logger.info(f'-> Sending: {pong}')

        time.sleep(cfg.request_time_sleep)
        await self.ws.send_json(ping)
        logger.info(f"-> Sending: {ping}")
