import os

from dotenv import load_dotenv, find_dotenv
from pydantic_settings import BaseSettings
load_dotenv(find_dotenv())


class Config(BaseSettings):

    urls: list = [
        'wss://proxy2.wynd.network:4444',
        'wss://proxy2.wynd.network:4650',
    ]

    user_agents: str = 'C:\\Users\sales3-suzuki\Desktop\PycharmProjects\yippy_grass\\user_agent.json'
    use_devices: str = 'C:\\Users\sales3-suzuki\Desktop\PycharmProjects\yippy_grass\\use_devices.json'

    device_count: int = 3

    ATTEMPTS: int = 50
    proxy_check_timeout: int = 6
    proxy_check_attempts: int = 1
    proxy_scam_check_attempts: int = 10

    request_time_sleep: int = 60

    user_id: str = os.getenv('user_id')

    scheme: str = 'http'
    login: str = os.getenv('login')
    password: str = os.getenv('password')
    host: str = 'pool.proxy.market'


cfg = Config()
