from flask import Flask, request, jsonify
import json
import threading
from datetime import datetime, timedelta

app = Flask(__name__)

# 读取配置
try:
    with open('private.config.json') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    with open('config.json') as config_file:
        config = json.load(config_file)

client_cache_time = config['clientCacheTime']
record_cache_time = config['recordCacheTime']

# 数据结构和锁
client_records = {}
lock = threading.Lock()

@app.route('/route/sync', methods=['POST'])
def sync():
    data = request.json
    client_domain = data['clientDomain']
    force = data.get('force', 0)
    client_ipv6 = request.remote_addr

    with lock:
        # 更新映射和时间
        client_records[client_domain] = {'ipv6': client_ipv6, 'timestamp': datetime.now()}

        # 清除过期记录
        current_time = datetime.now()
        for domain in list(client_records.keys()):
            if current_time - client_records[domain]['timestamp'] > timedelta(minutes=record_cache_time):
                del client_records[domain]

        return jsonify({domain: record['ipv6'] for domain, record in client_records.items()})

if __name__ == '__main__':
    app.run(host='::', port=config["port"])
