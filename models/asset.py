"""
مدل‌های مربوط به دارایی‌ها، کلاس‌های دارایی و مناطق بازار.
این ماژول ساختار استاندارد تمام دارایی‌های قابل معامله در پروژه را تعریف می‌کند.
"""

from enum import Enum
from abc import ABC
from typing import Optional, List
from datetime import time


class AssetClass(Enum):
    """دسته‌بندی اصلی دارایی‌ها"""
    CRYPTO = "crypto"
    FOREX = "forex"
    STOCK = "stock"
    INDEX = "index"
    COMMODITY = "commodity"


class MarketRegion(Enum):
    """مناطق جغرافیایی/اقتصادی بازارها"""
    GLOBAL = "global"
    USA = "usa"
    EUROPE = "europe"
    UK = "uk"
    JAPAN = "japan"
    ASIA = "asia"
    MIDDLE_EAST = "middle_east"
    OTHER = "other"


class TradingHours:
    """نمایش ساعات معاملات یک دارایی"""
    def __init__(self, start: time, end: time, timezone: str):
        self.start = start
        self.end = end
        self.timezone = timezone
    
    def is_open(self) -> bool:
        # منطق بررسی باز بودن بازار بر اساس زمان فعلی
        # فعلاً به صورت Placeholder باقی می‌ماند
        return True


class Instrument(ABC):
    """کلاس پایه برای تمام دارایی‌های قابل معامله"""
    
    def __init__(
        self,
        symbol: str,
        asset_class: AssetClass,
        region: MarketRegion,
        exchange: str,
        currency: str,
        timezone: str,
        tick_size: float,
        lot_size: float,
        price_precision: int,
        volume_precision: int = 0,
        trading_hours: Optional[TradingHours] = None,
        active: bool = True
    ):
        self.symbol = symbol
        self.asset_class = asset_class
        self.region = region
        self.exchange = exchange
        self.currency = currency
        self.timezone = timezone
        self.tick_size = tick_size
        self.lot_size = lot_size
        self.price_precision = price_precision
        self.volume_precision = volume_precision
        self.trading_hours = trading_hours
        self.active = active
    
    @property
    def instrument_id(self) -> str:
        """شناسه یکتای استاندارد دارایی"""
        return f"{self.asset_class.value}:{self.region.value}:{self.exchange}:{self.symbol}"
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.symbol} ({self.asset_class.value})>"


class CryptoAsset(Instrument):
    """نماینده دارایی‌های کریپتوکارنسی"""
    def __init__(self, blockchain: Optional[str] = None, **kwargs):
        super().__init__(asset_class=AssetClass.CRYPTO, **kwargs)
        self.blockchain = blockchain


class ForexPair(Instrument):
    """نماینده جفت‌ارزهای فارکس"""
    def __init__(
        self,
        base_currency: str,
        quote_currency: str,
        pip_value: float,
        **kwargs
    ):
        super().__init__(asset_class=AssetClass.FOREX, **kwargs)
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.pip_value = pip_value


class Stock(Instrument):
    """نماینده سهام شرکت‌ها"""
    def __init__(
        self,
        isin: Optional[str] = None,
        sector: Optional[str] = None,
        industry: Optional[str] = None,
        market_cap: Optional[float] = None,
        **kwargs
    ):
        super().__init__(asset_class=AssetClass.STOCK, **kwargs)
        self.isin = isin
        self.sector = sector
        self.industry = industry
        self.market_cap = market_cap


class Index(Instrument):
    """نماینده شاخص‌های بازار"""
    def __init__(
        self,
        components_count: Optional[int] = None,
        base_value: Optional[float] = None,
        calculation_method: Optional[str] = None,
        **kwargs
    ):
        super().__init__(asset_class=AssetClass.INDEX, **kwargs)
        self.components_count = components_count
        self.base_value = base_value
        self.calculation_method = calculation_method


class Commodity(Instrument):
    """نماینده کالاها (Commodities)"""
    def __init__(
        self,
        unit: str,  # e.g., "Ounce", "Barrel"
        grade: Optional[str] = None,
        **kwargs
    ):
        super().__init__(asset_class=AssetClass.COMMODITY, **kwargs)
        self.unit = unit
        self.grade = grade
