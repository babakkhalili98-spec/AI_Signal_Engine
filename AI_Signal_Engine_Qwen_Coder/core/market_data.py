"""
=========================================================
AI Signal Engine
Market Data
Version : 3.0.0
=========================================================

وظایف

• دریافت داده خام بازار
• Cache
• Validation
• Retry
• Wrapper برای ExchangeClient

=========================================================
"""

from __future__ import annotations

import logging
import time

from typing import Dict
from typing import Any
from typing import Optional

from core.exchange_client import ExchangeClient


# =========================================================
# Market Data
# =========================================================

class MarketData:

    """
    فقط دریافت داده بازار

    هیچ تحلیل تکنیکالی اینجا انجام نمی‌شود.
    """

    def __init__(self):

        self.logger = logging.getLogger(

            "MarketData"

        )

        self.client = ExchangeClient()

        self.cache: Dict[str, Any] = {}

        self.cache_time = 5

        self.initialized = False

    # -----------------------------------------------------

    def initialize(self):

        """
        اتصال به صرافی
        """

        if self.initialized:

            return

        connected = self.client.connect()

        if not connected:

            raise ConnectionError(
                "Exchange Connection Failed"
            )

        self.initialized = True

        self.logger.info(
            "MarketData Ready"
        )

    # -----------------------------------------------------

    def _cache_key(

        self,

        *args

    ):

        return "_".join(

            map(

                str,

                args

            )

        )

    # -----------------------------------------------------

    def _get_cache(

        self,

        key

    ):

        if key not in self.cache:

            return None

        item = self.cache[key]

        if (

            time.time()

            -

            item["time"]

            >

            self.cache_time

        ):

            del self.cache[key]

            return None

        return item["data"]

    # -----------------------------------------------------

    def _set_cache(

        self,

        key,

        value

    ):

        self.cache[key] = {

            "time":

                time.time(),

            "data":

                value

        }

    # -----------------------------------------------------

    def clear_cache(self):

        self.cache.clear()

        self.logger.info(

            "Market Cache Cleared"

        )
    # -----------------------------------------------------
    # Symbols
    # -----------------------------------------------------

    def get_symbols(self):

        key = self._cache_key("symbols")

        cached = self._get_cache(key)

        if cached is not None:

            return cached

        data = self.client.symbols()

        self._set_cache(

            key,

            data

        )

        return data

    # Alias
    symbols = get_symbols

    # -----------------------------------------------------
    # Ticker
    # -----------------------------------------------------

    def get_ticker(

        self,

        symbol

    ):

        key = self._cache_key(

            "ticker",

            symbol

        )

        cached = self._get_cache(key)

        if cached is not None:

            return cached

        data = self.client.ticker(

            symbol

        )

        self._set_cache(

            key,

            data

        )

        return data

    # Alias
    ticker = get_ticker

    # -----------------------------------------------------
    # Last Price
    # -----------------------------------------------------

    def get_last_price(

        self,

        symbol

    ):

        ticker = self.get_ticker(

            symbol

        )

        if ticker is None:

            return None

        return ticker.get(

            "last"

        )

    # Alias
    last_price = get_last_price

    # -----------------------------------------------------
    # OHLCV
    # -----------------------------------------------------

    def get_ohlcv(

        self,

        symbol,

        timeframe,

        limit=500

    ):

        key = self._cache_key(

            symbol,

            timeframe,

            limit

        )

        cached = self._get_cache(key)

        if cached is not None:

            return cached

        candles = self.client.ohlcv(

            symbol,

            timeframe,

            limit

        )

        self._set_cache(

            key,

            candles

        )

        return candles

    # Alias
    ohlcv = get_ohlcv
    klines = get_ohlcv

    # -----------------------------------------------------
    # OrderBook
    # -----------------------------------------------------

    def get_orderbook(

        self,

        symbol

    ):

        return self.client.orderbook(

            symbol

        )

    # Alias
    orderbook = get_orderbook

    # -----------------------------------------------------
    # Volume
    # -----------------------------------------------------

    def get_volume(

        self,

        symbol

    ):

        ticker = self.get_ticker(

            symbol

        )

        if ticker is None:

            return None

        return ticker.get(

            "volume"

        )
    # -----------------------------------------------------
    # Validate Candles
    # -----------------------------------------------------

    def validate_data(

        self,

        candles

    ):

        """
        بررسی صحت داده‌های کندل
        """

        if candles is None:

            return False

        if not isinstance(

            candles,

            list

        ):

            return False

        if len(candles) == 0:

            return False

        required = [

            "open",

            "high",

            "low",

            "close",

            "volume"

        ]

        for candle in candles:

            for field in required:

                if field not in candle:

                    return False

        return True

    # -----------------------------------------------------
    # Retry OHLCV
    # -----------------------------------------------------

    def safe_ohlcv(

        self,

        symbol,

        timeframe,

        limit=500,

        retry=3

    ):

        """
        دریافت کندل با Retry
        """

        for attempt in range(retry):

            try:

                candles = self.get_ohlcv(

                    symbol,

                    timeframe,

                    limit

                )

                if self.validate_data(

                    candles

                ):

                    return candles

            except Exception as ex:

                self.logger.exception(ex)

            time.sleep(1)

        return None

    # -----------------------------------------------------
    # Scanner Data
    # -----------------------------------------------------

    def get_market_data(
        self,
        symbol,
        timeframe,
        limit=300,
    ):

        candles = self.safe_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )

        if not candles:
            return None

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "candles": candles,
            "open": [c["open"] for c in candles],
            "high": [c["high"] for c in candles],
            "low": [c["low"] for c in candles],
            "close": [c["close"] for c in candles],
            "volume": [c["volume"] for c in candles],
            "time": [c["time"] for c in candles],
            "last_price": candles[-1]["close"],
        }

    # -----------------------------------------------------
    # Health Check
    # -----------------------------------------------------

    def health_check(self):

        """
        وضعیت MarketData
        """

        return {

            "initialized":

                self.initialized,

            "cache_items":

                len(self.cache),

            "exchange":

                self.client.health_check()

        }

    # -----------------------------------------------------
    # Close
    # -----------------------------------------------------

    def close(self):

        """
        بستن اتصال
        """

        try:

            self.client.disconnect()

        except Exception:

            pass

        self.initialized = False

        self.clear_cache()

        self.logger.info(

            "MarketData Closed"

        )

    # -----------------------------------------------------
    # Shutdown
    # -----------------------------------------------------

    def shutdown(self):

        """
        خاموش کردن کامل MarketData
        """

        self.logger.info("")

        self.logger.info("=" * 60)

        self.logger.info(

            "MARKET DATA SHUTDOWN"

        )

        self.logger.info("=" * 60)

        self.close()