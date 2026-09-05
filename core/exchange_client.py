"""
=========================================================
AI Signal Engine
Exchange Client
Version : 4.0
=========================================================

Exchange Gateway

تمام ارتباط موتور با صرافی از این کلاس انجام می‌شود.

در آینده فقط Provider عوض می‌شود
و هیچ قسمت دیگری از موتور تغییر نمی‌کند.

Supported Providers

- Nobitex
=========================================================
"""

from __future__ import annotations

import logging
from typing import Any

from providers.nobitex_provider import NobitexProvider


class ExchangeClient:

    """
    Exchange Gateway
    """

    # -------------------------------------------------

    def __init__(self):

        self.logger = logging.getLogger(
            "ExchangeClient"
        )

        self.provider = NobitexProvider()

        self.connected = False

    # -------------------------------------------------
    # Connect
    # -------------------------------------------------

    def connect(self) -> bool:

        """
        اتصال به Provider
        """

        try:

            self.connected = self.provider.ping()

            if self.connected:

                self.logger.info(
                    "Connected To Nobitex"
                )

            else:

                self.logger.error(
                    "Connection Failed"
                )

            return self.connected

        except Exception as e:

            self.connected = False

            self.logger.exception(e)

            return False

    # -------------------------------------------------
    # Disconnect
    # -------------------------------------------------

    def disconnect(self):

        """
        قطع ارتباط
        """

        try:

            if hasattr(
                self.provider,
                "close"
            ):

                self.provider.close()

        finally:

            self.connected = False

    # -------------------------------------------------
    # Reconnect
    # -------------------------------------------------

    def reconnect(self):

        self.disconnect()

        return self.connect()

    # -------------------------------------------------
    # Ping
    # -------------------------------------------------

    def ping(self):

        return self.provider.ping()

    # -------------------------------------------------
    # Health
    # -------------------------------------------------

    def health_check(self):

        return {

            "provider":
                self.provider.__class__.__name__,

            "connected":
                self.connected,

            "ping":
                self.ping(),

            "server_time":
                self.provider.get_server_time(),

        }
    # -------------------------------------------------
    # Symbols
    # -------------------------------------------------

    def symbols(self):

        """
        لیست نمادها
        """

        return self.provider.get_symbols()

    # Alias
    get_symbols = symbols

    # -------------------------------------------------
    # Ticker
    # -------------------------------------------------

    def ticker(
        self,
        symbol: str,
    ) -> dict:

        """
        اطلاعات لحظه‌ای بازار
        """

        return self.provider.get_ticker(symbol)

    # Alias
    get_ticker = ticker

    # -------------------------------------------------
    # Last Price
    # -------------------------------------------------

    def last_price(
        self,
        symbol: str,
    ) -> float | None:

        """
        آخرین قیمت معامله
        """

        ticker = self.provider.get_ticker(symbol)

        if not ticker:
            return None

        return ticker.get("last")

    # Alias
    get_last_price = last_price

    # -------------------------------------------------
    # OrderBook
    # -------------------------------------------------

    def orderbook(
        self,
        symbol: str,
    ) -> dict:

        """
        دفتر سفارشات
        """

        return self.provider.get_orderbook(symbol)

    # Alias
    get_orderbook = orderbook
    # -------------------------------------------------
    # OHLCV
    # -------------------------------------------------

    def ohlcv(
        self,
        symbol: str,
        timeframe: str = "15m",
        limit: int = 500,
    ) -> list:

        """
        دریافت کندل‌ها
        """

        return self.provider.get_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )

    # Alias
    get_ohlcv = ohlcv

    # -------------------------------------------------
    # OHLC
    # -------------------------------------------------

    def ohlc(
        self,
        symbol: str,
        timeframe: str = "15m",
        limit: int = 500,
    ) -> list:

        """
        سازگاری با نسخه‌های قدیمی
        """

        return self.provider.get_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )

    # Alias
    get_ohlc = ohlc

    # -------------------------------------------------
    # Server Time
    # -------------------------------------------------

    def server_time(self):

        """
        زمان سرور
        """

        return self.provider.get_server_time()

    # Alias
    get_server_time = server_time

    # -------------------------------------------------
    # Provider Info
    # -------------------------------------------------

    def provider_info(self):

        """
        اطلاعات Provider
        """

        if hasattr(self.provider, "info"):

            return self.provider.info()

        return {

            "name": self.provider.__class__.__name__,

            "connected": self.connected,

        }
    # -------------------------------------------------
    # Balance
    # -------------------------------------------------

    def balance(self):

        """
        موجودی حساب
        """

        if hasattr(self.provider, "get_balance"):

            return self.provider.get_balance()

        return None

    # Alias
    get_balance = balance

    # -------------------------------------------------
    # Positions
    # -------------------------------------------------

    def positions(self):

        """
        معاملات باز
        """

        if hasattr(self.provider, "get_positions"):

            return self.provider.get_positions()

        return []

    # Alias
    get_positions = positions

    # -------------------------------------------------
    # Open Orders
    # -------------------------------------------------

    def open_orders(self):

        """
        سفارش‌های باز
        """

        if hasattr(self.provider, "get_open_orders"):

            return self.provider.get_open_orders()

        return []

    # Alias
    get_open_orders = open_orders

    # -------------------------------------------------
    # Cancel Order
    # -------------------------------------------------

    def cancel_order(self, order_id):

        """
        لغو سفارش
        """

        if hasattr(self.provider, "cancel_order"):

            return self.provider.cancel_order(order_id)

        raise NotImplementedError(
            "Provider does not support cancel_order()"
        )

    # -------------------------------------------------
    # Place Order
    # -------------------------------------------------

    def place_order(self, **kwargs):

        """
        ثبت سفارش
        """

        if hasattr(self.provider, "place_order"):

            return self.provider.place_order(**kwargs)

        raise NotImplementedError(
            "Provider does not support place_order()"
        )
    # -------------------------------------------------
    # Shutdown
    # -------------------------------------------------

    def shutdown(self):

        """
        خاموش کردن Client
        """

        try:

            self.disconnect()

        except Exception as e:

            self.logger.exception(e)

        self.logger.info(
            "Exchange Client Closed"
        )

    # -------------------------------------------------
    # Status
    # -------------------------------------------------

    @property
    def is_connected(self) -> bool:

        """
        وضعیت اتصال
        """

        return self.connected

    # -------------------------------------------------
    # Provider Name
    # -------------------------------------------------

    @property
    def provider_name(self) -> str:

        """
        نام Provider
        """

        return self.provider.__class__.__name__

    # -------------------------------------------------
    # String
    # -------------------------------------------------

    def __repr__(self):

        return (

            f"<ExchangeClient "

            f"provider={self.provider_name} "

            f"connected={self.connected}>"

        )

    # -------------------------------------------------
    # Context Manager
    # -------------------------------------------------

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