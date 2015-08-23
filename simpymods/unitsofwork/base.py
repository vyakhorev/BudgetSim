# -*- coding: utf-8 -*-

__author__ = 'Alexey'

"""
    Base interfaces for Units Of Work (UoW). These are the means of communication
    between Agent and it's Modules. UoW must heavily rely and exploit economic or
    management meaning of tasks so that it would be easy to handle them.
    Some of the UoWs must support Cash Flow (CF) and Goods Flow (GF) calculus.
    Type itself is very important since agent routes UoW to modules according
    to UoW type.
"""

from simpymods.econinstances import cMoney, cGood

class cUnitOfWork(object):
    concrete_type = ""

    def __init__(self):
        self.trace = [] # a log
        #self.general_type = ""

class cEconomicUoW(cUnitOfWork):
    """
        Supports CF and GF interfaces
    """
    def __init__(self):
        super(cEconomicUoW, self).__init__()
        self.cf = {} # Key is a currency
        self.gf = {} # Key is an item

    def add_to_cf(self, what, when, howmuch):
        if not(what in self.cf):
            self.cf[what] = cCashFlow()
        self.cf[what].add_flow(when, howmuch)

    def add_to_gf(self, what, when, howmuch):
        if not(what in self.gf):
            self.gf[what] = cGoodsFlow()
        self.gf[what].add_flow(when, howmuch)


class cFlow(object):
    """
        Howmuch and when for a single what.
    """
    #TODO: add some algebra with CF, iterations, zero checking (would be important)
    def __init__(self):
        self.flow = {} #Ordered dict?...
        self.active_whens = []
        self.is_sorted = 0

    def add_flow(self, when, howmuch):
        self.flow[when] = howmuch
        self.active_whens += [when]

    def wipe(self):
        self.flow = {} #Ordered dict?...
        self.active_whens = []
        self.is_sorted = 0

class cCashFlow(cFlow):
    pass

class cGoodsFlow(cFlow):
    pass
