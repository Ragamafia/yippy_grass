import asyncio
import json
import random

from loguru import logger
from aiohttp import ClientSession

from proxies.pool import get_proxy
from base import user_devices
from config import cfg


SOCKET_URL = random.choice(cfg.urls)

async def parse_message(session: ClientSession, message: dict, device: dict, proxy:str, headers: dict):
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
        url = message.get("data").get("url")
        async with session.get(url, proxy=proxy, headers=headers) as response:
            body = await response.text()
            print(body)
            return {
                "id": "",
                "action": "HTTP_REQUEST",
                "data": {
                    "url": url,
                    "method": "GET",
                    "headers": response.headers,
                },
                "body": body,
                "authenticated": False
            }


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
    async with ClientSession(**kwargs) as session:
        logger.info(f'Connecting WS with proxy: {proxy.url}')
        async with session.ws_connect(SOCKET_URL) as ws:
            async for message in ws:
                message = json.loads(message.data)
                logger.success(f"<- Received: {message}")
                if response := await parse_message(session, message, device, proxy.url, headers):
                    response["id"] = message["id"]
                    await ws.send_json(response)


async def main():
    devices = user_devices.get_devices(cfg.device_count)
    await asyncio.gather(*[run_device(d) for d in devices])


if __name__ == "__main__":
    asyncio.run(main())