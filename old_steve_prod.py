# -*- coding: utf-8 -*-

__author__ = 'Alexey'

import simpymods
from simpymods import simpy
import datetime
import random
import sys

"""
Не работающий и нигде не использующийся файл - но в нём есть здравые идеи
"""

class cCrafter(simpymods.simulengin.cConnToDEVS):
    def __init__(self):
        super(cCrafter, self).__init__()
        self.receipt_classes = []
        self.running_receipts = []

    def init_sim(self):
        self.RES_prod_orders = simpy.Store(self.simpy_env)
        # for i, rec_i in enumerate(self.receipts):
        #     self.devs.add_block(rec_i, "receipt_"+str(i))

    def add_prod_order(self, item, qtty):
        self.RES_prod_orders.put({'item':item,'qtty':qtty})

    def add_receipt(self, a_receipt_class):
        self.receipt_classes += [a_receipt_class]

    def find_receipt(self, item_name):
        acc_recs = []
        for rec_cl_i in self.receipt_classes:
            if item_name == rec_cl_i.output_item:
                acc_recs += [rec_cl_i]
        if len(acc_recs) == 0:
            return None
        return self.devs.random_generator.choice(acc_recs)

    def my_generator(self):
        while 1:
            prod_order = yield self.RES_prod_orders.get()
            item, qtty = prod_order['item'], prod_order['qtty']
            rec_class = self.find_receipt(item)
            if rec_class is None:
                self.sent_log("Unable to find a receipt for " + str(item) + " - stunned for 10 minutes")
                self.RES_prod_orders.put(prod_order)
                yield self.simpy_env.timeout(10)
            else:
                #TODO: проверить наличие в ящике
                self.do_receipt(rec_class, qtty)

    def do_receipt(self, a_receipt_class, qtty):
        new_production_process = a_receipt_class()
        new_production_process.set_crafter(self)
        self.devs.add_block_during_simulation(new_production_process, do_register = 0)
        new_production_process.add_ingoing_request(qtty)
        self.running_receipts += [new_production_process]

    def receive_back_request(self, item, qtty):
        self.add_prod_order(item, qtty)


class cReceiptTourch(simpymods.simulengin.cConnToDEVS):
    output_item = 'tourch'
    input_items = {'wooden_stick':1, 'coal':1}

    def set_ingoing_queue(self, a_queue):
        self.ingoing_requests = a_queue

    def add_outgoing(self, qtty):
        for item_i, qtty_per_unit_i in self.input_items.iteritems():
            self.outgoing_requests.put({'item':item_i,'qtty':qtty*qtty_per_unit_i})

    def init_sim(self):
        self.ingoing_requests = simpy.Store(self.simpy_env)
        self.outgoing_requests = simpy.Store(self.simpy_env)

    def set_crafter(self, a_crafter):
        self.crafter = a_crafter

    def add_ingoing_request(self, qtty):
        self.ingoing_requests.put({'item':self.output_item,'qtty':qtty})

    def my_generator(self):
        while 1:
            req_i = yield self.ingoing_requests.get()
            if req_i['item'] == self.output_item:
                self.sent_log("doing " + str(req_i['qtty']) + " of " + str(req_i['item']))
                self.add_outgoing(req_i['qtty'])
                yield self.simpy_env.timeout(5)
            else:
                self.sent_log("wrong order - unable to do receipt")
                self.crafter.receive_back_request(req_i['item'], req_i['qtty'])
                yield self.simpy_env.timeout(5)

if __name__ == "__main__":

    start_date = datetime.date(2015,8,6)
    seed = random.randint(0, sys.maxint)

    # Build system
    simpy_env = simpy.Environment()
    the_devs = cProductionSystem(simpy_env, start_date)
    the_devs.set_seed(seed)

    crafter = cCrafter()
    the_devs.add_block(crafter, "crafter")

    crafter.add_receipt(cReceiptTourch)

    print("start simulation")

    runner = simpymods.simulengin.cSimulRunner(the_devs)

    loganddata = runner.run_and_return_log(sim_until = 300, print_console = True, print_to_list = [])

    # Выводим результаты
    log = loganddata['log_list']