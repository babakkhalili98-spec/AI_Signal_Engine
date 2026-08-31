"""
مدل سیگنال معاملاتی با چرخه حیات کامل.
این مدل تمام اطلاعات لازم برای ردیابی سیگنال از تولید تا بسته‌شدن را ذخیره می‌کند.
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
import uuid


class SignalStatus(Enum):
    """وضعیت‌های مختلف چرخه حیات سیگنال"""
    NEW = "new"
    ACTIVE = "active"
    TP1_HIT = "tp1_hit"
    TP2_HIT = "tp2_hit"
    TP3_HIT = "tp3_hit"
    SL_HIT = "sl_hit"
    INVALIDATED = "invalidated"
    CLOSED = "closed"


class SignalDirection(Enum):
    """جهت سیگنال"""
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


@dataclass
class Signal:
    """
    نماینده یک سیگنال معاملاتی کامل با تمام متادیتا.
    
    Attributes:
        signal_id: شناسه یکتای سیگنال (UUID)
        instrument_id: شناسه یکتای دارایی (مثلاً CRYPTO:NOBITEX:BTCUSDT)
        asset_class: کلاس دارایی (CRYPTO, FOREX, STOCK, etc.)
        market_region: منطقه بازار (USA, EUROPE, etc.)
        symbol: نماد معاملاتی
        timeframe: تایم‌فریم تحلیل
        direction: جهت سیگنال (LONG/SHORT)
        entry_price: قیمت ورود پیشنهادی
        sl_price: قیمت حد ضرر
        tp1_price: قیمت هدف اول
        tp2_price: قیمت هدف دوم
        tp3_price: قیمت هدف سوم
        score: امتیاز سیگنال (0-100)
        reliability_score: امتیاز قابلیت اطمینان (اختیاری - برای آینده)
        indicators_used: لیست اندیکاتورهای استفاده‌شده
        tools_used: لیست ابزارهای تحلیل استفاده‌شده
        smart_money_snapshot: اسنپ‌شات داده‌های Smart Money در زمان تولید
        news_warning: هشدار خبری مرتبط (در صورت وجود)
        status: وضعیت فعلی سیگنال
        created_at: زمان ایجاد سیگنال
        updated_at: زمان آخرین به‌روزرسانی
        closed_at: زمان بسته‌شدن سیگنال
        close_reason: دلیل بسته‌شدن
        result: نتیجه نهایی (Profit/Loss/Neutral)
    """
    
    # اطلاعات هویتی
    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    instrument_id: str = ""
    asset_class: str = ""
    market_region: str = ""
    symbol: str = ""
    timeframe: str = ""
    
    # اطلاعات معاملاتی
    direction: SignalDirection = SignalDirection.NEUTRAL
    entry_price: float = 0.0
    sl_price: float = 0.0
    tp1_price: float = 0.0
    tp2_price: float = 0.0
    tp3_price: float = 0.0
    
    # امتیازات و تحلیل
    score: float = 0.0
    reliability_score: Optional[float] = None
    
    # اجزای تشکیل‌دهنده سیگنال
    indicators_used: List[str] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    smart_money_snapshot: Optional[Dict[str, Any]] = None
    news_warning: Optional[str] = None
    
    # چرخه حیات
    status: SignalStatus = SignalStatus.NEW
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None
    close_reason: Optional[str] = None
    result: Optional[str] = None  # e.g., "TP1", "SL", "PROFIT", "LOSS"
    
    # متادیتای اضافی
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.direction, str):
            self.direction = SignalDirection(self.direction)
        if isinstance(self.status, str):
            self.status = SignalStatus(self.status)
    
    def update_status(self, new_status: SignalStatus, reason: Optional[str] = None):
        """به‌روزرسانی وضعیت سیگنال"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status in [SignalStatus.CLOSED, SignalStatus.INVALIDATED]:
            self.closed_at = self.updated_at
            if reason:
                self.close_reason = reason
    
    def is_active(self) -> bool:
        """بررسی فعال بودن سیگنال"""
        return self.status in [SignalStatus.NEW, SignalStatus.ACTIVE]
    
    def is_closed(self) -> bool:
        """بررسی بسته‌شدن سیگنال"""
        return self.status in [
            SignalStatus.TP1_HIT, 
            SignalStatus.TP2_HIT, 
            SignalStatus.TP3_HIT,
            SignalStatus.SL_HIT,
            SignalStatus.CLOSED,
            SignalStatus.INVALIDATED
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل سیگنال به دیکشنری برای ذخیره‌سازی"""
        return {
            "signal_id": self.signal_id,
            "instrument_id": self.instrument_id,
            "asset_class": self.asset_class,
            "market_region": self.market_region,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "direction": self.direction.value,
            "entry_price": self.entry_price,
            "sl_price": self.sl_price,
            "tp1_price": self.tp1_price,
            "tp2_price": self.tp2_price,
            "tp3_price": self.tp3_price,
            "score": self.score,
            "reliability_score": self.reliability_score,
            "indicators_used": self.indicators_used,
            "tools_used": self.tools_used,
            "smart_money_snapshot": self.smart_money_snapshot,
            "news_warning": self.news_warning,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "close_reason": self.close_reason,
            "result": self.result,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Signal":
        """ایجاد سیگنال از دیکشنری"""
        return cls(**data)
