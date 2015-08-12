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
        self.init_account_structure()
        self.init_movement_types()

    def init_account_structure(self):
        raise NotImplementedError("AccountSystem is not designed - implement init_account_structure first")

    def init_movement_types(self):
        raise NotImplementedError("AccountSystem is not designed - implement init_movement_types first")

    def apply_movement(self, a_movement):
        a_movement.build_actions()
        for act in a_movement.actions:
            self._apply_action(act)

    def get_account_net(self, acc_name):
        if not(acc_name in self.accounts):
            raise BaseException("account system has no account named " + acc_name)
        acc = self.accounts[acc_name]
        #debit = acc.

    def _apply_action(self, action):
        # Ищем счет
        if not(action.account_name in self.accounts):
            raise BaseException("account system has no account named " + acc_name)
        acc = self.accounts[action.account_name]

        # Добавляем движение
        acc._apply_action(action)

    def _add_account(self, account, account_name):
        self.accounts[account_name] = account

class cAccount(object):
    def __init__(self):
        # Словари values_dt, values_kt, values_net - значения учета.
        #   например, values_net[good][shipdoc] - это {cost:<some cost>, qtty:<some qtty>} по товару по документу.
        # сам лист хранит лишь названия, значения в словарях.
        # TODO: it's faster to have one values with debit, credit inside
        self.values_dt = {}
        self.values_ct = {}
        self.layers = []
        self.dims = {}
        self.init_dims_and_layers()

    def init_dims_and_layers(self):
        raise NotImplementedError("Account is not designed - implement init_dims_and_layers first")

    def iter_totals(self):
        pass
        # if len(self.layers) == 1:
        #     for k_i in self.values_dt:
        #         yield [k_i

    def _apply_action(self, action):
        if action.type == "debit":
            v = self.values_dt
            v2 = self.values_ct
        elif action.type == "credit":
            v = self.values_ct
            v2 = self.values_dt
        l = action.layer_name

        if l not in self.layers:
            raise BaseException("[cAccount] - wrong layer in action " + str(action))

        # Пока предположим, что длина action.dimensions - макс три элемента. Потом подумаем, как обобщить..
        if len(action.dimensions) == 1:
            subc1 = action.dimensions[0]
            if not(subc1 in v):
                v[subc1] = {}
                v2[subc1] = {}
                for lay in self.layers:
                    v[subc1][lay] = 0
                    v2[subc1][lay] = 0
            v[subc1][l] += action.value

        elif len(action.dimensions) == 2:
            subc1 = action.dimensions[0]
            subc2 = action.dimensions[1]
            if not(subc1 in v):
                v[subc1] = {}
                v2[subc1] = {}
            if not(subc2 in v[subc1]):
                v[subc2] = {}
                v2[subc2] = {}
                for lay in self.layers:
                    v[subc2][lay] = 0
                    v2[subc2][lay] = 0
            v[subc2][l] += action.value

        elif len(action.dimensions) == 3:
            subc1 = action.dimensions[0]
            subc2 = action.dimensions[1]
            subc3 = action.dimensions[2]
            if not(subc1 in v):
                v[subc1] = {}
                v2[subc1] = {}
            if not(subc2 in v[subc1]):
                v[subc2] = {}
                v2[subc2] = {}
            if not(subc3 in v[subc2]):
                v[subc3] = {}
                v2[subc3] = {}
                for lay in self.layers:
                    v[subc3][lay] = 0
                    v2[subc3][lay] = 0
            v[subc3][l] += action.value

class cAccountMovement(object):
    # Здесь хранится логика разнесения некоторой операции по счетам. Документ, в общем.
    def __init__(self, moment):
        self.moment = moment
        self.actions = []

    def build_actions(self):
        raise NotImplementedError()

class cAccountAction(object):
    # Элемент движения документа
    def __init__(self):
        self.dims = {} #values per level inside
        self.type = None
        self.account_name = None
        self.dimensions = None
        self.layer_name = None
        self.value = None

    def __repr__(self):
        return str(self.type) + " of " + str(self.account_name) + " " + str(self.layer_name) + " for " + str(self.value) + " dims: " + str(self.dimensions)

    def debit(self, account_name, dimensions, layer_name, value):
        self.type = "debit"
        self._set_action(account_name, dimensions, layer_name, value)

    def credit(self, account_name, dimensions, layer_name, value):
        self.type = "credit"
        self._set_action(account_name, dimensions, layer_name, value)

    def _set_action(self, account_name, dimensions, layer_name, value):
        self.account_name = account_name
        self.dimensions = dimensions # список субконто
        self.layer_name = layer_name
        self.value = value

# Конкретная реализация учета производства
class cAccountSystemBasic(cAccountSystem):
    def init_account_structure(self):
        self._add_account(cAccountRawMaterials(),"10")
        self._add_account(cAccountPayable(),"60")

    def init_movement_types(self):
        pass

class cAccountInventoryForSale(cAccount):
    def init_dims_and_layers(self):
        pass

class cAccountRawMaterials(cAccount):
    def init_dims_and_layers(self):
        self.dims = {'warehouse':'value', 'good':'value', 'shipment':'movement'}
        self.layers = ['cost', 'qtty']

class cAccountUnfinishedProduction(cAccount):
    def init_dims_and_layers(self):
        pass

class cAccountRecievables(cAccount):
    def init_dims_and_layers(self):
        pass


class cAccountPayable(cAccount):
    def init_dims_and_layers(self):
        self.dims = {'counterparty':'value', 'currency':'value', 'shipment':'movement'}
        self.layers = ['money']

class cMVBuyRawMaterials(cAccountMovement):
    # Получаем сырьё, отдаём деньги
    def __init__(self, moment):
        super(cMVBuyRawMaterials, self).__init__(moment)
        self.goods = []
        self.counterparty_name = None
        self.currency_name = None
        self.warehouse = None
        self.currency_rate = 1

    def __repr__(self):
        return "movement @ " + str(self.moment) + ": buy raw materials from " + str(self.counterparty_name)

    def set_contract(self, counterparty_name, currency_name, warehouse, currency_rate = 1):
        self.counterparty_name = counterparty_name
        self.currency_name = currency_name
        self.warehouse = warehouse
        self.currency_rate = currency_rate # Если не в рублях расчеты

    def add_good(self, good, qtty, cost):
        # cost - в варлюте расчетов
        self.goods += [{'good':good, 'qtty':qtty, 'cost':cost}]

    def build_actions(self):
        # Add items to inventory
        total_debt = 0
        for g_i in self.goods:
            dims = [self.warehouse, g_i['good'], self]
            act_one = cAccountAction()
            act_one.debit('10', dims, 'qtty', g_i['qtty'])
            act_two = cAccountAction()
            act_two.debit('10', dims, 'cost', g_i['cost'] * self.currency_rate)
            self.actions += [act_one, act_two]
            total_debt += g_i['cost']
        # Add payable
        dims = [self.counterparty_name, self.currency_name, self]
        act_pay = cAccountAction()
        act_pay.credit('60', dims, 'money', total_debt)
        self.actions += [act_pay]


# Пример.
if __name__ == "__main__":
    AccSys = cAccountSystemBasic()

    # 1 - buy some materials
    buy_doc = cMVBuyRawMaterials(0)
    buy_doc.set_contract('oil supplier','RUB','the warehouse')
    buy_doc.add_good('oil 1',1000.,1000*44.1)
    buy_doc.add_good('oil 2',2000.,2000*48.1)
    AccSys.apply_movement(buy_doc)

    # 2 - make a good from materials


    # 3 - pay for materials

    # 4 - sell materials

    # 5 - receive money for goods

    # 6 - fix profits
