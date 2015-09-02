# coding: utf8
import random
from threading import Thread
from threading import Lock
from core import *
from ant import MazeContext


poller = zmq.Poller()

sock_cache = {}

def initialize():
    assert Config.dists
    assert Config.RESTIMEOUT > 0
    ctx = zmq.Context()
    for dist in Config.dists:
        sock = ctx.socket(zmq.REQ)
        sock.connect(dist)
        sock_cache[dist] = sock

    Tiktok().start()
    Thread(target=Proxy.instance().looping).start()


def send(topic, body):
    return __send('{topic}----{body}'.format(topic=topic, body=body))


def __send(msg):
    while not MazeContext.last_choice:
        pass
    choice = MazeContext.last_choice
    sock = sock_cache[choice]
    sock.send(msg)
    poller.register(sock, zmq.POLLIN)
    if poller.poll(Config.RESTIMEOUT):
        res = sock.recv()
        poller.unregister(sock)
        return res
    else:
        poller.unregister(sock)
        raise IOError('recv timeout!')


def test1():
    tik = time.time()
    for i in range(1000):
        send('bbb', 'hello world')
    tok = time.time()
    print tok - tik

def test2():
    stock_map = {
            'aapl': 100.0,
            'wbai': 20.0,
            'goog': 165.0,
            'baid': 144.0,
            'jd': 33.0,
            'intr': 39.0,
            'shne': 178.0,
            'msft': 43.90,
            'txn': 47.05,
        }
    stock_copy = stock_map.copy()
    while 1:
        r = random.randint(1,100) / 200.0
        time.sleep(r)
        stock = random.choice(stock_map.keys())
        steps = random.randint(-100, 100) / 100.0
        org_price = stock_map[stock]
        latest_price = stock_copy[stock] + steps
        stock_copy[stock] = latest_price
        counts = latest_price - org_price
        rge = counts / org_price * 100.0
        #print stock, steps, org_price, latest_price, counts, rge
        send('stock', '%s,%.3g,%.3g,%.3g,%.3g' % (stock, latest_price, counts, rge, steps))



if __name__ == "__main__":
    Config.dists = ['tcp://192.168.56.1:9074', 'tcp://192.168.56.101:9074', 'tcp://localhost:9074']
    Config.WAKER_PROTOCOL = 'tcp://localhost:10910'
    Config.INFORM_PROTOCOL = 'tcp://*:10910'
    initialize()
    test2()
