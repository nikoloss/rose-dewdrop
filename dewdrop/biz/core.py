# coding: utf8
import zmq
import tornado.web
import sys

ctx = zmq.Context()


class Statistics(object):
    CONNECTIONS = 0


class Application(tornado.web.Application):
    handlers = []
    @classmethod
    def register(cls, **kwargs):
        path = kwargs.get('path')

        def deco(handler):
            clazz = handler
            Application.handlers.append((path, clazz))
            return handler

        return deco

    def __init__(self, **kwargs):
        settings = {
            'xsrf_cookies': False,
            'autoreload': True
        }
        kwargs.update(settings)
        if Application.handlers:
            super(Application, self).__init__(Application.handlers, **kwargs)
        else:
            sys.exit(1)
