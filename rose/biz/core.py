#coding:utf8

import zmq, time

import traceback
from abc import *
from zmq.eventloop.zmqstream import ZMQStream
from lib.autoconf import conf_drawer
from lib.log import Log

rose = None


@conf_drawer.register_my_setup(look='radio')
def init(confs):
    global rose
    rose = Rose(confs)
    assert rose
    rose.set_handler('ping', PingHandler)


class AbsHandler(object):
    @abstractmethod
    def process(self, pub, topic, body):
        pass


class DefaultHandler(AbsHandler):

    def process(self, pub, topic, body):
        pub.send_multipart([topic, body])


class PingHandler(AbsHandler):

    def process(self, pub, topic, body):
        pass


class Rose(object):

    def __init__(self, confs):
        self.confs = confs
        self.plant()
        self.handlers = {}

    def set_handler(self, topic, handler):
        self.handlers[topic] = handler

    def sprinkling(self, msg):
        try:
            topic, body = msg[0].split('----')
            #Log.rose_log().debug(msg)
            handler = self.handlers.get(topic, DefaultHandler)()
            handler.process(self.pub, topic, body)
            #time.sleep(0.09)
            self.ressock.send('ok')
        except Exception, e:
            self.ressock.send(str(e))
            Log.rose_log().exception(e)

    def plant(self):
        self.ctx = zmq.Context()
        self.pub = self.ctx.socket(zmq.PUB)
        self.pub.bind(self.confs['pub'])
        self.ressock = self.ctx.socket(zmq.REP)
        self.ressock.bind(self.confs['protocol'])
        self.responder = ZMQStream(self.ressock)
        self.responder.on_recv(self.sprinkling)



