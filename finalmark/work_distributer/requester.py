import json
from redis import Redis
from datetime import datetime
from hashlib import sha256
from time import sleep

class RefreshRequester(object):

    def __init__(self, queue):
        self.redis = Redis(host='redis')
        self.queue = queue

    def block_request(self, data):
        username = data.get('username')
        work_id = self._generate_work_id(username)
        data.update({"work_id": work_id})

        for _ in range(5):
            if self._wait_for_receive(work_id, data):
                response = self._wait_for_response(work_id)
                if response:
                    return response
        return {}

    def _wait_for_receive(self, work_id, data):
        self.redis.lpush(self.queue, json.dumps(data))
        key, value = self.redis.brpop(work_id)
        data = json.loads(value.decode())
        if data.get('status') == 'processing':
            return True
        return False

    def _wait_for_response(self, work_id):
        key, value = self.redis.brpop(work_id, timeout=30)

        if value is not None:
            data = json.loads(value.decode())
            return data
        else:
            return {}

    def _generate_work_id(self, username):
        h = sha256()
        h.update(username.encode('utf-8'))
        h.update(str(datetime.now()).encode('utf-8'))
        return h.hexdigest()
