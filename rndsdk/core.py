#coding: utf8

import threading, time
import zmq
from etc import Config
from ant import *


class Proxy(object):

    PING = 'ping----echo'
    _instance_lock = threading.Lock()
    SENDING = 1
    CLOSE = 0

    OPEN_THE_GATE = 'open_the_gate'
    CLOSE_THE_GATE = 'close_the_gate'
    ELECT = 'elect'
    DONE = 'done'

    def __init__(self):
        self.status = Proxy.CLOSE
        self.loop = zmq.Poller()
        self.ctx = zmq.Context()
        self.map = {}
        self._waker = self.ctx.socket(zmq.REP)
        self._waker.bind(Config.INFORM_PROTOCOL)
        self.loop.register(self._waker, zmq.POLLIN)
        for dist in Config.dists:
            # 为每个dist创建socket并绑定小蚂蚁
            ant_sock = self.ctx.socket(zmq.REQ)
            ant_sock.connect(dist)
            MazeContext.choices[dist] = 0
            ant = Ant(dist)
            self.map[ant_sock] = ant
            self.loop.register(ant_sock, zmq.POLLIN | zmq.POLLOUT)
        self.inited = 1

    @staticmethod
    def instance():
        if not hasattr(Proxy, "_instance"):
            with Proxy._instance_lock:
                if not hasattr(Proxy, "_instance"):
                    # New instance after double check
                    Proxy._instance = Proxy()
        return Proxy._instance


    def looping(self):
        while 1:
            socks = self.loop.poll(1000)
            for sock, st in socks:
                if st & zmq.POLLIN:
                    msg = sock.recv()
                    if sock == self._waker:
                        if msg == Proxy.CLOSE_THE_GATE:
                            self.status = Proxy.CLOSE
                        elif msg == Proxy.OPEN_THE_GATE:
                            self.status = Proxy.SENDING
                        elif msg == Proxy.ELECT:
                            convert = dict((v, k) for k, v in MazeContext.choices.items())
                            MazeContext.last_choice = convert[max(convert.keys())]
                        sock.send(Proxy.DONE)
                    else:
                        ant = self.map.get(sock)
                        # 有绑定蚂蚁 说明是Ping包 判断是否需要接着发
                        ant.returned()
                elif st & zmq.POLLOUT:
                    if self.status == Proxy.SENDING:
                        sock.send(Proxy.PING)


class Tiktok(threading.Thread):

    def __init__(self):
        super(Tiktok, self).__init__()
        self.ctx = zmq.Context()
        self.op = self.ctx.socket(zmq.REQ)
        self.op.connect(Config.WAKER_PROTOCOL)

    def run(self):
        while 1:
            if Proxy.instance().inited:
                #clear
                for k in MazeContext.choices.keys():
                    MazeContext.choices[k] = 0
                # 释放蚂蚁
                self.op.send(Proxy.OPEN_THE_GATE)
                self.op.recv()
                # hold for ants' activity
                time.sleep(Config.activity_last)
                # 停止活动
                self.op.send(Proxy.CLOSE_THE_GATE)
                self.op.recv()
                # 推选
                self.op.send(Proxy.ELECT)
                self.op.recv()
                time.sleep(Config.activity_interval)


if __name__ == "__main__":
    Config.dists = ['tcp://localhost:9074', 'tcp://localhost:7795', 'tcp://192.168.56.101:9074']
    Tiktok().start()
    Proxy.instance().looping()

