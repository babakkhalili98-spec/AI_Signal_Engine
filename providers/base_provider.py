"""
=========================================================
AI Signal Engine
Base Provider
=========================================================

قرارداد مشترک تمام Exchange Provider ها.

هدف:
- جلوگیری از وابستگی مستقیم Engine ها به یک صرافی
- یکسان‌سازی API بین Nobitex / Tabdeal / سایر صرافی‌ها
- حفظ سازگاری با نسخه‌های قدیمی پروژه
=========================================================
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseProvider(ABC):
    """
    Interface مشترک تمام Provider های صرافی.
    """

    # =====================================================
    # MARKET
    # =====================================================

    @abstractmethod
    def get_symbols(self) -> List[str]:
        """دریافت لیست نمادهای قابل معامله."""
        raise NotImplementedError

    @abstractmethod
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """دریافت اطلاعات آخرین قیمت."""
        raise NotImplementedError

    @abstractmethod
    def get_orderbook(
        self,
        symbol: str,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """دریافت دفتر سفارشات."""
        raise NotImplementedError

    # =====================================================
    # OHLCV / KLINES
    # =====================================================

    @abstractmethod
    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """
        دریافت کندل‌ها.

        فرمت استاندارد خروجی:

        {
            "timestamp": ...,
            "open": ...,
            "high": ...,
            "low": ...,
            "close": ...,
            "volume": ...
        }
        """
        raise NotImplementedError

    def get_klines(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        """
        Alias استاندارد برای get_ohlcv.

        این متد برای سازگاری با نسخه‌های مختلف پروژه
        نگه داشته شده است.
        """
        return self.get_ohlcv(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )

    # =====================================================
    # SERVER
    # =====================================================

    @abstractmethod
    def get_server_time(self) -> int:
        """زمان سرور بر حسب milliseconds."""
        raise NotImplementedError

    @abstractmethod
    def ping(self) -> bool:
        """بررسی اتصال به صرافی."""
        raise NotImplementedError

    # =====================================================
    # OPTIONAL ACCOUNT METHODS
    # =====================================================

    def get_balance(self) -> Optional[Dict[str, Any]]:
        """
        موجودی حساب.

        Provider هایی که هنوز قابلیت حساب ندارند
        می‌توانند این متد را override کنند.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} "
            "does not support get_balance()"
        )

    def get_positions(self) -> List[Dict[str, Any]]:
        """لیست پوزیشن‌های باز."""
        raise NotImplementedError(
            f"{self.__class__.__name__} "
            "does not support get_positions()"
        )

    def get_open_orders(
        self,
        symbol: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """لیست سفارش‌های باز."""
        raise NotImplementedError(
            f"{self.__class__.__name__} "
            "does not support get_open_orders()"
        )

    def cancel_order(
        self,
        order_id: Any,
        symbol: Optional[str] = None,
    ) -> Dict[str, Any]:
        """لغو سفارش."""
        raise NotImplementedError(
            f"{self.__class__.__name__} "
            "does not support cancel_order()"
        )

    def place_order(self, **kwargs) -> Dict[str, Any]:
        """ثبت سفارش."""
        raise NotImplementedError(
            f"{self.__class__.__name__} "
            "does not support place_order()"
        )

    # =====================================================
    # OPTIONAL INFORMATION
    # =====================================================

    def info(self) -> Dict[str, Any]:
        """اطلاعات Provider."""
        return {
            "name": self.__class__.__name__,
        }

    def close(self) -> None:
        """بستن منابع Provider."""
        return None