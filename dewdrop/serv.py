# coding: utf8

import getopt
from tornado.log import app_log
from zmq.eventloop.zmqstream import ZMQStream
from zmq.eventloop.ioloop import ZMQIOLoop

loop = ZMQIOLoop()
loop.install()

from lib.autoconf import *
from lib.path import *
from lib.log import *
from biz.core import *

'''
    conf_drawer是一个配置管理器的实例,类型Config定义在lib.autoconf中,register_my_setup
    装饰器会在加载文件的时候执行,把各个文件的setup函数append到其setups列表中去,所以理论上它
    先于main函数的执行,而main函数会调用conf_drawer的setup函数,其中就是遍历注册的setups列
    执行注册过来的各种setup函数
'''
@conf_drawer.register_my_setup(look='push')
def all_start(pcc):
    files_list = os.listdir(BIZ_PATH)
    files_list = set(['biz.' + x[:x.rfind(".")] for x in files_list if x.endswith(".py")])
    map(__import__, files_list)
    Hubber(pcc['ihq'])  # subscirbe

class Hubber(object):
    '''
        此类为一个本地的pub/sub-HUB,任何新websocket连接进来都会通过一个zmqsocket订阅到HUB
        的pub端,与此同时这个HUB自己也会订阅一个真正的消息中心iHQ

        websocket连接中通过ipc连接协议订阅HUB

        HUB通过tcp连接协议订阅iHQ
    '''
    def __init__(self, dist):
        host, port = dist.split(':')
        self._sub = ctx.socket(zmq.SUB)
        self._sub.setsockopt(zmq.SUBSCRIBE, '')
        self._sub.connect('tcp://{host}:{port}'.format(host=host, port=port))
        self._inproc_pub = ctx.socket(zmq.PUB)
        self._inproc_pub.bind('inproc:///tmp/monster_{}'.format(pid))
        self._sstream = ZMQStream(self._sub)
        self._sstream.on_recv(self.recv)

    def recv(self, frame):
        app_log.info('MESSAGE:%s', frame)
        # TODO case:写缓存满,先使用nowait方式写,如果捕获Again异常,把内容压入一个deque中,使用on_write来写
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
        xsrf_cookies=False
    )
    app.listen(port)
    app_log.info('[{}]starting...'.format(os.getpid()))
    loop.instance().start()
