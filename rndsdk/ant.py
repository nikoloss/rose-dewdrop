#coding: utf8

import random


class MazeContext(object):
    last_choice = None
    choices = {}

    @classmethod
    def chose(cls):
        total_weight = sum(MazeContext.choices.values()) or 1
        dice = random.randint(1, total_weight)
        totoal_cur = 0
        for path, weight in MazeContext.choices.iteritems():
            totoal_cur += weight
            if totoal_cur >= dice:
                return path
        else:
            return random.choice(MazeContext.choices.keys())


class Ant(object):

    def __init__(self, first_choice):
        self.my_choice = first_choice

    def returned(self):
        MazeContext.choices[self.my_choice] += 1

    def chose(self):
        self.my_choice = MazeContext.chose()