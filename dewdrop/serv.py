# coding: utf8

import getopt
import tornado.ioloop
import tornado.web
from tornado.log import app_log
from zmq.eventloop.zmqstream import ZMQStream
from zmq.eventloop.ioloop import ZMQIOLoop

loop = ZMQIOLoop()
loop.install()

from lib.autoconf import *
from lib.path import *
from lib.log import *
from biz.core import *


@conf_drawer.register_my_setup(look='push_center')
def all_start(pcc):
    files_list = os.listdir(BIZ_PATH)
    files_list = set(['biz.' + x[:x.rfind(".")] for x in files_list if x.endswith(".py")])
    map(__import__, files_list)
    Hubber(pcc['ihq'])  # subscirbe

class Hubber(object):

    def __init__(self, dist):
        host, port = dist.split(':')
        self._sub = ctx.socket(zmq.SUB)
        self._sub.setsockopt(zmq.SUBSCRIBE, '')
        self._sub.connect('tcp://{host}:{port}'.format(host=host, port=port))
        self._inproc_pub = ctx.socket(zmq.PUB)
        self._inproc_pub.bind('inproc://monster')
        self._sstream = ZMQStream(self._sub)
        self._sstream.on_recv(self.recv)

    def recv(self, frame):
        app_log.info('MESSAGE:%s', frame)
        self._inproc_pub.send_multipart(frame)


if __name__ == "__main__":
    # init
    port = 8888
    includes = None
    opts, argvs = getopt.getopt(sys.argv[1:], "c:p:")
    for op, value in opts:
        if op == '-c':
            includes = value
        elif op == '-p':
            port = int(value)
    if not includes:
        includes = os.path.join(ETC_PATH, 'etc.json')
        print "no configuration found!,will use [%s] instead" % includes
    cpff = ConfigParserFromFile()
    includes | up(cpff.parseall) | up(conf_drawer.setup)
    app = Application(
        xsrf_cookies=False,
        template_path=os.path.join(os.path.dirname(__file__), 'template'),
        static_path=os.path.join(os.path.dirname(__file__), 'static')
    )
    app.listen(port)

    app_log.info('starting...')
    tornado.ioloop.IOLoop.instance().start()
