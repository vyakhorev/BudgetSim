# -*- coding: utf-8 -*-

__author__ = 'Alexey'

from simpymods.simulengin import cConnToDEVS
from simpymods import simpy

class cAgentMod(cConnToDEVS):
    """
    У модуля агента есть ресурсы, процессы, планы (возможно ещё что-то появится).
    При подключении это всё передаётся агенту.
    Помогает структурировать логику поведения агента на отдельные составляющие.
    """
    def __init__(self, module_name):
        super(cAgentMod, self).__init__() #Nothing there at the moment
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

    def set_parent_agent(self, an_agent):
        """
        :param an_agent:
            cAgent instance
        """
        self.parent_agent = an_agent

    def init_sim(self):
        """
            Call self.register_process, self.register_resource, self.register_plan here
        """
        # Basic I/O
        self.RES_input_UoW = simpy.Store(self.simpy_env)
        self.register_resource(self.RES_input_UoW, 'input_UoW')
        self.RES_output_UoW = simpy.Store(self.simpy_env)
        self.register_resource(self.RES_output_UoW, 'output_UoW')
        self.register_process(self.PROC_UoW_servo, 'UoW_servo')

    def PROC_UoW_servo(self):
        """
            This process routes input UoW to other processes with self.route_UoW
        """
        while 1:
            new_UoW = yield self.RES_input_UoW.get()
            self.route_UoW(new_UoW)

    def route_UoW(self, UoW):
        """
            This process routes input UoW to other processes.
            To be implemented in concrete modules (can be partly automated, though...)
        """
        raise NotImplementedError()

    def my_generator(self):
        """
        The ultimate generator function for the module. Start simpy processes here,
        registered process are implemented by default
        """
        for name_i, proc_i in self.processes.iteritems():
            self.simpy_env.process(proc_i())
            self.sent_log("started to " + str(name_i))

    def register_process(self, new_process, process_name):
        """ TODO: args, kwargs
        :param new_process:
            A generator returning simpy.Event (callable). Shall be activated in my_generator.
        :param process_name:
            Unique name, shall be available in module scope
        """
        if process_name in self.processes:
            raise BaseException("process " + process_name + " already set")
        self.processes[process_name] = new_process
        #setattr(self, "PROC_"+process_name, new_process)

    def register_resource(self, new_resource, resource_name):
        """
        :param new_resource:
            simpy.Store / simpy.Container / simulengin.cAccount / ...
        :param resource_name:
            Unique name, shall be available as an attribute
        """
        if resource_name in self.resources:
            raise BaseException("resource " + resource_name + " already set")
        self.resources[resource_name] = new_resource
        #setattr(self, "RES_"+resource_name, new_resource)

    def register_plan(self, new_plan, plan_name):
        """
        :param new_plan:
            Instance of simulengin.cPlan
        :param plan_name:
            A readable name for the plan
        """
        if plan_name in self.plans:
            raise BaseException("plan " + plan_name + " already set")
        self.plans[plan_name] = new_plan
        #setattr(self, "PLAN_"+plan_name, new_plan)

# Test it
if __name__ == "__main__":
    pass
