# -*- coding: utf-8 -*-

import simpymods
from simpymods import simpy
import datetime
import random
import sys

class cProductionSystem(simpymods.simulengin.cDiscreteEventSystem):
    def build_system(self):
        pass

class cSteve(simpymods.simulengin.cConnToDEVS):
    def __repr__(self):
        return "Steve"

    def my_generator(self):
        while 1:
            self.sent_log("I want to go mining, I need some tourches")
            # Сделали новый процесс производства
            # new_production_process = cReceiptTourch()
            new_production_process = recipe_Torch()
            self.devs.add_block_during_simulation(new_production_process, do_register=0)

            #new_production_process2 = recipe_Coal()
            #self.devs.add_block_during_simulation(new_production_process2, do_register=0)

            # Теперь в процессе есть ссылки на среду симуляции и запущен my_generator
            new_production_process.add_ingoing_request(50) #процесс 1 раз запустится и всё
            yield self.simpy_env.timeout(100)


class Cconnecter():
    pass


class cRecipe(simpymods.simulengin.cConnToDEVS):
    # Базовый рецепт
    def __init__(self, name, duration, mydict):
        # name - name of recipe
        # duration - time consuming
        # mydict - dict of components

        self.recipe_name = name
        self.duration = duration
        self.recipe_dict = mydict

        print('{0} from {1} in {2} minutes'.format(self.recipe_name, self.recipe_dict, self.duration))
        #print self.__class__().__repr__()

    def __repr__(self):
        return self.recipe_name

    def init_sim(self):
        self.ingoing_requests = simpy.Store(self.simpy_env)

    def add_ingoing_request(self, qtty):
        self.ingoing_requests.put({'item': self.recipe_name, 'qtty':qtty})

    def my_generator(self):

        req_i = yield self.ingoing_requests.get()

        self.sent_log("doing " + str(req_i['qtty']) + " of " + str(req_i['item']))
        yield self.simpy_env.timeout(self.duration)


class recipe_Torch(cRecipe):
    # name = 'Torch'
    # duration = 5
    # components = {'planks': 1, 'coal': 2}

    def __init__(self):
        name = 'Torch'
        duration = 5
        components = {'planks': 1, 'coal': 2}
        self.add_sub_recipe('coal')

        super(recipe_Torch, self).__init__(name, duration, components)

    def add_sub_recipe(self, sub):
        #super(recipe_Torch, self).add_complex_recipe(sub)
        pass


class recipe_Coal(cRecipe):

    def __init__(self):
        name = 'Coal'
        duration = 2
        components = {'wood': 1}

        super(recipe_Coal, self).__init__(name, duration, components)




class cReceiptTourch(simpymods.simulengin.cConnToDEVS):
    output_item = 'tourch'
    duration = 5

    def __repr__(self):
        return "Production of " + str(self.output_item)

    def init_sim(self):
        self.ingoing_requests = simpy.Store(self.simpy_env)

    def add_ingoing_request(self, qtty):
        self.ingoing_requests.put({'item':self.output_item,'qtty':qtty})

    def my_generator(self):
        req_i = yield self.ingoing_requests.get()
        self.sent_log("doing " + str(req_i['qtty']) + " of " + str(req_i['item']))
        yield self.simpy_env.timeout(self.duration)


class cCrafter(simpymods.simulengin.cConnToDEVS):
    pass


if __name__ == "__main__":
    start_date = datetime.date(2015,8,6)  # Дату надо бы убрать потом из ядра...
    seed = random.randint(0, sys.maxint)

    # Build system
    simpy_env = simpy.Environment()
    the_devs = cProductionSystem(simpy_env, start_date)
    the_devs.set_seed(seed)

    Steve = cSteve()
    the_devs.add_block_named(Steve, "Steve")



    print("start simulation")

    runner = simpymods.simulengin.cSimulRunner(the_devs)

    loganddata = runner.run_and_return_log(sim_until = 300, print_console = True, print_to_list = [])

    # Выводим результаты
    log = loganddata['log_list']