import asyncio


async def get_connect(host, port):
    class Connect:
        async def put_data(self):
            print('отправка данных...')
            await asyncio.sleep(2)
            print('данные отправлены.')

        async def get_data(self):
            print('получение данных...')
            await asyncio.sleep(2)
            print('данные получены')

        async def close(self):
            print('закрытие соединения')
            await asyncio.sleep(2)
            print('соединение закрыто')

    print('устанавливаем соединение...')
    await asyncio.sleep(2)
    print('соединение установлено')

    return Connect()


class Connection:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def __aenter__(self):
        self.connect = await get_connect(self.host, self.port)
        return self.connect

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.connect.close()


async def main():
    async with Connection('localhost', 9001) as conn:
        send_task = asyncio.create_task(conn.put_data())
        recive_task = asyncio.create_task(conn.get_data())

        await send_task
        await recive_task