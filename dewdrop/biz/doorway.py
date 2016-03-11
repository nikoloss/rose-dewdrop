# coding: utf-8
from zmq.eventloop.zmqstream import ZMQStream

import tornado.websocket
import tornado.web
from tornado.log import app_log
from core import *
import time
import json


HEARTBEAT_CC = 40

MEMBERS = 0


class Messager(object):

    def __init__(self, callback):
        self.callback = callback
        self.stamps = {}
        self.topics = []
        self._sock = ctx.socket(zmq.SUB)
        self._sock.connect('inproc://monster')
        self._stream = ZMQStream(self._sock)
        self._stream.on_recv(self.recv)

    def destroy(self):
        self.callback = None
        self.topics = None
        self._stream.close()

    def subscribe(self, raw_topic, stamp):
        topic = raw_topic.split(':')
        if not topic:
            return
        if [x for x in self.topics if x == topic]:
            return
        self.stamps.update({raw_topic: stamp})
        self._sock.setsockopt(zmq.SUBSCRIBE, str(topic[0]))
        self.topics.append(topic)

    def unsubscribe(self, raw_topic):
        topic = raw_topic.split(':')
        if not topic:
            return
        try:
            self.topics.remove(raw_topic.split(':'))
            self.stamps.pop(raw_topic)
            for tt in self.topics:
                if tt[0] == topic[0]:
                    break
            else:
                self._sock.setsockopt(zmq.UNSUBSCRIBE, str(topic[0]))
        except:
            pass

    def recv(self, frame):
        _, data = frame
        try:
            dd = json.loads(data)
            top = dd.get('topic')
            if not top:
                return
            top = top.split(':')
            for topic in self.topics:
                if topic == top[:len(topic)]:
                    raw_topic = ':'.join(topic)
                    stamp = self.stamps.get(raw_topic)
                    dd['stamp'] = stamp
                    self.callback(ujson.dumps(dd))
        except:
            pass



@Application.register(path='/api/push/ws')
class PushWs(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        self.prepare()

    def prepare(self):
        if not hasattr(self, '_is_open'):
            self.messager = Messager(self.push)
            self.timestamp = time.time()
            self.messager.subscribe('SYS:PING', 'SYS:PING')
            Statistics.CONNECTIONS += 1
            app_log.info('online connections %d', Statistics.CONNECTIONS)
            self._is_open = True

    def push(self, msg):
        if (time.time() - self.timestamp) > 2 * HEARTBEAT_CC:
            self.close()
        else:
            self.write_message(msg)

    def on_message(self, message):
        app_log.debug(message)
        self.timestamp = time.time()
        try:
            content = json.loads(message)
            op = content['action']
            if op == 'sub':
                self.messager.subscribe(content['data'], content['stamp'])
            elif op == 'subs':
                for topic in content['data']:
                    self.messager.subscribe(topic, content['stamp'])
            elif op == 'unsub':
                self.messager.unsubscribe(content['data'])
            elif op == 'unsubs':
                for topic in content['data']:
                    self.messager.unsubscribe(topic)
            elif op == 'clear':
                self.messager = None
                self.messager = Messager(self.send)
            elif op == 'pong':
                pass
        except Exception as e:
            app_log.exception(e)

    def on_close(self):
        if hasattr(self, '_is_open'):
            self.messager.destroy()
        Statistics.CONNECTIONS -= 1
        app_log.info('online connections %d', Statistics.CONNECTIONS)


@Application.register(path='/test')
class Page(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')
