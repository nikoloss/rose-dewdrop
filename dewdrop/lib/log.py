#coding: utf8
import os
from logging.config import fileConfig
import path
from autoconf import conf_drawer


@conf_drawer.register_my_setup(look='logging', level=1)
def setup(log_conf):
    log_path = os.path.join(path.ETC_PATH, log_conf['conf'])
    fileConfig(log_path)