import asyncio
import logging

from websockets.asyncio.client import connect


class GrassWs:
    def __init__(self, proxy = None):
        self.proxy = proxy
        self.session = None
        self.websocket = None

    async def connection(self):
        uri = f'wss://proxy2.wynd.network:4444/'
        headers = {
            'Pragma': 'no-cache',
            'Origin': 'chrome-extension://ilehaonighjijnmpnagapkhpcdbhclfg',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Sec-WebSocket-Key': 'PvGcWz+F1tCYcqHT9rqnXA==',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Upgrade': 'websocket',
            'Cache-Control': 'no-cache',
        }

        try:
            self.websocket = await connect(uri)
        except Exception as e:
            print(e)


GrassWs().connection()
