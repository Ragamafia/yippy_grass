import asyncio
from datetime import datetime as dt
import random as rnd

from aiohttp import ClientSession, ClientTimeout
from aiohttp_proxy import ProxyConnector, ProxyType
from bs4 import BeautifulSoup as bs

import config as cfg
from models import Proxy

TIMEOUT = ClientTimeout(total=cfg.proxy_check_timeout)
SCAN_TIMEOUT = ClientTimeout(total=60)


async def get_scam_rate(ip: str):
    async with ClientSession() as session:
        for i in range(cfg.proxy_scam_check_attempts):
            try:
                url = f"https://scamalytics.com/ip/{ip}"
                async with session.get(url) as resp:
                    # print(await resp.text())
                    soup = bs(await resp.text(), "html.parser")
                    if score := soup.find("div", {"class": "score"}):
                        return int(score.text.split(": ")[-1].strip())
            except Exception as e:
                ...
                # print(f"Can not get scam rate: {e}")


class BaseChecker:
    url: str

    def __init__(self, scheme, login, password, host, port):
        self.host = host
        self.port = port
        self.scheme = scheme
        self.login = login
        self.password = password

    async def check(self):
        proxy_type = ProxyType.HTTP if self.scheme == "http" else ProxyType.HTTPS
        kwargs = {
            "timeout": TIMEOUT,
            "connector": ProxyConnector(
                proxy_type=proxy_type,
                host=self.host,
                port=self.port,
                username=self.login,
                password=self.password,
            ),
        }
        valid = False
        ip = None

        async with ClientSession(**kwargs) as session:
            for _ in range(cfg.proxy_check_attempts):
                try:
                    async with session.get(self.url) as resp:
                        ip = await self._check(resp)
                        valid = bool(ip)
                        break
                except Exception as e:
                    print(f"Can not check proxy: {e}")

            scam_rate = ip and await get_scam_rate(ip)
            if not scam_rate or scam_rate > 11:
                valid = False

        return Proxy(
            scheme=self.scheme,
            login=self.login,
            password=self.password,
            host=self.host,
            port=self.port,
            ip=ip,
            status="free" if valid else "dead",
            # last_checked=int(dt.utcnow().timestamp()),
        )

    async def _check(self, response) -> str:
        return ((await response.json()) or {}).get("ip")


class IPWhoIsChecker(BaseChecker):
    url: str = "http://ipwhois.app/json/"


class IPifyChecker(BaseChecker):
    url: str = "https://api.ipify.org"

    async def _check(self, response) -> str:
        result = (await response.text()).strip()
        if (7 > len(result) < 16) and "." in result[1:4]:
            return result.get("ip")


checkers = [
    IPWhoIsChecker,
    IPifyChecker,
]


async def check_proxy(scheme, login, password, host, port):
    checker = rnd.choice(checkers)
    return await checker(scheme, login, password, host, port).check()


class ProxyPool:
    proxies: list

    def __init__(self):
        self.proxies = []

    async def get(self):
        if not self.proxies:
            self.proxies = await self.fetch_all_proxies()

        while self.proxies and (proxy_raw := self.proxies.pop(0)):
            if proxy := await check_proxy(**proxy_raw):
                return proxy

    async def fetch_all_proxies(self):
        proxies = [{
            "scheme": cfg.scheme,
            "login": cfg.login,
            "password": cfg.password,
            "host": cfg.host,
            "port": port
        } for port in range(10101, 11000)]

        return proxies


proxy_pool = ProxyPool()
get_proxy = proxy_pool.get

if __name__ == '__main__':
    for i in range(400):
        print(asyncio.run(get_proxy()))
        print(asyncio.run(get_proxy()))
        print(asyncio.run(get_proxy()))