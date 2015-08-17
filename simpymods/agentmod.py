# -*- coding: utf-8 -*-

__author__ = 'Alexey'

import simulengin

class cAgentMod(simulengin.cConnToDEVS):
    """
    У модуля агента есть ресурсы, процессы, планы (возможно ещё что-то появится).
    При подключении это всё передаётся агенту.
    Помогает структурировать логику поведения агента на отдельные составляющие
    """
    def __init__(self, module_name):
        super(cAgentMod, self).__init__(self) #Там ничего не происходит пока
        self.module_name = module_name
        self.parent_agent = None
        self.processes = {}
        self.resources = {}
        self.plans = {}

    def __repr__(self):
        if self.parent_agent is None:
            return self.module_name
        else:
            return self.parent_agent.name + ":" + self.module_name

    def init_sim(self):
        # Здесь надо инициировать все ресурсы
        pass

    def register_resource(self, new_resource, resource_name):
        if resource_name in



# Test it
if __name__ == "__main__":
    pass
