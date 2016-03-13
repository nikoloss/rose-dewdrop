# coding: utf-8
from zmq.eventloop.zmqstream import ZMQStream

import tornado.websocket
import tornado.web
from tornado.log import app_log
from core import *
import time
import json


HEARTBEAT_CC = 60

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
        '''订阅
            订阅的主题支持多级主题,用冒号分隔,例如
            WEATHER:CHINA:HANGZHOU
            订阅父主题将会收到所有该类主题消息,比如订阅了WEATHER:CHINA,将收到所有中国城市的天气

            但由于zmq的订阅规则中并不支持多级主题,于是需要自己在内容中维护多级主题关系,将顶级主题送到zmq中
        '''
        topic = raw_topic.split(':')
        if not topic:
            return
        if [x for x in self.topics if x == topic]:
            return
        self.stamps.update({raw_topic: stamp})
        self._sock.setsockopt(zmq.SUBSCRIBE, str(topic[0]))
        #TODO 目前的多级主题(topics)的内存结构为列表,消息送达之后需整体遍历列表以判断用户是否订阅该主题,可以考虑使用trie树来优化
        self.topics.append(topic)

    def unsubscribe(self, raw_topic):
        '''取消订阅
            比订阅操作更复杂的是退订的时候必须检查顶级主题下的所以子主题都已经退订,如果有一个子主题还在就不能
            完全从zmq当中退订该顶级主题
        '''
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
                    self.callback(json.dumps(dd))
        except:
            pass



@Application.register(path='/api/push/ws')
class PushWs(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        # 每个新的websocket连接进来都会绑定一个基于zmqsocket的Messager对象订阅到本进程的消息发布中心HUB
        self.messager = Messager(self.push)
        # 时间戳,每次客户端发消息都会刷新此时间戳,服务器在发送的时候会判断当前时间减去上次请求的时间戳超过两个心跳周期会主动断开
        self.timestamp = time.time()
        Statistics.CONNECTIONS += 1
        app_log.info('online connections %d', Statistics.CONNECTIONS)

    def push(self, msg):
        if (time.time() - self.timestamp) > 2 * HEARTBEAT_CC:
            # 超过两个心跳周期没有任何数据则断开
            self.close()
        else:
            self.write_message(msg)

    def on_message(self, message):
        app_log.debug(message)
        self.timestamp = time.time() #刷新时间戳
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
        self.messager.destroy()
        Statistics.CONNECTIONS -= 1
        app_log.info('online connections %d', Statistics.CONNECTIONS)
