# -*- coding: utf-8 -*-

__author__ = 'Alexey'

import simpymods
import datetime
import random
import sys

class cBudgetSystem(simpymods.simulengin.cDiscreteEventSystem):
    def set_the_producer(self, block):
        block.s_set_devs(self)
        self.blocks += [block]
        self.the_producer = block

    def build_system(self):
        pass

if __name__ == "__main__":

    start_date = datetime.date(2015,8,6)
    seed = random.randint(0, sys.maxint)

    # Build system
    simpy_env = simpymods.simpy.Environment()
    the_devs = cBudgetSystem(simpy_env, start_date)
    the_devs.set_seed(seed)

    the_producer = simpymods.cAgent("The producer")
    the_devs.set_the_producer(the_producer)

    print("start simulation")

    # Build runner and observers
    runner = simpymods.simulengin.cSimulRunner(the_devs)

    loganddata = runner.run_and_return_log(sim_until = 300, print_console = True, print_to_list = [])

    # Выводим результаты
    log = loganddata['log_list']

    # # Выводим наблюдения за временными рядами
    # import matplotlib
    # for obs_name, var_name in runner.sim_results.get_available_names():
    #     data_frame = runner.sim_results.get_dataframe_for_epochvar(obs_name, var_name)
    #     data_frame.plot()
    #     print(data_frame)
    # matplotlib.pyplot.show()