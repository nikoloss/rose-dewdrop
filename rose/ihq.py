#coding:utf8
#
#    *************           *************            *************
#    *  client   *           *   client  *            *   client  *
#    *************           *************            *************
#          |                        |                        |
#          |                        |                        |
#     *************          **************          **************
#     * websocket *          *  websocket *          *  websocket *
#     *    HUB    *          *     HUB    *          *      HUB   *
#     *************          **************          **************
#           \ sub                |  sub              sub/
#            \                   |                     /
#              ------------------|--------------------
#                                | pub
#                         ****************
#                         *              *
#                         * ROSE - iHQ   *
#                         *              *
#                         ****************
#                                | sub
#              ------------------|-------------------
#            /                   |                    \
#          /                     |                      \
#     ***********            **********               ************
#     * sdk     *            * sdk    *               * sdk      *
#     * service *            * http   *               * other... *
#     ***********            **********               ************
#


import zmq
import getopt
import sys
from lib.log import logger

poller = zmq.Poller()

'''
    整个information headquarter分为PUB端口跟SUB端口
    SUB端口用来接收SDK下达的消息,然后通过PUB端口广播出去
'''
def serv_forever(sub_p, pub_p):
    context = zmq.Context()
    pub_s = context.socket(zmq.PUB)
    pub_s.bind('tcp://*:{PUB_PORT}'.format(PUB_PORT=pub_p))

    sub_s = context.socket(zmq.SUB)
    sub_s.setsockopt(zmq.SUBSCRIBE, '')
    sub_s.bind('tcp://*:{SUB_PORT}'.format(SUB_PORT=sub_p))

    poller.register(sub_s, zmq.POLLIN)

    socks = dict(poller.poll(360000))
    while 1:
        if socks:
            for sock, event in socks.iteritems():
                if sock is sub_s:
                    frame = sub_s.recv_multipart()
                    logger.info('MESSAGE:%s', frame)
                    pub_s.send_multipart(frame)


if __name__ == '__main__':
    sub_p = 9021
    pub_p = 9022
    opts, argvs = getopt.getopt(sys.argv[1:], "s:p:")
    for op, value in opts:
        if op == '-s':
            sub_p = int(value)
        if op == '-p':
            pub_p = int(value)
    logger.info('starting...')
    serv_forever(sub_p, pub_p)
