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
            user_agent = self.data.pop(0)
            logger.info(f'Load new device: {user_agent}')

        self.update_user_agent_list(self.data)

        for k, v in user_agent.items():
            headers['result']['browser_id'] = k
            headers['result']['user_agent'] = v

            return headers

    def update_user_agent_list(self, data):
        with open(self.user_agents, 'w') as file:
            json.dump(data, file, indent=4)


device = Device(cfg.user_agents, cfg.use_devices, cfg.free_devices)


