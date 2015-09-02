#coding=utf-8
# author Rowland
# edit 2014-03-19 14:16:46

import logging
import logging.config
import requests
import os, urllib, urllib2, re, time

from autoconf import conf_drawer
from web import err
import path

@conf_drawer.register_my_setup(look='logging', level=1)
def set_up(cfg):
    log_path = os.path.join(path._ETC_PATH, cfg['config_file'])
    logging.config.fileConfig(log_path)


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