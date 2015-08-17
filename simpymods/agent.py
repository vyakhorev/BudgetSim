# -*- coding: utf-8 -*-

__author__ = 'Alexey'

import simulengin

class cAgent(simulengin.cConnToDEVS):
    """
    Каркас для привязки модулей
    """
    def __init__(self, name):
        self.name = name
        # All the processes, resources and plans are also available as attributes
        self.processes = {}
        self.resources = {}
        self.plans = {}

    def __repr__(self):
        return self.name

    # def add_module(self, new_module):
    #     """
    #     :new_module: один из модулей
    #     """
    #

    def init_sim(self):
        pass

    def my_generator(self):
        while 1:
            self.sent_log("I'm alive")
            yield self.simpy_env.timeout(5)

# Test it
if __name__ == "__main__":
    pass
