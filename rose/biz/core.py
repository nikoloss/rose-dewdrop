#coding:utf8

import zmq, time

import traceback
from zmq.eventloop.zmqstream import ZMQStream
from lib.autoconf import conf_drawer

rose = None

@conf_drawer.register_my_setup(look='radio')
def init(confs):
    global rose
    rose = Rose(confs)
    assert rose


class DefaultHandler(object):

    def __init__(self):
        pass

    def process(self, body):
        return body


class Rose(object):

    def __init__(self, confs):
        self.confs = confs
        self.handlers = {
            'ping': DefaultHandler
        }
        self.plant()

    def set_handler(self, topic, handler):
        self.handlers[topic] = handler

    def sprinkling(self, msg):
        try:
            topic, body = msg[0].split('----')
            handler = self.handlers.get(topic, DefaultHandler)()
            self.pub.send_multipart([topic, handler.process(body)])
            #time.sleep(0.09)
            self.ressock.send('ok')
        except Exception, e:
            self.ressock.send(str(e))

    def plant(self):
        self.ctx = zmq.Context()
        self.pub = self.ctx.socket(zmq.PUB)
        self.pub.bind(self.confs['pub'])
        self.ressock = self.ctx.socket(zmq.REP)
        self.ressock.bind(self.confs['protocol'])
        self.responder = ZMQStream(self.ressock)
        self.responder.on_recv(self.sprinkling)



