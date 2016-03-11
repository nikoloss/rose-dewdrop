#coding: utf-8

import os, sys, re
import json
from abc import *
import traceback


class ConfigParser(object):
    '''
        This abstract class provides a strategy of how to get those configurations
        through a file or remote config ?
    '''
    @abstractmethod
    def parseall(self, *args):
        pass


class up(object):
    def __init__(self, func):
        self.func = func

    def __ror__(self, inputs):
        return self.func(inputs)


class Configer(object):
    '''
        This class will hold configurations and registered setups(functions)
        It can determine when to setup them
    '''
    config = {}
    setups = []


    def register_my_setup(self, **deco):
        def foo(func):
            location = deco.get('look')
            level = deco.get('level', 99999)
            self.setups.append({
                'func': func,
                'location': location,
                'level': level
            })
            return func

        return foo

    def setup(self, own_cfg, onlevel=0):
        '''
            Call all(or specific level) setup functions which registered via using
            "Configer.register_my_setup" decorator.
            If "onlevel" has been set, only the matched setup fucntions will be
            loaded(or hot reloaded).
            BE CAREFUL! The registed setup function shall apply reload logic in case
            of a runtime-hot-reloaded callback hit.
        '''
        self.setups.sort(key=lambda x: x['level'])
        self.config.update(own_cfg)

        for s in Configer.setups:
            func = s['func']
            location = s['location']
            try:
                if location:
                    func(self.config[location])
                else:
                    func()
            except Exception:
                traceback.print_exc()
                sys.exit(1)

    def on_change(self):
        pass


class ConfigParserFromFile(ConfigParser):
    '''
        via Config Files
    '''
    def parseall(self, fullpath):
        etc = os.path.dirname(fullpath)
        cfg = {}

        with open(fullpath, 'r') as f:
            raw = f.read()
            #去掉多行注释
            raw_escape_comment = re.sub(r'/\*[\s\S]+?\*/', '', raw)
            cfg = json.loads(raw_escape_comment)
            if cfg.get('$includes'):
                for include in cfg['$includes']:
                    icfg = self.parseall(os.path.join(etc, include))
                    cfg.update(icfg)
        return cfg


conf_drawer = Configer()