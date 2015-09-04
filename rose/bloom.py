#coding:utf8
import sys, os
import getopt

from lib import path
from lib.autoconf import *
from biz import core

from zmq.eventloop.ioloop import ZMQIOLoop

from lib.log import Log



def prepare(conf_file):
    cpff = ConfigParserFromFile()
    conf_file | E(cpff.parseall) | E(conf_drawer.setup)


if __name__ == "__main__":
    includes = None
    opts, argvs = getopt.getopt(sys.argv[1:], "c:h")
    for op, value in opts:
        if op == '-c':
            includes = value
            path._ETC_PATH = os.path.dirname(os.path.abspath(value))
        elif op == '-h':
            print u'''使用参数启动:
                        usage: [-c]
                        -c <file> ******加载配置文件
                   '''
            sys.exit(0)
    if not includes:
        includes = os.path.join(path._ETC_PATH, 'includes_dev.json')
        print "no configuration found!,will use [%s] instead" % includes
    prepare(includes)
    Log.rose_log().info("starting...")
    ZMQIOLoop.instance().start()