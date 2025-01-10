from typing import Literal
from typing import Union

from pydantic import BaseModel

Scheme = Literal["http", "https"]
ProxyStatus = Literal["busy", "free", "dead"]


class Proxy(BaseModel):
    scheme: Scheme
    login: str
    password: str
    host: str
    port: int
    ip: Union[str, None] = None

    status: ProxyStatus = "free"

    def __hash__(self):
        return hash(self.ip)

    def __eq__(self, other):
        return self.ip == other.ip