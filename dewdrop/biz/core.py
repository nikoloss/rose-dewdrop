#coding: utf-8
import os, sys, json, inspect, time
import tornado.web

from lib.autoconf import conf_drawer
from lib import path
import tornado.ioloop
import tornado.web
from tornado.log import app_log

logger = app_log


@conf_drawer.register_my_setup()
def setup():
    # scan files for first run decorators as a initialization
    files_list = os.listdir(path._BIZ_PATH)
    files_list = set(['.'.join([os.path.basename(path._BIZ_PATH), x[:x.rfind(".")]])
                      for x in files_list if x.endswith(".py")])
    map(__import__, files_list)



class Application(tornado.web.Application):

    handlers = []

    @classmethod
    def register(cls, **kwargs):
        path = kwargs.get('path')
        def deco(Handler):
            clazz = Handler
            Application.handlers.append((path, clazz))
            return Handler
        return deco

    def __init__(self):
        settings = {
            'xsrf_cookies': False,
            'autoreload': True
        }
        if Application.handlers:
            super(Application, self).__init__(Application.handlers, settings)
        else:
            logger.critical('no handlers found in application\'s settings')
            sys.exit(1)

