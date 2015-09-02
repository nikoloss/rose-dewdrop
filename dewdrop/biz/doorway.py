#coding: utf-8
import tornado.websocket
from tornado.log import app_log
from core import *
from msglet import Msglet


@Application.register(path='/stare_at/(\w+)')
class EchoWebSocket(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self, object):
        self.ml = Msglet(self.tell)
        self.ml.subscribe(object)

    def on_message(self, message):
        self.write_message(message)

    def tell(self, items):
        self.write_message(items[1])
        app_log.info(items)

    def on_connection_close(self):
        self.ml.close()
