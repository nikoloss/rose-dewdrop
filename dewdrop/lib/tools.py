#coding=utf-8
# author Rowland
# edit 2014-03-19 14:16:46


import requests
import time

from web import err


def fetch(dist, params=None, method='get'):
    r = None
    try:
        if method == 'post':
            r = requests.post(dist, params=params, timeout=5)
        else:
            r = requests.get(dist, params=params, timeout=5)
        if r.status_code != 200:
            e = err.RemoteError
            e.reason = 'http status[%d]' % r.status_code
            raise err.RemoteError()
        return r.content
    except Exception, e:
        #Log().getLog().exception('---url:%s ---', dist)
        raise e
    finally:
        if r:
            r.close()

def hash_choice(array, seed=time.time()):
    length = len(array)
    if length == 0:
        return ''
    index = int(seed % length)
    return array[index]

class XMLUtils(object):

    def parseElement(self, e):
        ret = {}
        if e.text:
            ret['text'] = e.text
        if e.attrib:
            ret['attr'] = e.attrib
        for i in e.iterchildren():
            ret.update({i.tag: self.parseElement(i)})
        return ret