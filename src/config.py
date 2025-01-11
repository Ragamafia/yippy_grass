from pydantic_settings import BaseSettings


class Config(BaseSettings):
    proxy_check_timeout: int = 6
    proxy_check_attempts: int = 1
    proxy_scam_check_attempts: int = 10

    scheme: str = "http"
    login: str = "kEUXJtHGBGFP"
    password: str = "RNW78Fm5"
    host: str = "pool.proxy.market"


cfg = Config()
