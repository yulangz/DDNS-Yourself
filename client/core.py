import requests
import json
import os

defaultConfigDir = os.path.dirname(os.path.abspath(__file__))


class DDNSClient:
    def __init__(self) -> None:
        self.config = {}
        self.readConfig()
    
    def readConfig(self):
        try:
            with open(os.path.join(defaultConfigDir, 'private.config.json')) as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            with open(os.path.join(defaultConfigDir, 'config.json')) as config_file:
                self.config = json.load(config_file)

    def sync_hosts(self, force=False):
        payload = {'clientDomain': self.config['domain']}
        if force:
            payload['force'] = 1

        response = requests.post(f"{'https' if self.config['https'] else 'http'}://{self.config['serverAddr']}:{self.config['serverPort']}/route/sync", json=payload)
        if response.json():
            with open(self.config["hostPath"], 'r+') as hosts_file:
                lines = hosts_file.readlines()
                new_content = ""
                for line in lines:
                    if not line.strip().endswith(self.config["domainSuffix"]):
                        new_content += line
                for domain, ipv6 in response.json().items():
                    new_content += f"{ipv6} {domain}\n"

                hosts_file.seek(0)
                hosts_file.write(new_content)
                hosts_file.truncate()
