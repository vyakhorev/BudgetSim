# -*- coding: utf-8 -*-

__author__ = 'Alexey'

from shared import *
import simulengin as sime

class cBudgetSystem(sime.cDiscreteEventSystem):

    def set_currency_market(self, block):
        block.s_set_devs(self)
        self.blocks += [block]
        self.currency_market = block

    def set_rawmat_market(self, block):
        block.s_set_devs(self)
        self.blocks += [block]
        self.rawmat_market = block

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
        self.pending_orders = []

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
            yield self.devs.simpy_env.process(self.day_step())

    def day_step(self):
        yield self.devs.simpy_env.timeout(1)
        self.settle_orders()

    def settle_orders(self):
        pass

class cRawMaterialsMarket(cMarket):
    def __repr__(self):
        return "raw materials market"

    def settle_orders(self):
        self.sent_log('settling orders...')

class cFinalProductMarket(cMarket):
    def __init__(self):
        self.clients = []
        self.orders = []
        super(cFinalProductMarket,self).__init__()

    def init_sim(self):
        self.RES_orders = simpy.Store(self.devs.simpy_env)

    def add_client(self,clientname,good):
        #adding new client to list
        if clientname not in (self.clients):
            client = {'clientname': clientname ,'good': good}
            self.clients.append(client)

    def add_order(self):
        pass

    def my_generator(self):
        while 1:
#            for cl_i in self.clients:
#                self.orders += {cl_i['clientname'],cl_i['Good']}

            self.RES_orders.put(self.clients)
            yield self.devs.simpy_env.timeout(1)

    def __repr__(self):
        return "final materials market"

    def settle_orders(self):
        self.sent_log('settling orders...')


class cProducer(sime.cConnToDEVS):
    def __init__(self, companyname, RUB_amount):
        self.companyname = companyname
        self.RUB_amount = RUB_amount

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

    def my_generator(self):
        self.devs.simpy_env.process(self.PROC_replenish_inventory())
        self.devs.simpy_env.process(self.PROC_supply_manager())
        self.devs.simpy_env.process(self.PROC_dealer())
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
                self.sent_log("selling " + str(deal_i))

def do_buy_prepay_deal(agent, deal_i):
    yield agent.devs.simpy_env.process(agent.RES_money.get_bulk("RUB", deal_i["RUB_to_pay"]))
    agent.RES_warehouse.add_bulk(deal_i["good"], deal_i["qtty"])

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

    the_producer = cProducer("Producer", 1000000)
    the_devs.set_the_producer(the_producer)

    print("start simulation")

    # Build runner and observers
    runner = sime.cSimulRunner(the_devs)
    runner.add_observer(cRateObserver,u"Курсы валют",10)
    runner.add_observer(cMoneyObserver,u"Деньги в казне", 1)
    runner.add_observer(cInventoryObserver,u"Товары",1)

    loganddata = runner.run_and_return_log(sim_until = 60, print_console = True, print_to_list = [])

    # Выводим результаты
    log = loganddata['log_list']

    # Выводим наблюдения за временными рядами
    for obs_name, var_name in runner.sim_results.get_available_names():
        data_frame = runner.sim_results.get_dataframe_for_epochvar(obs_name, var_name)
        print(data_frame)






