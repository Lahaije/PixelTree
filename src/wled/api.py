from typing import Dict, Union
import requests
import time


class Wled:
    def __init__(self, ip='192.168.2.6'):
        self.ip = ip

    def get_state(self):
        return self.send({}, 'state')

    def get_all(self):
        r = requests.get(f"http://{self.ip}/json")
        return r.json()

    def send(self, data: Dict[str, Union[str, bool]], url=''):
        uri = f"http://{self.ip}/json/{url}"
        start = time.time()
        r = requests.post(uri, json=data)
        print(f"{(time.time()-start)*1000:0.0f} ms -> {uri}")
        return r.json()


if __name__ == "__main__":
    wled = Wled()
    print(wled.get_all())
