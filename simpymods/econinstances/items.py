# -*- coding: utf-8 -*-

__author__ = 'Alexey'

from simpymods.misc import abst_key

class cItem(abst_key):
    def __init__(self, name):
        self.name = name

class cMoney(cItem):
    pass

class cGood(cItem):
    def get_exp_life(self):
        return 999999 #how to declare infinity?..

class cPerishableGood(cItem):
    def __init__(self, name, halflife = 1):
        super(cPerishableGood, self).__init__()
        self.halflife = 1

    def get_exp_life(self):
        return self.halflife

class cMachinery(cItem):
    pass


