# -*- coding: utf-8 -*-

__author__ = 'Alexey'

from shared import *
import simulengin as sime

class cBudgetSystem(sime.cDiscreteEventSystem):

    def set_currency_market(self, block):
        self.register_block(block)
        self.currency_market = block

    def set_rawmat_market(self, block):
        self.register_block(block)
        self.rawmat_market = block

    def set_finalproduct_market(self, block):
        self.register_block(block)
        self.finalproduct_market = block

    def set_the_producer(self, block):
        block.s_set_devs(self)
        self.blocks += [block]
        self.the_producer = block

    def build_system(self):
        self.init_goods()

    def init_goods(self):
        self.goods = []
        self.goods += ['Oil1Drum']
        self.goods += ['Oil2Drum']
        self.goods += ['Elastomer']
        self.goods += ['Drum']
        self.goods += ['IBC']
        self.goods += ['FillingGelBulk']
        self.goods += ['FloodingGelBulk']
        self.goods += ['FillingGelDrum']
        self.goods += ['FloodingGelDrum']
        self.goods += ['FillingGelIBC']
        self.goods += ['FloodingGelIBC']

# Элементы симуляционной системы
class cCurrencyMarket(sime.cConnToDEVS):

    def __init__(self):
        self.ccy_quotes = {}

    def __repr__(self):
        return "currency market"

    def log_repr(self):
        return "currency market"

    def my_generator(self):
        if self.devs.logging_on:
            self.devs.simpy_env.process(self.log_printer())
        while 1:
            yield self.devs.simpy_env.process(self.day_step())

    def log_printer(self):
        while 1:
            yield self.devs.simpy_env.timeout(10)
            for k,v in self.ccy_quotes.iteritems():
                if str(k) <> "RUB":
                    av_rate = (v["buy"]+v["sell"])/2
                    self.sent_log("%s is %d"%(str(k), av_rate))

    def add_ccy_quote(self, ccy, buy, sell, stdev):
        if self.ccy_quotes is None:
            self.ccy_quotes = dict()
        quote_i = dict(ccy = ccy, buy = buy, sell = sell, stdev = stdev)
        self.ccy_quotes[ccy] = quote_i

    def get_ccy_buy_quote(self, ccy):
        return self.ccy_quotes[ccy]["buy"]

    def get_ccy_sell_quote(self, ccy):
        return self.ccy_quotes[ccy]["sell"]

    def get_ccy_quote(self, ccy):
        b = self.ccy_quotes[ccy]["buy"]
        s = self.ccy_quotes[ccy]["sell"]
        return (b+s)/2

    def get_ccy_list(self):
        return self.ccy_quotes.keys()

    def day_step(self):
        yield self.devs.simpy_env.timeout(1)
        for q_i in self.ccy_quotes.itervalues():
            buy_i = q_i["buy"]
            sell_i = q_i["sell"]
            stdev_i = q_i["stdev"]
            price_i = (sell_i + buy_i)/2
            spread = price_i - sell_i
            dr = self.devs.random_generator.normalvariate(0,stdev_i)
            newprice = price_i*(1+dr)
            q_i["buy"] = newprice + spread
            q_i["sell"] = newprice - spread

    def convert_rate(self,ccy_from,ccy_to):
        # sum_ccy_to = sum_ccy_from * convert_rate
        fr_r = self.get_ccy_quote(ccy_from)
        to_r = self.get_ccy_quote(ccy_to)
        rt = fr_r / to_r
        return rt

class cMarket(sime.cConnToDEVS):
    def __init__(self):
        self.prices = []

    def add_price(self, good, minqtty, price, ccy):
        price_i = dict(good = good, minqtty = minqtty, price = price, ccy = ccy)
        self.prices += [price_i]

    def give_price(self, good, qtty):
        offers = []
        indeces = []
        indprices = []
        for i, pr in enumerate(self.prices):
            if good == pr['good'] and qtty>=pr["minqtty"]:
                offers += [pr['price']]
                indeces += [i]
                indprices += [pr]
        # FIXME: сделать это безобразие по-нормальному
        minval = min(offers)
        prmin = offers.index(minval)
        return indprices[prmin]

    def __repr__(self):
        return "market"

    def my_generator(self):
        while 1:
            yield self.devs.simpy_env.timeout(1)
            yield self.devs.simpy_env.process(self.day_step())

    def day_step(self):
        yield sime.empty_event(self.devs.simpy_env)

class cRawMaterialsMarket(cMarket):
    def __repr__(self):
        return "raw materials market"

class cFinalProductMarket(cMarket):
    def __init__(self):
        self.clients = []
        super(cFinalProductMarket,self).__init__()

    def init_sim(self):
        self.RES_orders = simpy.Store(self.devs.simpy_env)
        for cl_i in self.clients:
            self.devs.register_block(cl_i)

    def add_client(self, client):
        self.clients += [client]

    def add_order(self, order_i):
        self.RES_orders.put(order_i)

    def __repr__(self):
        return "final materials market"

class cClient(sime.cConnToDEVS):
    def __init__(self, companyname, defferment):
        self.supply_lines = []
        self.companyname = companyname
        self.defferment = defferment

    def __repr__(self):
        return self.companyname

    def add_supply_line(self, good, qtty, freq):
        new_supply_line = {}
        new_supply_line["good"] = good
        new_supply_line["qtty"] = qtty
        new_supply_line["freq"] = freq #every freq times on average
        self.supply_lines += [new_supply_line]

    def init_sim(self):
        for supply_line in self.supply_lines:
            supply_line["last_time"] = self.devs.nowsimtime()

    def my_generator(self):
        for supl_i in self.supply_lines:
            self.devs.simpy_env.process(self.PROC_supply_line(supl_i))
        yield sime.empty_event(self.devs.simpy_env) #Formality

    def ask_about_plans(self):
        # Вызывается cProducer
        # Возвращает сообщения
        # TODO: можно обобщить обмен сообщеняими общим процессом интеракций.
        # Надо только тогда очереди сообщений общие сделать
        msgs = []
        for supl_i in self.supply_lines:
            # Кинем пока план по ближайшим трём отгрузкам
            when1 = supl_i["last_time"] + supl_i["freq"]
            when2 = when1 + supl_i["freq"]
            when3 = when2 + supl_i["freq"]
            a_msg1 = {'good':supl_i['good'], 'qtty':supl_i['qtty'], 'when':when1}
            a_msg2 = {'good':supl_i['good'], 'qtty':supl_i['qtty'], 'when':when2}
            a_msg3 = {'good':supl_i['good'], 'qtty':supl_i['qtty'], 'when':when3}
            msgs += [a_msg1, a_msg2, a_msg3]
        return msgs

    def PROC_supply_line(self, supply_line):
        while 1:
            till_next_order = supply_line["freq"] #TODO: random and account for last_time
            yield self.devs.simpy_env.timeout(till_next_order)
            qtty = supply_line["qtty"]
            good = supply_line["good"]
            supply_line["last_time"] = self.devs.nowsimtime()
            desired_shipment_date = self.devs.nowsimtime()
            new_order = {'qtty': qtty, 'good': good, 'desired_shipment_date': desired_shipment_date, 'client': self}
            self.sent_log("new order " + str(qtty) + " of " + str(good))
            self.devs.finalproduct_market.add_order(new_order)

class cProducer(sime.cConnToDEVS):
    def __init__(self, companyname, RUB_amount):
        self.companyname = companyname
        self.RUB_amount = RUB_amount
        self.prod_units = []

    def __repr__(self):
        return self.companyname

    def init_sim(self):
        # Товары и сырьё
        self.RES_warehouse = cAccount(self.devs.simpy_env)
        # Деньги
        self.RES_money = cAccount(self.devs.simpy_env)
        self.RES_money.add_bulk("RUB", self.RUB_amount)
        # Заявки на закупку сырья
        self.RES_rawmat_buy_orders = simpy.Store(self.devs.simpy_env)
        # Все сделки к выполнению (оплаты/отгрузки...)
        self.RES_deals = simpy.Store(self.devs.simpy_env)
        # Заказы клиентов
        self.RES_client_orders = simpy.Store(self.devs.simpy_env)
        # Заказы в цех
        self.RES_prod_orders = simpy.Store(self.devs.simpy_env)
        # Заказы в оборудование
        self.RES_prod_unit_orders = simpy.Store(self.devs.simpy_env)

        # Бюджет продаж
        self.PLAN_sales_budget = cPlan() # На момент желаемой отгрузки. what = goods
        # План производства
        #self.PLAN_prod_plan = cPlan() # На момент отправки в производство. what = goods (final goods)
        # План снабжения производства
        #self.PLAN_prod_supply_plan = cPlan() # На момент отправки в производство. what = goods (materials)
        # План платежей
        #self.PLAN_payment_plan = cPlan() # На момент платежа. what = 'RUB' (потом можно разные валюты)

    def add_prod_unit(self, prod_unit):
        self.prod_units += [prod_unit]

    def my_generator(self):
        self.devs.simpy_env.process(self.PROC_replenish_inventory())
        self.devs.simpy_env.process(self.PROC_supply_manager())
        self.devs.simpy_env.process(self.PROC_dealer())
        self.devs.simpy_env.process(self.PROC_sales())
        self.devs.simpy_env.process(self.PROC_sales_budget())
        self.devs.simpy_env.process(self.PROC_production_manager())
        self.devs.simpy_env.process(self.PROC_production_implementer())
        for pr_u in self.prod_units:
            pr_u.set_owner(self, self.RES_prod_unit_orders)
            self.devs.add_block_during_simulation(pr_u)
        yield sime.empty_event(self.devs.simpy_env) #Formality

    def PROC_replenish_inventory(self):
        while 1:
            yield self.devs.simpy_env.timeout(15)
            orders = []
            orders += [dict(good = 'Oil1Drum', qtty = 9000)]
            orders += [dict(good = 'Elastomer', qtty = 1000)]
            for ord_i in orders:
                self.sent_log("Ordering " + str(ord_i['qtty']) + " of " + ord_i['good'])
                self.RES_rawmat_buy_orders.put(ord_i)

    def PROC_supply_manager(self):
        while 1:
            ord_i = yield self.RES_rawmat_buy_orders.get()
            # TODO: проверить заказ, оптимизировать?
            deal_i = {}
            deal_i["good"] = ord_i["good"]
            deal_i["qtty"] = ord_i["qtty"]
            deal_i["price"] = self.devs.rawmat_market.give_price(deal_i["good"], deal_i["qtty"])
            deal_i["type"] = "buy_goods"
            deal_i["RUB_to_pay"] = deal_i["qtty"]*deal_i["price"]["price"]*self.devs.currency_market.get_ccy_quote(deal_i["price"]["ccy"])
            self.RES_deals.put(deal_i)

    def PROC_dealer(self):
        while 1:
            deal_i = yield self.RES_deals.get()
            atype = deal_i["type"]
            if atype == "buy_goods":
                self.sent_log("buying " + str(deal_i["qtty"]) + " of " + deal_i["good"])
                self.devs.simpy_env.process(do_buy_prepay_deal(self, deal_i))
                self.sent_log("bought " + str(deal_i["qtty"]) + " of " + deal_i["good"] + " for "+ str(deal_i["RUB_to_pay"]) + " RUB")
            elif atype == "sell_goods":
                self.sent_log("selling " + str(deal_i["qtty"]) + " of " + deal_i["good"])
                if deal_i['client'].defferment > 0:
                    self.devs.simpy_env.process(do_sell_postpay_deal(self, deal_i))
                else:
                    self.devs.simpy_env.process(do_sell_prepay_deal(self, deal_i))

    def PROC_sales(self):
        while 1:
            ord_i = yield self.devs.finalproduct_market.RES_orders.get()
            self.sent_log("new order from " + str(ord_i['client']) + ' for ' + str(ord_i['qtty']) + ' of ' + ord_i['good'])
            # корректируем бюджет продаж (если его нет, ничего не происходит)
            self.PLAN_sales_budget.close_nearest_plan(ord_i['good'], ord_i['qtty'])
            # ставим сделку в план
            deal_i = {}
            deal_i["good"] = ord_i["good"]
            deal_i["qtty"] = ord_i["qtty"]
            deal_i['client'] = ord_i['client']
            deal_i["price"] = self.devs.finalproduct_market.give_price(deal_i["good"], deal_i["qtty"])
            deal_i["type"] = "sell_goods"
            deal_i["RUB_to_receive"] = deal_i["qtty"]*deal_i["price"]["price"]*self.devs.currency_market.get_ccy_quote(deal_i["price"]["ccy"])
            self.RES_deals.put(deal_i)

    def PROC_sales_budget(self):
        # Опрашиваем клиентов о планах на снабжение
        while 1:
            # TODO: не перетирать бюджет, а править (можно сделать правильный ключ для what)
            self.PLAN_sales_budget.whipe()
            # TODO: обобщить коммуникациями между агентами
            for cl_i in self.devs.finalproduct_market.clients:
                self.sent_log("updating sales budget for " + str(cl_i))
                plans = cl_i.ask_about_plans()
                for msg in plans:
                    self.sent_log(str(cl_i) + ' wants to buy ' + str(msg['qtty']) + ' of ' + msg['good'] + ' at ' + str(msg['when']))
                    self.PLAN_sales_budget.add_plan(msg['when'], msg['good'], msg['qtty'])
            yield self.devs.simpy_env.timeout(15)

    def PROC_production_manager(self):
        # Планируем заказы в производство
        while 1:
            horiz1 = self.devs.nowsimtime()
            horiz2 = horiz1 + 30
            # Проверяем, сколько продавцы запланировали отгрузить в след. месяц.
            # Сверяем с остатками на складе. Строим по этому бюджет производства и делаем заказ.
            for good_i in self.PLAN_sales_budget.get_avail_whats():
                to_sale = self.PLAN_sales_budget.get_howmuch_between_whens(good_i, horiz1, horiz2)
                avail = self.RES_warehouse.get_bulk_level(good_i)
                to_produce = to_sale - avail
                if to_produce > 0:
                    self.sent_log('plan to produce ' + str(to_produce) + ' of ' + str(good_i) + ' (in stock: ' +
                                  str(avail) + ', demand: ' + str(to_sale) + ')')
                    # Создаём заказ в производство TODO: бюджет, сделать, чтобы не дублировать
                    prod_order = {'good':good_i, 'qtty':to_produce}
                    self.RES_prod_orders.put(prod_order)
            # Повторяем раз в месяц (то есть, производим ровно месячную потребность)
            yield self.devs.simpy_env.timeout(30)

    def PROC_production_implementer(self):
        while 1:
            prod_order = yield self.RES_prod_orders.get()
            self.sent_log('schedule producing ' + str(prod_order['qtty']) + ' of ' + str(prod_order['good']))
            # Здесь можно сделать умные штуки, вроде баланса нагрузки на оборудование
            # TODO: проверить, что prod_unit может сделать заказ - надо как-то иначе организовать.. Пайп сделать?..
            self.RES_prod_unit_orders.put(prod_order)

def do_buy_prepay_deal(agent, deal_i):
    yield agent.devs.simpy_env.process(agent.RES_money.get_bulk("RUB", deal_i["RUB_to_pay"]))
    agent.RES_warehouse.add_bulk(deal_i["good"], deal_i["qtty"])

def do_sell_prepay_deal(agent, deal_i):
    yield agent.devs.simpy_env.process(agent.RES_warehouse.get_bulk(deal_i['good'], deal_i["qtty"]))
    agent.devs.simpy_env.process(agent.RES_money.add_bulk("RUB", deal_i['RUB_to_receive']))

def do_sell_postpay_deal(agent, deal_i):
    yield agent.devs.simpy_env.process(agent.RES_warehouse.get_bulk(deal_i['good'], deal_i["qtty"]))
    yield agent.devs.simpy_env.timeout(deal_i['client'].defferment)
    agent.devs.simpy_env.process(agent.RES_money.add_bulk("RUB", deal_i['RUB_to_receive']))

class cProductionUnit(sime.cConnToDEVS):
    def __init__(self, name):
        self.production_schemes = []
        self.cost_per_unit = 0
        self.name = name

    def init_sim(self):
        #self.resource = simpy.Resource(self.devs.simpy_env)
        #self.RES_operations = simpy.Store(self.devs.simpy_env)
        pass

    def add_prod_scheme(self, prod_scheme):
        self.production_schemes += [prod_scheme]

    def set_owner(self, owner, order_queue):
        self.owner = owner
        self.RES_order_queue = order_queue

    def my_generator(self):
        while 1:
            prod_order = yield self.RES_order_queue.get()
            # Подбираем "рецепт" производства
            best_scheme = None
            min_time = None
            for prod_sc in self.production_schemes:
                if prod_sc.is_able_to_produce(prod_order['good'], prod_order['qtty']):
                    time_to_produce = prod_sc.get_time_to_produce(prod_order['qtty'])
                    if min_time is None:
                        min_time = time_to_produce
                        best_scheme = prod_sc
                    elif time_to_produce < min_time:
                        min_time = time_to_produce
                        best_scheme = prod_sc
            # TODO: что-то сделать, если не можем произвести
            for op_i in best_scheme.get_operations(prod_order['qtty']):
                if op_i['type'] == 'take_material':
                    yield self.devs.simpy_env.process(self.owner.RES_warehouse.get_bulk(op_i['material'], op_i['qtty']))
                elif op_i['type'] == 'busy':
                    yield self.devs.simpy_env.timeout(op_i['timeout'])
                elif op_i['type'] == 'receive_good':
                    self.owner.RES_warehouse.add_bulk(op_i['good'], op_i['qtty'])

class cProdSchemeMixer(object):
    # No sim logic here
    def __init__(self):
        self.inputs = []
        self.materials_list = []
        self.final_good = None
        self.min_qtty = 0
        self.max_qtty = 0
        self.timeout = 0

    def add_input(self, material, qtty_per_unit):
        self.inputs += [{'material':material, 'qtty_per_unit':qtty_per_unit}]
        if material not in self.materials_list:
            self.materials_list += [material]

    def add_output(self, good):
        self.final_good = good

    def set_scheme_params(self, min_qtty, max_qtty, timeout):
        self.min_qtty = min_qtty
        self.max_qtty = max_qtty
        self.timeout = timeout

    def is_able_to_produce(self, good, final_qtty):
        if final_qtty < self.min_qtty or final_qtty > self.max_qtty:
            return 0
        if good == self.final_good:
            return 1
        return 0

    def get_time_to_produce(self, final_qtty):
        return self.timeout

    def get_operations(self, final_qtty):
        # returns a list of operations to produce final_qtty
        if final_qtty < self.min_qtty or final_qtty > self.max_qtty:
            return None
        operations = []
        for inp in self.inputs:
            mat = inp['material']
            qtty = inp['qtty_per_unit'] * final_qtty
            operations += [{'type':'take_material', 'material':mat, 'qtty':qtty}]
        operations += [{'type':'busy','timeout':self.timeout}]
        operations += [{'type':'receive_good', 'good':self.final_good, 'qtty':final_qtty}]
        return operations

class cPlan(object):
    # Для бюджетов использую
    def __init__(self):
        self.plans = {}
        self.is_sorted = 0
        self.active_whens = []
        self.active_whats = []

    def add_plan(self, pl_when, pl_what, pl_howmuch):
        if not(pl_when in self.plans):
            self.plans[pl_when] = {}
            self.active_whens += [pl_when]
            self.is_sorted = 0
        if not(pl_what in self.plans[pl_when]):
            self.plans[pl_when][pl_what] = 0
            if pl_what not in self.active_whats:
                self.active_whats += [pl_what]
        self.plans[pl_when][pl_what] += pl_howmuch

    def get_avail_whats(self):
        return self.active_whats

    def get_howmuch_between_whens(self, what, when1, when2):
        if not what in self.active_whats:
            return 0
        if when1 > when2:
            raise BaseException('cPlan.get_whats_between_whens(when1, when2) - should be when1<=when2 !')
        N = len(self.active_whens)
        if N==0:
            return 0
        if not self.is_sorted:
            self.active_whens.sort()
            self.is_sorted = 1
        min_when = self.active_whens[0]
        max_when = self.active_whens[N-1]
        if when1 > max_when:
            return 0
        if when2 < min_when:
            return 0

        c = 0
        t = self.active_whens[c]
        howmuch = 0
        while t <= when2 and c <= N-1:
            t = self.active_whens[c]
            if t >= when1:
                if what in self.plans[t]:
                    howmuch += self.plans[t][what]
            c += 1
        return howmuch

    def close_nearest_plan(self, what, howmuch):
        # find last ones with this whats
        N = len(self.active_whens)
        if N==0:
            return
        if not self.is_sorted:
            self.active_whens.sort()
            self.is_sorted = 1
        c = 0
        left_to_close = howmuch
        while left_to_close > 0 and c <= N-1:
            t = self.active_whens[c]
            if what in self.plans[t]:
                if self.plans[t][what] < left_to_close:
                    left_to_close -= self.plans[t][what]
                    self.plans[t][what] = 0
                else:
                    self.plans[t][what] -= left_to_close
                    left_to_close = 0
            c += 1

    def whipe(self):
        self.plans = {}
        self.is_sorted = 0
        self.active_whens = []
        self.active_whats = []

    def forget_history(self, last_when):
        # clean the memory, speedup lookups
        N = len(self.active_whens)
        if N==0:
            return
        if not self.is_sorted:
            self.active_whens.sort()
            self.is_sorted = 1
        min_when = self.active_whens[0]
        max_when = self.active_whens[N-1]
        if min_when >= last_when:
            # no need to forget
            return
        if max_when < last_when:
            # our plan is completely outdated
            self.whipe()
            return

        c = 0
        t = self.active_whens[c]
        while t < last_when and c <= N-1:
            t = self.active_whens[c]
            forget_it = self.plans.pop(t)
            forget_it = None # hopefully it'll work better this way
            c += 1


# Наблюдатели за системой
class cRateObserver(sime.cAbstObserver):
    def observe_data(self):
        for ccy_i in self.system.currency_market.get_ccy_list():
            if str(ccy_i) <> "RUB":
                quote = self.system.currency_market.get_ccy_quote(ccy_i)
                self.record_data(str("RUB -> ") + str(ccy_i), quote)

class cMoneyObserver(sime.cAbstObserver):
    def observe_data(self):
        money_level = self.system.the_producer.RES_money.get_bulk_level("RUB")
        self.record_data("Money in " + str(self.system.the_producer), money_level)

class cInventoryObserver(sime.cAbstObserver):
    def observe_data(self):
        for item in self.system.the_producer.RES_warehouse.get_bulk_item_list():
            item_level = self.system.the_producer.RES_warehouse.get_bulk_level(item)
            self.record_data(item + " at " + str(self.system.the_producer), item_level)

# Вспомогательно
class cAccount(object):
    def __init__(self, simpy_env):
        self.bulk_inventory = {}
        self.store_inventory ={}
        self.simpy_env = simpy_env

    def add_bulk(self, item, amount):
        if not(item in self.bulk_inventory):
            self.bulk_inventory[item] = simpy.Container(simpy_env)
        self.bulk_inventory[item].put(amount)
        yield sime.empty_event(self.devs.simpy_env)

    def get_bulk(self, item, amount):
        if not(item in self.bulk_inventory):
            self.bulk_inventory[item] = simpy.Container(simpy_env)
        yield self.bulk_inventory[item].get(amount)

    def get_bulk_level(self, item):
        if not(item in self.bulk_inventory):
            return 0
        else:
            return self.bulk_inventory[item].level

    def get_bulk_item_list(self):
        return self.bulk_inventory.keys()

if __name__ == "__main__":

    start_date = datetime.date(2015,8,6)
    seed = random.randint(0, sys.maxint)

    # Build system
    simpy_env = simpy.Environment()
    the_devs = cBudgetSystem(simpy_env, start_date)
    the_devs.set_seed(seed)

    ccy_mrkt = cCurrencyMarket()
    ccy_mrkt.add_ccy_quote("USD",62.2,63.5,0.02)
    ccy_mrkt.add_ccy_quote("EUR",68.2,69.9,0.03)
    ccy_mrkt.add_ccy_quote("RUB",1.,1.,0.)
    the_devs.set_currency_market(ccy_mrkt)

    rawmat_mrkt = cRawMaterialsMarket()
    rawmat_mrkt.add_price('Oil1Drum',0.,44.40,"RUB")
    rawmat_mrkt.add_price('Oil2Drum',0.,49.00,"RUB")
    rawmat_mrkt.add_price('Elastomer',0.,17.0,"EUR")
    rawmat_mrkt.add_price('Elastomer',1000.,16.8,"EUR")
    rawmat_mrkt.add_price('Drum',0.,1150.,"RUB")
    rawmat_mrkt.add_price('IBC',0.,4800.,"RUB")
    rawmat_mrkt.add_price('IBC',10.,2800.,"RUB")
    the_devs.set_rawmat_market(rawmat_mrkt)

    final_mrkt = cFinalProductMarket()
    final_mrkt.add_price('FinalGood1',0.,3.,'USD')
    final_mrkt.add_price('FinalGood2',0.,4.,'USD')
    the_devs.set_finalproduct_market(final_mrkt)

    cl1 = cClient('Client 1', 30)
    cl1.add_supply_line('FinalGood1',1000,15)
    cl1.add_supply_line('FinalGood2',1500,30)
    final_mrkt.add_client(cl1)

    cl2 = cClient('Client 2',0)
    cl2.add_supply_line('FinalGood1',100,5)
    cl2.add_supply_line('FinalGood2',70,10)
    final_mrkt.add_client(cl2)

    the_producer = cProducer("Producer", 3000000)
    the_devs.set_the_producer(the_producer)

    # TODO add drums in a nice way
    prod_unit = cProductionUnit('mixer')

    prod_scheme1 = cProdSchemeMixer()
    prod_scheme1.add_input('Oil1Drum', 0.9)
    prod_scheme1.add_input('Elastomer', 0.1)
    prod_scheme1.add_output('FinalGood1')
    prod_scheme1.set_scheme_params(0,9999999,5)
    prod_unit.add_prod_scheme(prod_scheme1)

    prod_scheme2 = cProdSchemeMixer()
    prod_scheme2.add_input('Oil2Drum', 0.89)
    prod_scheme2.add_input('Elastomer', 0.11)
    prod_scheme2.add_output('FinalGood2')
    prod_scheme2.set_scheme_params(0,9999999,5)
    prod_unit.add_prod_scheme(prod_scheme2)

    the_producer.add_prod_unit(prod_unit)

    print("start simulation")
    print('MEDIC!!!')

    # Build runner and observers
    runner = sime.cSimulRunner(the_devs)
    runner.add_observer(cRateObserver,u"Курсы валют",10)
    runner.add_observer(cMoneyObserver,u"Деньги в казне", 1)
    runner.add_observer(cInventoryObserver,u"Товары",1)

    loganddata = runner.run_and_return_log(sim_until = 300, print_console = True, print_to_list = [])

    # Выводим результаты
    log = loganddata['log_list']

    # Выводим наблюдения за временными рядами
    for obs_name, var_name in runner.sim_results.get_available_names():
        data_frame = runner.sim_results.get_dataframe_for_epochvar(obs_name, var_name)
        print(data_frame)






