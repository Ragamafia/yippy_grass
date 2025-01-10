from datetime import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field

Scheme = Literal["http", "https"]
ProxyStatus = Literal["busy", "free", "dead"]


class Proxy(BaseModel):
    scheme: Scheme
    login: str
    password: str
    host: str
    port: int
    ip: str

    status: ProxyStatus = "free"
    last_checked: int = Field(default_factory=lambda: int(dt.utcnow().timestamp()))
    last_used: int

    def __hash__(self):
        return hash(self.ip)

    def __eq__(self, other):
        return self.ip == other.ip