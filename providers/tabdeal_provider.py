"""
=========================================================
AI Signal Engine
Tabdeal Provider
Version : 1.0
=========================================================

Provider رسمی تبدیل برای اتصال ExchangeClient.

API مستندات تبدیل:
https://docs.tabdeal.org/

فعلاً این Provider برای لایه Market/Data طراحی شده
و ساختار آن طوری است که بعداً قابلیت‌های معامله نیز
بدون تغییر در Engine ها اضافه شوند.
=========================================================
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from providers.base_provider import BaseProvider


class TabdealProvider(BaseProvider):
    """
    Provider صرافی تبدیل.
    """

    DEFAULT_BASE_URL = "https://api1.tabdeal.org"

    # -------------------------------------------------
    # Timeframe mapping
    # -------------------------------------------------

    TIMEFRAME_MAP = {
        "1m": "1m",
        "3m": "3m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "2h": "2h",
        "4h": "4h",
        "6h": "6h",
        "8h": "8h",
        "12h": "12h",
        "1d": "1d",
    }

    # -------------------------------------------------
    # INIT
    # -------------------------------------------------

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 15,
    ):

        self.api_key = (
            api_key
            or os.getenv("TABDEAL_API_KEY")
        )

        self.api_secret = (
            api_secret
            or os.getenv("TABDEAL_API_SECRET")
        )

        self.base_url = (
            base_url
            or os.getenv(
                "TABDEAL_BASE_URL",
                self.DEFAULT_BASE_URL,
            )
        ).rstrip("/")

        self.timeout = int(timeout)

    # =====================================================
    # SYMBOL NORMALIZATION
    # =====================================================

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        """
        تبدیل فرمت‌های رایج نماد به فرمت API تبدیل.

        BTC/USDT
        BTC_USDT
        btcusdt

        -> BTCUSDT
        """

        if not symbol:
            raise ValueError(
                "symbol cannot be empty"
            )

        value = str(symbol).strip().upper()

        value = value.replace(
            "/",
            "",
        )

        value = value.replace(
            "_",
            "",
        )

        value = value.replace(
            "-",
            "",
        )

        return value

    # =====================================================
    # HTTP
    # =====================================================

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Any:

        params = dict(params or {})

        if signed:

            if not self.api_key:
                raise RuntimeError(
                    "TABDEAL_API_KEY is not configured"
                )

            if not self.api_secret:
                raise RuntimeError(
                    "TABDEAL_API_SECRET is not configured"
                )

            params.setdefault(
                "timestamp",
                int(time.time() * 1000),
            )

            query = urlencode(
                params,
                doseq=True,
            )

            signature = hmac.new(
                self.api_secret.encode("utf-8"),
                query.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()

            params["signature"] = signature

        query = urlencode(
            params,
            doseq=True,
        )

        url = f"{self.base_url}{path}"

        if query:
            url = f"{url}?{query}"

        headers = {
            "Accept": "application/json",
            "User-Agent": (
                "AI-Signal-Engine/5.0"
            ),
        }

        if signed:
            headers["X-MBX-APIKEY"] = self.api_key

        request = Request(
            url=url,
            headers=headers,
            method=method.upper(),
        )

        with urlopen(
            request,
            timeout=self.timeout,
        ) as response:

            import json

            raw = response.read()

            return json.loads(
                raw.decode("utf-8")
            )

    # =====================================================
    # PING
    # =====================================================

    def ping(self) -> bool:

        try:

            self._request(
                "GET",
                "/r/api/v1/ping",
            )

            return True

        except Exception:

            return False

    # =====================================================
    # SERVER TIME
    # =====================================================

    def get_server_time(self) -> int:

        result = self._request(
            "GET",
            "/r/api/v1/time",
        )

        return int(
            result["serverTime"]
        )

    # =====================================================
    # SYMBOLS
    # =====================================================

    def get_symbols(self) -> List[str]:

        result = self._request(
            "GET",
            "/r/api/v1/exchangeInfo",
        )

        symbols = []

        for item in result.get(
            "symbols",
            [],
        ):

            if not isinstance(
                item,
                dict,
            ):
                continue

            symbol = (
                item.get("symbol")
                or item.get("tabdealSymbol")
            )

            if symbol:
                symbols.append(
                    str(symbol).upper()
                )

        return sorted(
            set(symbols)
        )

    # =====================================================
    # TICKER
    # =====================================================

    def get_ticker(
        self,
        symbol: str,
    ) -> Dict[str, Any]:

        normalized = (
            self._normalize_symbol(symbol)
        )

        result = self._request(
            "GET",
            "/r/api/v1/ticker/24hr",
            {
                "symbol": normalized,
            },
        )

        if isinstance(
            result,
            list,
        ):

            result = (
                result[0]
                if result
                else {}
            )

        return result or {}

    # =====================================================
    # ORDER BOOK
    # =====================================================

    def get_orderbook(
        self,
        symbol: str,
        limit: int = 50,
    ) -> Dict[str, Any]:

        normalized = (
            self._normalize_symbol(symbol)
        )

        result = self._request(
            "GET",
            "/r/api/v1/depth",
            {
                "symbol": normalized,
                "limit": int(limit),
            },
        )

        return result or {}

    # =====================================================
    # OHLCV
    # =====================================================

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:

        normalized_timeframe = (
            self.TIMEFRAME_MAP.get(
                timeframe
            )
        )

        if normalized_timeframe is None:

            raise ValueError(
                f"Unsupported Tabdeal timeframe: "
                f"{timeframe}"
            )

        normalized_symbol = (
            self._normalize_symbol(symbol)
        )

        result = self._request(
            "GET",
            "/r/api/v1/klines",
            {
                "symbol": normalized_symbol,
                "interval": normalized_timeframe,
                "limit": min(
                    max(int(limit), 1),
                    1000,
                ),
            },
        )

        return self._normalize_klines(
            result
        )

    # =====================================================
    # KLINES
    # =====================================================

    def get_klines(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:

        return self.get_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )

    # =====================================================
    # KLINE NORMALIZER
    # =====================================================

    @staticmethod
    def _normalize_klines(
        rows: Any,
    ) -> List[Dict[str, Any]]:

        if not isinstance(
            rows,
            list,
        ):
            return []

        result = []

        for row in rows:

            # -----------------------------------------
            # Binance-style array
            # -----------------------------------------

            if isinstance(
                row,
                (list, tuple),
            ) and len(row) >= 6:

                result.append(
                    {
                        "timestamp": int(
                            row[0]
                        ),
                        "open": float(
                            row[1]
                        ),
                        "high": float(
                            row[2]
                        ),
                        "low": float(
                            row[3]
                        ),
                        "close": float(
                            row[4]
                        ),
                        "volume": float(
                            row[5]
                        ),
                    }
                )

                continue

            # -----------------------------------------
            # Dict-style fallback
            # -----------------------------------------

            if isinstance(
                row,
                dict,
            ):

                timestamp = (
                    row.get("timestamp")
                    or row.get("openTime")
                    or row.get("time")
                )

                open_price = (
                    row.get("open")
                )

                high_price = (
                    row.get("high")
                )

                low_price = (
                    row.get("low")
                )

                close_price = (
                    row.get("close")
                )

                volume = (
                    row.get("volume")
                    or row.get("vol")
                    or 0
                )

                if timestamp is None:
                    continue

                if (
                    open_price is None
                    or high_price is None
                    or low_price is None
                    or close_price is None
                ):
                    continue

                result.append(
                    {
                        "timestamp": int(
                            timestamp
                        ),
                        "open": float(
                            open_price
                        ),
                        "high": float(
                            high_price
                        ),
                        "low": float(
                            low_price
                        ),
                        "close": float(
                            close_price
                        ),
                        "volume": float(
                            volume
                        ),
                    }
                )

        result.sort(
            key=lambda x: x["timestamp"]
        )

        return result

    # =====================================================
    # BALANCE
    # =====================================================

    def get_balance(self):

        result = self._request(
            "GET",
            "/r/api/v1/account",
            signed=True,
        )

        return result or {}

    # =====================================================
    # OPEN ORDERS
    # =====================================================

    def get_open_orders(
        self,
        symbol: Optional[str] = None,
    ):

        params = {}

        if symbol:
            params["symbol"] = (
                self._normalize_symbol(symbol)
            )

        result = self._request(
            "GET",
            "/r/api/v1/openOrders",
            params=params,
            signed=True,
        )

        return result or []

    # =====================================================
    # CANCEL ORDER
    # =====================================================

    def cancel_order(
        self,
        order_id: Any,
        symbol: Optional[str] = None,
    ):

        params = {
            "orderId": order_id,
        }

        if symbol:
            params["symbol"] = (
                self._normalize_symbol(symbol)
            )

        return self._request(
            "DELETE",
            "/api/v1/order",
            params=params,
            signed=True,
        )

    # =====================================================
    # PLACE ORDER
    # =====================================================

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        client_order_id: Optional[str] = None,
        **kwargs,
    ):

        params = {
            "symbol": self._normalize_symbol(
                symbol
            ),
            "side": str(side).upper(),
            "type": str(order_type).upper(),
            "quantity": quantity,
        }

        if price is not None:
            params["price"] = price

        if stop_price is not None:
            params["stopPrice"] = stop_price

        if client_order_id:
            params["newClientOrderId"] = (
                client_order_id
            )

        params.update(kwargs)

        return self._request(
            "POST",
            "/api/v1/order",
            params=params,
            signed=True,
        )

    # =====================================================
    # INFO
    # =====================================================

    def info(self) -> Dict[str, Any]:

        return {
            "name": "Tabdeal",
            "provider": "TabdealProvider",
            "base_url": self.base_url,
            "authenticated": bool(
                self.api_key
                and self.api_secret
            ),
        }

    # =====================================================
    # CLOSE
    # =====================================================

    def close(self) -> None:
        """
        Provider فعلاً connection دائمی ندارد.
        """
        return None