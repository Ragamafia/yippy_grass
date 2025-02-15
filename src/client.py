import asyncio
import json
import random
import aiohttp
import uuid

from loguru import logger
from aiohttp import ClientSession
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector, ProxyType

from proxies.pool import get_proxy
from base import user_devices
from config import cfg


SOCKET_URL = random.choice(cfg.urls)


async def parse_message(session: ClientSession, ws, message: dict, device: dict, proxy:str, headers: dict):

    if message.get('action') == "AUTH":
        return {
            "id": "",
            "origin_action": "AUTH",
            "result": {
                "browser_id": device["device_id"],
                "user_id": device["user_id"],
                "user_agent": device["user_agent"],
                "timestamp": 1736645161,
                "device_type": "extension",
                "version": "4.26.2",
                "extension_id": "ilehaonighjijnmpnagapkhpcdbhclfg"
            }
        }

    if message.get('action') == "PONG":
        return {"id": "", "origin_action": "PONG"}

    if message.get('action') == "HTTP_REQUEST":
        await send_ping(ws)

        url = message.get("data").get("url")
        async with session.get(url, proxy=proxy, headers=headers) as response:
            body = await response.text()
            return {
                "id": "",
                "action": "HTTP_REQUEST",
                "data": {
                    "url": url,
                    "method": "GET",
                    "headers": dict(response.headers),
                },
                "body": body,
                "authenticated": False
            }


def get_proxy_connector():
    https_proxy = True
    connector = ProxyConnector(
        proxy_type=ProxyType.HTTP if https_proxy else ProxyType.HTTPS,
        host=cfg.host,
        port=10300,
        username=cfg.login,
        password=cfg.password,
    )
    connector.proxy_auth = aiohttp.BasicAuth(
        cfg.login,
        cfg.password,
    )
    return connector


async def send_ping(ws):
    ping = {"id": str(uuid.uuid4()), "version": "1.0.0", "action": "PING", "data": {}}
    await ws.send_json(ping)
    logger.info(f"<- Send: {ping}")
    await asyncio.sleep(20)


async def run_device(device):
    headers = {
        "User-Agent": device.get("user_agent"),
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    kwargs = {
        "trust_env":  True,
        "headers": headers
    }
    proxy = await get_proxy()
    connector = get_proxy_connector()

    #async with CloudflareScraper(connector=connector, **kwargs) as session:
    async with ClientSession(**kwargs) as session:
        logger.info(f'Connecting WS with proxy: {proxy.url}')
        async with session.ws_connect(SOCKET_URL) as ws:
            while True:
                async for message in ws:
                    message = json.loads(message.data)
                    logger.success(f"<- Received: {message}")
                    if response := await parse_message(session, ws, message, device, proxy.url, headers):
                        response["id"] = message["id"]
                        await ws.send_json(response)
                        logger.info(f"<- Send: {response}")

                    await send_ping(ws)


async def main():
    devices = user_devices.get_devices(cfg.device_count)
    await asyncio.gather(*[run_device(d) for d in devices])


if __name__ == "__main__":
    asyncio.run(main())
