import json

from config import cfg
from logger import logger


headers = {"id": "",
           "origin_action": "AUTH",
           "result": {"browser_id": "",
                      "user_id": cfg.user_id,
                      "user_agent": "",
                      "timestamp": 1736645161,
                      "device_type": "extension",
                      "version": "4.26.2",
                      "extension_id": "ilehaonighjijnmpnagapkhpcdbhclfg"
                      }
           }


class Device:
    def __init__(self, user_agents, use_devices, free_devices):
        self.user_agents = user_agents
        self.use_devices = use_devices
        self.free_devices = free_devices

        self.generate_headers()

    def generate_headers(self):
        with open(self.user_agents, 'r') as file:
            self.data = json.load(file)
            self.user_agent = self.data.pop(0)

            logger.info(f'Load new device: {self.user_agent}')

        self.save_use_device(self.user_agent)
        self.update_user_agent_list(self.data)

        for k, v in self.user_agent.items():
            headers['result']['browser_id'] = k
            headers['result']['user_agent'] = v

            return headers

    def save_use_device(self, data):
        with open(self.use_devices, 'r') as file_before:
            before = json.load(file_before)
            before.append(data)
        with open(self.use_devices, 'w') as file_after:
            json.dump(before, file_after, indent=4)

    def update_user_agent_list(self, data):
        with open(self.user_agents, 'w') as file:
            json.dump(data, file, indent=4)


device = Device(cfg.user_agents, cfg.use_devices, cfg.free_devices)


