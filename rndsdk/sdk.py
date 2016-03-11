# coding: utf8
import zmq
import time

try:
    import ujson as json
except ImportError:
    import json

c = zmq.Context()


class Operation(object):
    def __init__(self, dist):
        host, port = dist.split(':')
        self.push_c = c.socket(zmq.PUB)
        self.push_c.connect('tcp://{host}:{port}'.format(host=host, port=port))
        time.sleep(1)

    def send(self, topic, body):
        sp = topic.split(':')
        channel = sp[0]
        ret = {
            'topic': topic,
            'data': body
        }
        ret = json.dumps(ret, ensure_ascii=False)
        self.push_c.send_multipart([channel, ret])

    def __del__(self):
        if self.push_c:
            self.push_c.close()

