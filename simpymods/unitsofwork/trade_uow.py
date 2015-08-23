# -*- coding: utf-8 -*-

__author__ = 'Alexey'

from base import cEconomicUoW, cUnitOfWork

class cBuyGoodsUoW(cEconomicUoW):
    """
        Instruction to buy some goods
    """
    concrete_type = "buy_goods"

    pass

class cSellGoodsUoW(cEconomicUoW):
    """
        Instruction to sell some goods
    """
    concrete_type = "sell_goods"

    pass