"""
=========================================================
AI Signal Engine
Base Exchange
Version : 3.0
Professional Edition
=========================================================
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseExchange(ABC):

    def __init__(

        self,

        config,

        logger

    ):

        self.config = config

        self.logger = logger

        self.connected = False

    # =====================================================
    # INFORMATION
    # =====================================================

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def exchange_type(self) -> str:
        """
        spot
        futures
        forex
        stock
        """
        pass

    @abstractmethod
    def version(self) -> str:
        pass

    # =====================================================
    # CONNECTION
    # =====================================================

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        pass

    @abstractmethod
    def reconnect(self) -> bool:
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        pass

    @abstractmethod
    def ping(self) -> float:
        """
        milliseconds
        """
        pass

    @abstractmethod
    def heartbeat(self):
        pass

    # =====================================================
    # ACCOUNT
    # =====================================================

    @abstractmethod
    def account_info(self) -> Dict:
        pass

    @abstractmethod
    def wallet(self) -> Dict:
        pass

    @abstractmethod
    def balance(self) -> float:
        pass

    @abstractmethod
    def free_balance(self) -> float:
        pass

    @abstractmethod
    def locked_balance(self) -> float:
        pass

    # =====================================================
    # MARKET
    # =====================================================

    @abstractmethod
    def symbols(self) -> List[str]:
        pass

    @abstractmethod
    def markets(self) -> List[Dict]:
        pass

    @abstractmethod
    def server_time(self):
        pass

    @abstractmethod
    def exchange_info(self):
        pass

    @abstractmethod
    def ticker(

        self,

        symbol

    ) -> Dict:

        pass

    @abstractmethod
    def tickers(self):

        pass

    @abstractmethod
    def candles(

        self,

        symbol,

        timeframe,

        limit=500

    ):

        pass

    @abstractmethod
    def orderbook(

        self,

        symbol,

        depth=20

    ):

        pass

    @abstractmethod
    def recent_trades(

        self,

        symbol,

        limit=100

    ):

        pass
    # =====================================================
    # ORDERS
    # =====================================================

    @abstractmethod
    def market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        **kwargs
    ) -> Dict:
        pass

    @abstractmethod
    def limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        **kwargs
    ) -> Dict:
        pass

    @abstractmethod
    def stop_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float,
        **kwargs
    ) -> Dict:
        pass

    @abstractmethod
    def stop_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float,
        limit_price: float,
        **kwargs
    ) -> Dict:
        pass

    @abstractmethod
    def oco_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        take_profit: float,
        stop_loss: float,
        **kwargs
    ) -> Dict:
        pass

    @abstractmethod
    def cancel_order(
        self,
        order_id: str
    ) -> bool:
        pass

    @abstractmethod
    def cancel_all_orders(
        self,
        symbol: str = None
    ) -> bool:
        pass

    @abstractmethod
    def order_status(
        self,
        order_id: str
    ) -> Dict:
        pass

    @abstractmethod
    def open_orders(
        self,
        symbol: str = None
    ) -> List[Dict]:
        pass

    @abstractmethod
    def order_history(
        self,
        symbol: str = None,
        limit: int = 100
    ) -> List[Dict]:
        pass

    # =====================================================
    # POSITIONS
    # =====================================================

    @abstractmethod
    def open_positions(self) -> List[Dict]:
        pass

    @abstractmethod
    def position(
        self,
        position_id: str
    ) -> Dict:
        pass

    @abstractmethod
    def close_position(
        self,
        position_id: str
    ) -> bool:
        pass

    @abstractmethod
    def close_all_positions(self) -> bool:
        pass

    # =====================================================
    # FUTURES
    # =====================================================

    @abstractmethod
    def funding_rate(
        self,
        symbol: str
    ):
        pass

    @abstractmethod
    def open_interest(
        self,
        symbol: str
    ):
        pass

    @abstractmethod
    def leverage(
        self,
        symbol: str
    ):
        pass

    @abstractmethod
    def set_leverage(
        self,
        symbol: str,
        leverage: int
    ) -> bool:
        pass

    # =====================================================
    # TRADING RULES
    # =====================================================

    @abstractmethod
    def minimum_order(
        self,
        symbol: str
    ) -> float:
        pass

    @abstractmethod
    def maximum_order(
        self,
        symbol: str
    ) -> float:
        pass

    @abstractmethod
    def minimum_notional(
        self,
        symbol: str
    ) -> float:
        pass

    @abstractmethod
    def price_precision(
        self,
        symbol: str
    ) -> int:
        pass

    @abstractmethod
    def quantity_precision(
        self,
        symbol: str
    ) -> int:
        pass

    @abstractmethod
    def maker_fee(self) -> float:
        pass

    @abstractmethod
    def taker_fee(self) -> float:
        pass

    @abstractmethod
    def trading_enabled(self) -> bool:
    # =====================================================
    # WEBSOCKET / STREAM
    # =====================================================

    @abstractmethod
    def subscribe_ticker(
        self,
        symbol: str
    ) -> bool:
        pass

    @abstractmethod
    def unsubscribe_ticker(
        self,
        symbol: str
    ) -> bool:
        pass

    @abstractmethod
    def subscribe_orderbook(
        self,
        symbol: str
    ) -> bool:
        pass

    @abstractmethod
    def unsubscribe_orderbook(
        self,
        symbol: str
    ) -> bool:
        pass

    @abstractmethod
    def subscribe_trades(
        self,
        symbol: str
    ) -> bool:
        pass

    @abstractmethod
    def unsubscribe_trades(
        self,
        symbol: str
    ) -> bool:
        pass

    @abstractmethod
    def subscribe_candles(
        self,
        symbol: str,
        timeframe: str
    ) -> bool:
        pass

    @abstractmethod
    def unsubscribe_candles(
        self,
        symbol: str,
        timeframe: str
    ) -> bool:
        pass

    # =====================================================
    # UTILITIES
    # =====================================================

    @abstractmethod
    def normalize_symbol(
        self,
        symbol: str
    ) -> str:
        pass

    @abstractmethod
    def validate_symbol(
        self,
        symbol: str
    ) -> bool:
        pass

    @abstractmethod
    def validate_quantity(
        self,
        symbol: str,
        quantity: float
    ) -> bool:
        pass

    @abstractmethod
    def validate_price(
        self,
        symbol: str,
        price: float
    ) -> bool:
        pass

    @abstractmethod
    def round_quantity(
        self,
        symbol: str,
        quantity: float
    ) -> float:
        pass

    @abstractmethod
    def round_price(
        self,
        symbol: str,
        price: float
    ) -> float:
        pass

    @abstractmethod
    def estimate_fee(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float
    ) -> float:
        pass

    @abstractmethod
    def estimate_margin(
        self,
        symbol: str,
        quantity: float,
        leverage: int
    ) -> float:
        pass

    # =====================================================
    # HEALTH
    # =====================================================

    @abstractmethod
    def health_check(self) -> dict:
        pass

    @abstractmethod
    def reconnect_if_needed(self) -> bool:
        pass

    @abstractmethod
    def close(self):
        pass

    # =====================================================
    # DEFAULT METHODS
    # =====================================================

    def ready(self) -> bool:

        return self.is_connected()

    def can_trade(self) -> bool:

        return self.is_connected() and self.trading_enabled()

    def info(self) -> dict:

        return {

            "exchange": self.name(),

            "type": self.exchange_type(),

            "version": self.version(),

            "connected": self.is_connected()

        }

    def __str__(self):

        return f"{self.name()} ({self.exchange_type()})"

    def __repr__(self):

        return self.__str__()
        pass