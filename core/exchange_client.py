"""
=========================================================
AI Signal Engine
Exchange Client
Version : 5.0
=========================================================

Exchange Gateway

تمام ارتباط موتور با صرافی از این کلاس انجام می‌شود.

Engine های پروژه نباید مستقیماً Provider را بشناسند.

Provider از طریق:
    ExchangeClient(provider=...)

انتخاب می‌شود.

نمونه:

    ExchangeClient()

یا:

    ExchangeClient("TABDEAL")

یا:

    ExchangeClient("NOBITEX")
=========================================================
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from providers.base_provider import BaseProvider
from providers.nobitex_provider import NobitexProvider

try:
    from providers.tabdeal_provider import TabdealProvider
except ImportError:
    TabdealProvider = None


class ExchangeClient:
    """
    لایه Gateway بین Engine و Exchange Provider.
    """

    # =====================================================
    # INIT
    # =====================================================

    def __init__(
        self,
        provider: Optional[Any] = None,
        exchange_name: Optional[str] = None,
    ):
        self.logger = logging.getLogger("ExchangeClient")

        self.connected = False

        # -------------------------------------------------
        # Provider object مستقیم
        # -------------------------------------------------

        if provider is not None:

            if not hasattr(provider, "get_ohlcv"):
                raise TypeError(
                    "Provider must implement get_ohlcv()"
                )

            self.provider = provider

        else:

            name = (
                exchange_name
                or os.getenv("EXCHANGE_NAME")
                or "NOBITEX"
            )

            self.provider = self._create_provider(name)

        self.logger.info(
            "ExchangeClient initialized | provider=%s",
            self.provider_name,
        )

    # =====================================================
    # PROVIDER FACTORY
    # =====================================================

    def _create_provider(self, exchange_name: str) -> BaseProvider:
        """
        ساخت Provider بر اساس نام صرافی.
        """

        name = str(exchange_name).strip().upper()

        if name in {
            "TABDEAL",
            "TABAADOL",
            "TABADOL",
            "تبدیل",
        }:

            if TabdealProvider is None:
                raise ImportError(
                    "TabdealProvider is not available."
                )

            return TabdealProvider()

        if name in {
            "NOBITEX",
            "NOBITEX_PROVIDER",
        }:

            return NobitexProvider()

        raise ValueError(
            f"Unsupported exchange provider: {exchange_name}"
        )

    # =====================================================
    # CONNECT
    # =====================================================

    def connect(self) -> bool:
        """
        اتصال به Provider.
        """

        try:

            self.connected = bool(
                self.provider.ping()
            )

            if self.connected:

                self.logger.info(
                    "Connected | provider=%s",
                    self.provider_name,
                )

            else:

                self.logger.error(
                    "Connection failed | provider=%s",
                    self.provider_name,
                )

            return self.connected

        except Exception:

            self.connected = False

            self.logger.exception(
                "Exchange connection failed"
            )

            return False

    # =====================================================
    # DISCONNECT
    # =====================================================

    def disconnect(self) -> None:
        """
        قطع ارتباط.
        """

        try:

            close_method = getattr(
                self.provider,
                "close",
                None,
            )

            if callable(close_method):
                close_method()

        except Exception:

            self.logger.exception(
                "Provider close failed"
            )

        finally:

            self.connected = False

    # =====================================================
    # RECONNECT
    # =====================================================

    def reconnect(self) -> bool:

        self.disconnect()

        return self.connect()

    # =====================================================
    # PING
    # =====================================================

    def ping(self) -> bool:

        try:

            return bool(
                self.provider.ping()
            )

        except Exception:

            self.logger.exception(
                "Provider ping failed"
            )

            return False

    # =====================================================
    # HEALTH
    # =====================================================

    def health_check(self) -> Dict[str, Any]:

        ping_result = self.ping()

        try:
            server_time = (
                self.provider.get_server_time()
            )
        except Exception:
            server_time = None

        return {
            "provider": self.provider_name,
            "connected": self.connected,
            "ping": ping_result,
            "server_time": server_time,
        }

    # =====================================================
    # SYMBOLS
    # =====================================================

    def symbols(self) -> List[str]:

        return self.provider.get_symbols()

    get_symbols = symbols

    # =====================================================
    # TICKER
    # =====================================================

    def ticker(
        self,
        symbol: str,
    ) -> Dict[str, Any]:

        return self.provider.get_ticker(
            symbol
        )

    get_ticker = ticker

    # =====================================================
    # LAST PRICE
    # =====================================================

    def last_price(
        self,
        symbol: str,
    ) -> Optional[float]:

        ticker = self.provider.get_ticker(
            symbol
        )

        if not ticker:
            return None

        value = ticker.get("last")

        if value is None:
            value = ticker.get("price")

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    get_last_price = last_price

    # =====================================================
    # ORDER BOOK
    # =====================================================

    def orderbook(
        self,
        symbol: str,
        limit: int = 50,
    ) -> Dict[str, Any]:

        try:

            return self.provider.get_orderbook(
                symbol=symbol,
                limit=limit,
            )

        except TypeError:

            # سازگاری با Provider های قدیمی
            return self.provider.get_orderbook(
                symbol
            )

    get_orderbook = orderbook

    # =====================================================
    # OHLCV
    # =====================================================

    def ohlcv(
        self,
        symbol: str,
        timeframe: str = "15m",
        limit: int = 500,
    ) -> List[Dict[str, Any]]:

        return self.provider.get_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )

    get_ohlcv = ohlcv

    # =====================================================
    # KLINES
    # =====================================================

    def klines(
        self,
        symbol: str,
        timeframe: str = "15m",
        limit: int = 500,
    ) -> List[Dict[str, Any]]:

        return self.provider.get_klines(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )

    get_klines = klines

    # =====================================================
    # OHLC
    # =====================================================

    def ohlc(
        self,
        symbol: str,
        timeframe: str = "15m",
        limit: int = 500,
    ) -> List[Dict[str, Any]]:

        return self.provider.get_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )

    get_ohlc = ohlc

    # =====================================================
    # SERVER TIME
    # =====================================================

    def server_time(self) -> int:

        return self.provider.get_server_time()

    get_server_time = server_time

    # =====================================================
    # PROVIDER INFO
    # =====================================================

    def provider_info(self) -> Dict[str, Any]:

        info_method = getattr(
            self.provider,
            "info",
            None,
        )

        if callable(info_method):

            try:
                return info_method()
            except Exception:
                self.logger.exception(
                    "Provider info failed"
                )

        return {
            "name": self.provider_name,
            "connected": self.connected,
        }

    # =====================================================
    # BALANCE
    # =====================================================

    def balance(self):

        method = getattr(
            self.provider,
            "get_balance",
            None,
        )

        if not callable(method):

            raise NotImplementedError(
                "Provider does not support get_balance()"
            )

        return method()

    get_balance = balance

    # =====================================================
    # POSITIONS
    # =====================================================

    def positions(self):

        method = getattr(
            self.provider,
            "get_positions",
            None,
        )

        if not callable(method):

            raise NotImplementedError(
                "Provider does not support get_positions()"
            )

        return method()

    get_positions = positions

    # =====================================================
    # OPEN ORDERS
    # =====================================================

    def open_orders(
        self,
        symbol: Optional[str] = None,
    ):

        method = getattr(
            self.provider,
            "get_open_orders",
            None,
        )

        if not callable(method):

            raise NotImplementedError(
                "Provider does not support "
                "get_open_orders()"
            )

        try:
            return method(symbol=symbol)
        except TypeError:
            return method(symbol)

    get_open_orders = open_orders

    # =====================================================
    # CANCEL ORDER
    # =====================================================

    def cancel_order(
        self,
        order_id: Any,
        symbol: Optional[str] = None,
    ):

        method = getattr(
            self.provider,
            "cancel_order",
            None,
        )

        if not callable(method):

            raise NotImplementedError(
                "Provider does not support "
                "cancel_order()"
            )

        try:
            return method(
                order_id=order_id,
                symbol=symbol,
            )
        except TypeError:
            return method(order_id)

    # =====================================================
    # PLACE ORDER
    # =====================================================

    def place_order(self, **kwargs):

        method = getattr(
            self.provider,
            "place_order",
            None,
        )

        if not callable(method):

            raise NotImplementedError(
                "Provider does not support "
                "place_order()"
            )

        return method(**kwargs)

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self) -> None:

        self.disconnect()

        self.logger.info(
            "Exchange Client Closed"
        )

    # =====================================================
    # STATUS
    # =====================================================

    @property
    def is_connected(self) -> bool:

        return self.connected

    # =====================================================
    # PROVIDER NAME
    # =====================================================

    @property
    def provider_name(self) -> str:

        return self.provider.__class__.__name__

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self) -> str:

        return (
            f"<ExchangeClient "
            f"provider={self.provider_name} "
            f"connected={self.connected}>"
        )

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(self):

        self.connect()

        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ):

        self.shutdown()

        return False