__author__ = 'Alexey'

from shared import simpy

class cAccount(object):
    def __init__(self, simpy_env):
        self.bulk_inventory = {}
        self.store_inventory ={}
        self.simpy_env = simpy_env

    def add_bulk(self, item, amount):
        if not(item in self.bulk_inventory):
            self.bulk_inventory[item] = simpy.Container(self.simpy_env)
        self.bulk_inventory[item].put(amount)

    def get_bulk(self, item, amount):
        if not(item in self.bulk_inventory):
            self.bulk_inventory[item] = simpy.Container(self.simpy_env)
        yield self.bulk_inventory[item].get(amount)

    def get_bulk_level(self, item):
        if not(item in self.bulk_inventory):
            return 0
        else:
            return self.bulk_inventory[item].level

    def get_bulk_item_list(self):
        return self.bulk_inventory.keys()