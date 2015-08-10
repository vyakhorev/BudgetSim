# -*- coding: utf-8 -*-

__author__ = 'Vyakhorev'


# Общие классы

class cAccountSystem(object):
    def __init__(self):
        self.accounts = {}
        # Movement - документ. В нём есть логика.
        self.movements = []
        # Actions - просто изменения, результат работы документа.
        # На них ещё в документе ссылка хранится.
        self.actions = []

    def

    def add_account(self, account, account_name):
        self.account[account_name] = account

class cAccount(object):
    def __init__(self):
        # Словари values_dt, values_kt, values_net - значения учета.
        #   например, values_net[good][shipdoc] - это {cost:<some cost>, qtty:<some qtty>} по товару по документу.
        # layers - размерности учета (обычно 1-2 шт - количество и сумма или просто сумма).
        # сам лист хранит лишь названия, значения в словарях.
        self.values_dt = {}
        self.values_kt = {}
        self.values_net = {}
        self.layers = []
        self.dims = {}
        self.init_dims_and_layers()

    def init_dims_and_layers(self):
        raise NotImplementedError("An error with creating a layer")

class cAccountMovement(object):
    # Здесь хранится логика разнесения некоторой операции по счетам. Документ, в общем.
    def __init__(self, moment):
        self.moment = moment
        self.actions = []

    def build_actions(self):
        raise NotImplementedError()

    def do_movement(self, account_system):
        self.build_actions()
        for act in self.actions:
            account_system

class cAccountAction(object)
    # Элемент движения документа
    def __init__(self,


# Конкретная реализация учета производства


# Пример.