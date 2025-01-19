import json

from config import cfg


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
    def __init__(self, user_agent_list, update_list):
        self.user_agent_list = user_agent_list
        self.update_list = update_list

        self.get_device()
        self.generate_device()

    def generate_device(self):
        for item in self.devices:
            for k, v in item.items():
                headers['result']['browser_id'] = k
                headers['result']['user_agent'] = v

                return headers


    def get_device(self):
        with open(self.user_agent_list, 'r') as file:
            data = json.load(file)
            self.devices = data[:cfg.device_count]
            self.remaining_devices = data[cfg.device_count:]

    def update_device(self):
        with open(self.update_list, 'w') as file:
            json.dump(self.remaining_devices, file, indent=4)


dev = Device(cfg.user_agents, cfg.update_list)
