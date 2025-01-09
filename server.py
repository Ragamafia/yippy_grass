import asyncio

from aiohttp import web, WSMsgType, WSMessage


HOST = '0.0.0.0'
PORT = 9999

app = web.Application()


async def websocket_handler(request: web.Request) -> web.StreamResponse:
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    await ws.send_str(str(request.remote))
    await ws.close()
    print('accepted connection from', request.remote)
    return ws

app.add_routes([
    web.get('/', websocket_handler)
])


async def main():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=HOST, port=PORT)
    await site.start()
    print('server is running')
    await asyncio.Future()


asyncio.run(main())