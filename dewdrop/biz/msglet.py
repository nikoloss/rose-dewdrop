import zmq
from zmq.eventloop.zmqstream import ZMQStream
from lib.autoconf import conf_drawer
from tornado.log import app_log

config = {}
ctx = zmq.Context()


@conf_drawer.register_my_setup(look='radio')
def set_up(confs):
    config.update(confs)
    MsgletConf(config)


class MsgletConf(object):

    def __init__(self, configer):
        self.socket_pub = ctx.socket(zmq.PUB)
        self.socket_subs = []
        try:
            self.socket_pub.bind(configer['protocol_a'])
            configer['protocol'] = configer['protocol_a']
        except:
            self.socket_pub.bind(configer['protocol_b'])
            configer['protocol'] = configer['protocol_b'].replace('*', 'localhost')
        for sub in configer['sub_to']:
            socket_sub = ctx.socket(zmq.SUB)
            socket_sub.connect(sub)
            socket_sub.setsockopt(zmq.SUBSCRIBE, '')
            stream_sub = ZMQStream(socket_sub)
            stream_sub.on_recv(self.receiving)

    def receiving(self, items):
        if len(items) == 1:
            body = items[0]
            self.socket_pub.send(body)
        else:
            channel = items[0]
            body = items[1]
            self.socket_pub.send_multipart([channel, body])


class Msglet(object):

    def __init__(self, callback):
        self.callback = callback
        self.bind()

    def bind(self):
        self.socket = ctx.socket(zmq.SUB)
        self.socket.connect(config['protocol'])
        self.stream = ZMQStream(self.socket)
        self.stream.on_recv(self.callback)

    def subscribe(self, channel):
        self.socket.setsockopt_string(zmq.SUBSCRIBE, channel)

    def close(self):
        self.stream.close()

