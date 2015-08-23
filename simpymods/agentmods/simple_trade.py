# -*- coding: utf-8 -*-

__author__ = 'Alexey'
from agentmod import cAgentMod
from simpymods import simpy

class cSimpleTradeMod(cAgentMod):
    """
        Very basic module - buy some random number of goods and offer them to the market with higher price.
        Continue doing so as long as there is some demand.

        Not the best solution (it's better to ask clients first), this thing works for demonstration
        of economic UoW concept.
    """

    def __init__(self, module_name):
        super(cSimpleTradeMod, self).__init__(module_name)

    def init_sim(self):
        super(cSimpleTradeMod, self).init_sim()
        # Add processes / resources / plans here
        self.register_process(self.PROC_seller,'seller')
        self.RES_seller_queue = simpy.Store(self.simpy_env) #Do we need to automate this construction?
        self.register_resource(self.RES_seller_queue, 'seller_queue')

        self.register_process(self.PROC_buyer,'buyer')
        self.RES_buyer_queue = simpy.Store(self.simpy_env)
        self.register_resource(self.RES_buyer_queue, 'buyer_queue')

    def PROC_seller(self):
        while 1: # I can make this loop in regiister_process.. Should I?
            UoW = yield self.RES_seller_queue.get()


    def PROC_buyer(self):
        while 1:
            UoW = yield self.RES_buyer_queue.get()


    def route_UoW(self, UoW):
        if UoW.concrete_type == 'buy_goods':
            self.RES_buyer_queue.put(UoW)
        elif UoW.concrete_type == 'sell_goods':
            self.RES_seller_queue.put(UoW)


