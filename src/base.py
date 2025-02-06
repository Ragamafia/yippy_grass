import uuid
import json
from pydantic import BaseModel, Field
from pathlib import Path

from config import cfg


try:
    from fake_useragent import UserAgent
    fake_useragent = UserAgent()

except TypeError:

    class FakeOfFakeUserAgent:
        def __init__(self):
            try:
                self.load()

            except Exception:
                raise RuntimeError(
                    "You using old version of python and cannot generate fake useragents dynamycly."
                    "Please use Python 3.10+ or create file <fake_user_agents.json> with user agented presented"
                )

        filepath: Path = Path("../data/fake_user_agents.json")
        agents: list = Field(default_factory=list)

        def load(self):
            with open(self.filepath) as f:
                self.agents = json.load(f)

        def save(self):
            with open(self.filepath, "w") as f:
                json.dump(self.agents, f)

        def random(self):
            ua = self.agents.pop(0)
            self.save()
            return ua

    fake_useragent = FakeOfFakeUserAgent()


class Device(BaseModel):
    user_id: str
    device_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_agent: str = Field(default_factory=fake_useragent.random)

    def auth_data(self):
        return {
            "device_id": self.device_id,
            "user-agent": self.user_agent
        }


class UserDevices:
    user_id: str
    items: list

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.items = self.load()

    def get_devices(self, count: int):
        if count > len(self.items):
            for _ in range(count - len(self.items)):
                self.items.append(Device(user_id=self.user_id).auth_data())

            self.save()

        return self.items[:count]

    def load(self):
        try:
            with open(self.get_filename()) as f:
                return json.load(f)
        except:
            ...
        return []

    def save(self):
        with open(self.get_filename(), "w") as f:
            json.dump(self.items, f)

    def get_filename(self):
        return f"../data/devices/{self.user_id}.json"


user_devices = UserDevices(cfg.user_id)
