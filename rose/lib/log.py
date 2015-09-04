#coding: utf8
import logging, os, path
import logging.config
from autoconf import conf_drawer


@conf_drawer.register_my_setup(look='logging', level=1)
def set_up(cfg):
    global rose_log
    log_path = os.path.join(path._ETC_PATH, cfg['config_file'])
    logging.config.fileConfig(log_path)
    Log.logger = logging.getLogger(cfg['logger'])


class Log(object):
    logger = None

    @staticmethod
    def rose_log():
        return Log.logger