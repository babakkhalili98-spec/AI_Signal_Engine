"""
مدل‌های داده پایه برای کندل، تیکر و داده‌های بازار.
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass


@dataclass
class Candle:
    """نماینده یک کندل قیمتی استاندارد"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    instrument_id: str  # شناسه یکتای دارایی
    timeframe: str
    
    # فیلدهای اختیاری برای داده‌های پیشرفته‌تر
    buy_volume: Optional[float] = None
    sell_volume: Optional[float] = None
    trades_count: Optional[int] = None
    
    def __post_init__(self):
        if self.buy_volume is None:
            self.buy_volume = self.volume / 2
        if self.sell_volume is None:
            self.sell_volume = self.volume / 2
    
    @property
    def is_bullish(self) -> bool:
        return self.close > self.open
    
    @property
    def is_bearish(self) -> bool:
        return self.close < self.open


@dataclass
class Ticker:
    """نماینده اطلاعات قیمت لحظه‌ای"""
    instrument_id: str
    last_price: float
    bid: float
    ask: float
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    timestamp: Optional[datetime] = None
    
    @property
    def spread(self) -> float:
        return self.ask - self.bid
    
    @property
    def mid_price(self) -> float:
        return (self.bid + self.ask) / 2
