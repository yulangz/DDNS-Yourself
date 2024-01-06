import requests
import time
import json
import os
import platform

# 读取配置
with open('config.json') as config_file:
    config = json.load(config_file)

def sync_hosts(force=False):
    payload = {'clientDomain': config['domain']}
    if force:
        payload['force'] = 1

    response = requests.post(f"http://{config['serverAddr']}:{config['serverPort']}/route/sync", json=payload)
    if response.json():
        with open('hosts', 'r+') as hosts_file:
            lines = hosts_file.readlines()
            new_content = ""
            for line in lines:
                if not line.endswith(config["domainSuffix"]):
                    new_content += line
            for domain, ipv6 in response.json().items():
                new_content += f"{ipv6} {domain}{config['domainSuffix']}\n"

            hosts_file.seek(0)
            hosts_file.write(new_content)
            hosts_file.truncate()

def setup_gateway():
    pass
    # if config['gateway']:
    #     for interface in config['networkInterface']:
    #         if platform.system() == "Windows":
    #             os.system(f"netsh interface ipv6 add route ::/0 interface={interface} store=persistent {config['gateway']}")

if __name__ == "__main__":
    setup_gateway()
    sync_hosts(force=True)  # 首次启动时强制同步
    while True:
        sync_hosts()
        time.sleep(config['syncTime'])
