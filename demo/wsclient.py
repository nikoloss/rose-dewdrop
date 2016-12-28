import tornado.websocket
import tornado.ioloop


ioloop = tornado.ioloop.IOLoop.instance()

for x in range(1000):
    tornado.websocket.websocket_connect("ws://localhost:8888/api/push/ws", ioloop)

ioloop.start()
