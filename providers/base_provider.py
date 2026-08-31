"""
=========================================================
AI Signal Engine
Base Provider
=========================================================
"""

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    کلاس پایه تمام Provider ها
    """

    @abstractmethod
    def get_symbols(self):
        """لیست نمادها"""
        pass

    @abstractmethod
    def get_ticker(self, symbol):
        """آخرین قیمت"""
        pass

    @abstractmethod
    def get_orderbook(self, symbol):
        """دفتر سفارشات"""
        pass

    @abstractmethod
    def get_klines(self, symbol, timeframe, limit=500):
        """دریافت کندل"""
        pass

    @abstractmethod
    def get_server_time(self):
        """زمان سرور"""
        pass

    @abstractmethod
    def ping(self):
        """تست اتصال"""
        pass