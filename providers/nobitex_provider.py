"""
=========================================================
AI SIGNAL ENGINE
Nobitex Provider
Version : 11.0 Enterprise
=========================================================

وظایف
------

• ارتباط مستقیم با API نوبیتکس
• دریافت OHLCV
• دریافت Ticker
• دریافت OrderBook
• مدیریت Cache
• مدیریت Retry
• مدیریت Rate Limit
• تبدیل تایم‌فریم‌های اختصاصی موتور
• ارائه رابط استاندارد برای ExchangeClient

این فایل هیچ تحلیل تکنیکالی انجام نمی‌دهد.

=========================================================
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import requests

from config.settings import (
    API_RETRY,
    API_RETRY_DELAY,
    API_TIMEOUT,
    NOBITEX_BASE_URL,
)

logger = logging.getLogger("NobitexProvider")


class NobitexProvider:
    """
    Provider رسمی نوبیتکس

    تمام ارتباط با REST API فقط از این کلاس انجام می‌شود.
    """

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        self.base_url = NOBITEX_BASE_URL.rstrip("/")

        self.timeout = API_TIMEOUT

        self.retry = API_RETRY

        self.retry_delay = API_RETRY_DELAY

        self.session = requests.Session()

        self.lock = threading.Lock()

        self.cache: Dict[str, Any] = {}

        # مدت اعتبار کش (ثانیه)
        self.cache_timeout = 15

        # محدودکننده درخواست‌ها
        self.last_request_time = 0.0

        self.minimum_request_interval = 0.25

        logger.info("Nobitex Provider V11 Loaded")
    # =====================================================
    # Resolution
    # =====================================================

    def _resolution(self, timeframe: str):

        tf = timeframe.lower()

        mapping = {

            "1m": "1",
            "3m": "3",
            "5m": "5",
            "15m": "15",
            "30m": "30",
            "1h": "60",
            "4h": "240",
            "6h": "360",
            "1d": "D",

        }

        return mapping.get(tf)

    # =====================================================
    # Parent Timeframe
    # =====================================================

    def _parent_timeframe(self, timeframe: str):

        tf = timeframe.lower()

        if tf == "2h":
            return "1h"

        if tf == "8h":
            return "4h"

        if tf == "12h":
            return "4h"

        if tf in ("2d", "3d", "1w", "1mth", "1month", "1mon"):
            return "1d"

        return timeframe

    # =====================================================
    # Aggregate Factor
    # =====================================================

    def _factor(self, timeframe: str):

        tf = timeframe.lower()

        if tf == "2h":
            return 2

        if tf == "8h":
            return 2

        if tf == "12h":
            return 3

        if tf == "2d":
            return 2

        if tf == "3d":
            return 3

        if tf == "1w":
            return 7

        if tf in ("1mth", "1month", "1mon"):
            return 30

        return 1
    # =====================================================
    # HTTP Request
    # =====================================================

    def _request(
        self,
        symbol: str,
        resolution: str,
        countback: int,
    ) -> Optional[dict]:

        url = f"{self.base_url}/market/udf/history"

        params = {
            "symbol": symbol,
            "resolution": resolution,
            "to": int(time.time()),
            "countback": countback,
        }

        for attempt in range(1, self.retry + 1):

            try:

                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                )

                if response.status_code == 429:

                    wait = max(
                        self.retry_delay,
                        attempt * 2,
                    )

                    logger.warning(
                        f"429 Too Many Requests [{symbol}] -> Sleep {wait}s"
                    )

                    time.sleep(wait)
                    continue

                response.raise_for_status()

                data = response.json()

                return data

            except Exception as ex:

                logger.warning(
                    f"Retry {attempt}/{self.retry} [{symbol}] : {ex}"
                )

                time.sleep(self.retry_delay)

        return None

    # =====================================================
    # Parse History
    # =====================================================

    def _parse_history(
        self,
        data: Optional[dict],
    ) -> List[dict]:

        if not data:
            return []

        if data.get("s") != "ok":
            return []

        t = data.get("t", [])
        o = data.get("o", [])
        h = data.get("h", [])
        l = data.get("l", [])
        c = data.get("c", [])
        v = data.get("v", [])

        candles: List[dict] = []

        for i in range(len(t)):

            candles.append({

                "time": int(t[i]),

                "open": float(o[i]),

                "high": float(h[i]),

                "low": float(l[i]),

                "close": float(c[i]),

                "volume": float(v[i]),

            })

        return candles

    # =====================================================
    # Aggregate Candles
    # =====================================================

    def _aggregate(
        self,
        candles: List[dict],
        factor: int,
    ) -> List[dict]:

        if factor <= 1:
            return candles

        result = []

        index = 0

        while index < len(candles):

            group = candles[index:index + factor]

            if len(group) < factor:
                break

            result.append({

                "time": group[0]["time"],

                "open": group[0]["open"],

                "high": max(x["high"] for x in group),

                "low": min(x["low"] for x in group),

                "close": group[-1]["close"],

                "volume": sum(x["volume"] for x in group),

            })

            index += factor

        return result

    # =====================================================
    # Cache
    # =====================================================

    def _cache_key(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> str:

        return f"{symbol}_{timeframe}_{limit}"

    # -----------------------------------------------------

    def _load_cache(
        self,
        key: str,
    ):

        item = self.cache.get(key)

        if item is None:
            return None

        if time.time() - item["time"] > self.cache_timeout:

            del self.cache[key]

            return None

        return item["data"]

    # -----------------------------------------------------

    def _save_cache(
        self,
        key: str,
        data,
    ):

        self.cache[key] = {

            "time": time.time(),

            "data": data,

        }
    # =====================================================
    # Get History
    # =====================================================

    def get_history(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 300,
    ) -> List[dict]:

        key = self._cache_key(
            symbol,
            timeframe,
            limit,
        )

        cached = self._load_cache(key)

        if cached is not None:
            return cached

        # --------------------------------------------
        # تعیین تایم‌فریم والد
        # --------------------------------------------

        parent_tf = self._parent_timeframe(
            timeframe
        )

        resolution = self._resolution(
            parent_tf
        )

        if resolution is None:

            logger.error(
                f"Unsupported TimeFrame : {timeframe}"
            )

            return []

        factor = self._factor(
            timeframe
        )

        # برای تایم‌فریم‌های تجمیعی کندل بیشتری می‌گیریم
        countback = limit * factor + factor

        raw = self._request(

            symbol=symbol,

            resolution=resolution,

            countback=countback,

        )

        candles = self._parse_history(
            raw
        )

        if not candles:

            logger.warning(
                f"History Error [{symbol}]"
            )

            return []

        # --------------------------------------------
        # مرتب‌سازی
        # --------------------------------------------

        candles.sort(
            key=lambda x: x["time"]
        )

        # --------------------------------------------
        # حذف کندل تکراری
        # --------------------------------------------

        unique = []

        last_time = None

        for candle in candles:

            if candle["time"] == last_time:
                continue

            unique.append(candle)

            last_time = candle["time"]

        candles = unique

        # --------------------------------------------
        # ساخت تایم‌فریم‌های مصنوعی
        # --------------------------------------------

        candles = self._aggregate(

            candles,

            factor,

        )

        # --------------------------------------------
        # آخرین limit کندل
        # --------------------------------------------

        candles = candles[-limit:]

        self._save_cache(

            key,

            candles,

        )

        return candles
    # =====================================================
    # OHLCV
    # =====================================================

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 300,
    ) -> List[dict]:

        return self.get_history(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )

    # =====================================================
    # Market Data
    # =====================================================

    def get_market_data(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 300,
    ) -> Optional[dict]:

        candles = self.get_history(
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

            "time": [c["time"] for c in candles],

            "open": [c["open"] for c in candles],

            "high": [c["high"] for c in candles],

            "low": [c["low"] for c in candles],

            "close": [c["close"] for c in candles],

            "volume": [c["volume"] for c in candles],

            "last_price": candles[-1]["close"],

        }

    # =====================================================
    # Ticker
    # =====================================================

    def get_ticker(
        self,
        symbol: str,
    ) -> Optional[dict]:

        candles = self.get_history(
            symbol=symbol,
            timeframe="1h",
            limit=2,
        )

        if not candles:
            return None

        last = candles[-1]

        return {

            "symbol": symbol,

            "last": last["close"],

            "price": last["close"],

            "open": last["open"],

            "high": last["high"],

            "low": last["low"],

            "volume": last["volume"],

            "time": last["time"],

        }

    # =====================================================
    # Last Price
    # =====================================================

    def get_last_price(
        self,
        symbol: str,
    ) -> Optional[float]:

        ticker = self.get_ticker(symbol)

        if ticker is None:
            return None

        return ticker["last"]

    # =====================================================
    # OrderBook
    # =====================================================

    def get_orderbook(
        self,
        symbol: str,
    ) -> dict:

        url = f"{self.base_url}/v2/orderbook/{symbol}"

        try:

            response = self.session.get(
                url,
                timeout=self.timeout,
            )

            response.raise_for_status()

            return response.json()

        except Exception as ex:

            logger.warning(
                f"OrderBook Error [{symbol}] : {ex}"
            )

            return {}

    # =====================================================
    # Symbols
    # =====================================================

    def get_symbols(self):

        return [

            "BTCUSDT",

            "ETHUSDT",

            "BNBUSDT",

            "SOLUSDT",

            "XRPUSDT",

            "DOGEUSDT",

            "ADAUSDT",

            "AVAXUSDT",

        ]
    # =====================================================
    # Ping
    # =====================================================

    def ping(self) -> bool:

        try:

            url = f"{self.base_url}/market/stats"

            response = self.session.get(

                url,

                params={

                    "srcCurrency": "BTC",

                    "dstCurrency": "USDT",

                },

                timeout=self.timeout,

            )

            return response.status_code == 200

        except Exception:

            return False

    # =====================================================
    # Server Time
    # =====================================================

    def get_server_time(self):

        try:

            return int(time.time())

        except Exception:

            return None

    # =====================================================
    # Provider Information
    # =====================================================

    def info(self):

        return {

            "provider": "Nobitex",

            "version": "10.0",

            "connected": self.ping(),

            "cache_items": len(self.cache),

            "cache_timeout": self.cache_timeout,

        }

    # =====================================================
    # Health Check
    # =====================================================

    def health_check(self):

        try:

            test = self.get_history(

                symbol="BTCUSDT",

                timeframe="1h",

                limit=2,

            )

            return {

                "status": "OK",

                "provider": "Nobitex",

                "connected": self.ping(),

                "candles": len(test),

                "cache": len(self.cache),

            }

        except Exception as ex:

            return {

                "status": "ERROR",

                "provider": "Nobitex",

                "error": str(ex),

            }

    # =====================================================
    # Clear Cache
    # =====================================================

    def clear_cache(self):

        with self.lock:

            self.cache.clear()

        logger.info(

            "Provider Cache Cleared"

        )

    # =====================================================
    # Close
    # =====================================================

    def close(self):

        try:

            self.session.close()

        except Exception:

            pass

        self.clear_cache()

        logger.info(

            "Nobitex Provider Closed"

        )

    # =====================================================
    # Shutdown
    # =====================================================

    def shutdown(self):

        self.close()

    # =====================================================
    # Context Manager
    # =====================================================

    def __enter__(self):

        return self

    def __exit__(

        self,

        exc_type,

        exc_val,

        exc_tb,

    ):

        self.close()

        return False
# =====================================================
# DataFrame
# =====================================================

def get_dataframe(
    self,
    symbol: str,
    timeframe: str,
    limit: int = 300,
):

    try:

        import pandas as pd

        candles = self.get_history(

            symbol=symbol,

            timeframe=timeframe,

            limit=limit,

        )

        if not candles:

            return pd.DataFrame()

        df = pd.DataFrame(candles)

        df["datetime"] = pd.to_datetime(

            df["time"],

            unit="s",

        )

        df.set_index(

            "datetime",

            inplace=True,

        )

        df.sort_index(

            inplace=True,

        )

        return df

    except Exception as ex:

        logger.warning(

            f"DataFrame Error [{symbol}] : {ex}"

        )

        return None


# =====================================================
# Cache
# =====================================================

def clear_cache(self):

    with self.lock:

        self.cache.clear()

    logger.info(

        "Provider Cache Cleared"

    )


# =====================================================
# Close
# =====================================================

def close(self):

    try:

        self.session.close()

    except Exception:

        pass

    self.clear_cache()

    logger.info(

        "Nobitex Provider Closed"

    )


# =====================================================
# Shutdown
# =====================================================

def shutdown(self):

    self.close()


# =====================================================
# Context Manager
# =====================================================

def __enter__(self):

    return self


def __exit__(

    self,

    exc_type,

    exc_val,

    exc_tb,

):

    self.close()

    return False


# =====================================================
# String Representation
# =====================================================

def __repr__(self):

    return (

        f"<NobitexProvider "

        f"connected={self.ping()} "

        f"cache={len(self.cache)}>"

    )