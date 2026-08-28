"""
مدل‌های مربوط به گزارش‌های بازار و انواع خروجی‌ها.
این ماژول انواع مختلف گزارش‌ها را از سیگنال‌های معاملاتی تفکیک می‌کند.
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


class ReportType(Enum):
    """انواع مختلف گزارش‌ها و خروجی‌های سیستم"""
    SIGNAL = "signal"
    MARKET_DOMINANCE_REPORT = "market_dominance_report"
    LONDON_OPENING_REPORT = "london_opening_report"
    NEWS_WARNING = "news_warning"
    PERFORMANCE_REPORT = "performance_report"
    R_AND_D_REPORT = "r_and_d_report"
    SMART_MONEY_REPORT = "smart_money_report"


class FlowDirection(Enum):
    """جهت جریان سرمایه در Smart Money"""
    INFLOW = "inflow"
    OUTFLOW = "outflow"
    NEUTRAL = "neutral"
    ACCUMULATION = "accumulation"
    DISTRIBUTION = "distribution"


@dataclass
class MarketDominanceReport:
    """
    گزارش قدرت و تسلط بازار (Market Dominance / Market Strength).
    
    این گزارش سیگنال معاملاتی نیست، بلکه وضعیت کلی بازار را نشان می‌دهد.
    """
    report_id: str = field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    report_type: ReportType = ReportType.MARKET_DOMINANCE_REPORT
    asset_class: str = ""  # e.g., "CRYPTO", "FOREX", "STOCK"
    market_region: str = ""  # e.g., "USA", "EUROPE"
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # داده‌های گزارش
    dominance_value: Optional[float] = None  # درصد تسلط (در صورت کاربرد)
    strength_score: Optional[float] = None  # امتیاز قدرت بازار (0-100)
    direction: str = ""  # e.g., "BULLISH", "BEARISH", "NEUTRAL"
    trend: str = ""  # e.g., "UPTREND", "DOWNTREND", "SIDEWAYS"
    volatility: str = ""  # e.g., "HIGH", "MEDIUM", "LOW"
    volume_trend: str = ""  # e.g., "INCREASING", "DECREASING"
    
    # متادیتا
    data_source: str = ""  # نام Provider داده
    confidence: float = 0.0  # ضریب اطمینان گزارش (0-1)
    notes: Optional[str] = None  # توضیحات اضافی
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type.value,
            "asset_class": self.asset_class,
            "market_region": self.market_region,
            "timestamp": self.timestamp.isoformat(),
            "dominance_value": self.dominance_value,
            "strength_score": self.strength_score,
            "direction": self.direction,
            "trend": self.trend,
            "volatility": self.volatility,
            "volume_trend": self.volume_trend,
            "data_source": self.data_source,
            "confidence": self.confidence,
            "notes": self.notes
        }


@dataclass
class LondonOpeningReport:
    """
    گزارش بازگشایی بازار لندن.
    
    این گزارش روزانه تولید می‌شود و جفت‌ارزهای مناسب برای بررسی را پیشنهاد می‌دهد.
    این گزارش سیگنال معاملاتی نیست.
    """
    report_id: str = field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    report_type: ReportType = ReportType.LONDON_OPENING_REPORT
    date: datetime = field(default_factory=datetime.utcnow)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # لیست جفت‌ارزهای پیشنهادی برای بررسی
    top_pairs: List[Dict[str, Any]] = field(default_factory=list)
    # مثال: [{"pair": "EURUSD", "rank": 1, "volatility": "HIGH", "momentum": "BULLISH"}]
    
    # تحلیل کلی بازار
    market_context: str = ""
    overall_volatility: str = ""  # HIGH, MEDIUM, LOW
    key_levels: List[str] = field(default_factory=list)
    news_risk: str = ""  # HIGH, MEDIUM, LOW
    
    # متادیتا
    data_source: str = ""
    disclaimer: str = "این گزارش فقط نظر/تحلیل بازار است و SIGNAL معاملاتی نیست."
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type.value,
            "date": self.date.isoformat(),
            "timestamp": self.timestamp.isoformat(),
            "top_pairs": self.top_pairs,
            "market_context": self.market_context,
            "overall_volatility": self.overall_volatility,
            "key_levels": self.key_levels,
            "news_risk": self.news_risk,
            "data_source": self.data_source,
            "disclaimer": self.disclaimer
        }


@dataclass
class NewsWarning:
    """
    هشدار خبری برای رویدادهای مهم اقتصادی نزدیک به زمان سیگنال.
    
    این هشدار به تنهایی یک خروجی مستقل است و باید در بالای سیگنال نمایش داده شود.
    """
    warning_id: str = field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    event_name: str = ""  # e.g., "FOMC", "CPI", "NFP"
    impact: str = ""  # HIGH, MEDIUM, LOW
    event_time: Optional[datetime] = None
    time_until_event: Optional[str] = None  # e.g., "2 hours", "30 minutes"
    description: Optional[str] = None
    source: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "warning_id": self.warning_id,
            "event_name": self.event_name,
            "impact": self.impact,
            "event_time": self.event_time.isoformat() if self.event_time else None,
            "time_until_event": self.time_until_event,
            "description": self.description,
            "source": self.source,
            "timestamp": self.timestamp.isoformat()
        }
    
    def format_warning(self) -> str:
        """فرمت‌دهی هشدار برای نمایش"""
        warning = f"⚠️ NEWS WARNING\n"
        warning += f"Event: {self.event_name}\n"
        warning += f"Impact: {self.impact}\n"
        if self.time_until_event:
            warning += f"Time Until Event: {self.time_until_event}\n"
        if self.description:
            warning += f"{self.description}\n"
        return warning


@dataclass
class SmartMoneyReport:
    """
    گزارش جریان سرمایه هوشمند (Smart Money / Money Flow).
    
    این گزارش ورود، خروج، انباشت و توزیع سرمایه را نشان می‌دهد.
    """
    report_id: str = field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    instrument_id: str = ""
    asset_class: str = ""
    symbol: str = ""
    timeframe: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # داده‌های جریان سرمایه
    inflow: Optional[float] = None
    outflow: Optional[float] = None
    net_flow: Optional[float] = None
    flow_direction: FlowDirection = FlowDirection.NEUTRAL
    flow_strength: float = 0.0  # 0-100
    accumulation_distribution: str = ""  # ACCUMULATION, DISTRIBUTION, NEUTRAL
    
    # داده‌های اختیاری (بسته به Provider)
    order_book_imbalance: Optional[float] = None
    open_interest: Optional[float] = None
    funding_rate: Optional[float] = None
    large_trades_count: Optional[int] = None
    
    # متادیتا
    confidence: float = 0.0  # ضریب اطمینان (0-1)
    data_source: str = ""
    
    def __post_init__(self):
        if isinstance(self.flow_direction, str):
            self.flow_direction = FlowDirection(self.flow_direction)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "instrument_id": self.instrument_id,
            "asset_class": self.asset_class,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp.isoformat(),
            "inflow": self.inflow,
            "outflow": self.outflow,
            "net_flow": self.net_flow,
            "flow_direction": self.flow_direction.value,
            "flow_strength": self.flow_strength,
            "accumulation_distribution": self.accumulation_distribution,
            "order_book_imbalance": self.order_book_imbalance,
            "open_interest": self.open_interest,
            "funding_rate": self.funding_rate,
            "large_trades_count": self.large_trades_count,
            "confidence": self.confidence,
            "data_source": self.data_source
        }


@dataclass
class PerformanceReport:
    """
    گزارش عملکرد سیگنال‌ها (Performance Analysis).
    
    این گزارش پس از تحلیل سیگنال‌های بسته‌شده تولید می‌شود.
    """
    report_id: str = field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    report_type: ReportType = ReportType.PERFORMANCE_REPORT
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    generated_at: datetime = field(default_factory=datetime.utcnow)
    
    # آمار کلی
    total_signals: int = 0
    profitable_signals: int = 0
    losing_signals: int = 0
    win_rate: float = 0.0
    
    # تحلیل بر اساس عوامل مختلف
    by_indicator: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    by_timeframe: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    by_asset_class: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    by_market: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    by_pattern: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # نتایج تفصیلی
    tp1_hits: int = 0
    tp2_hits: int = 0
    tp3_hits: int = 0
    sl_hits: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type.value,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "generated_at": self.generated_at.isoformat(),
            "total_signals": self.total_signals,
            "profitable_signals": self.profitable_signals,
            "losing_signals": self.losing_signals,
            "win_rate": self.win_rate,
            "by_indicator": self.by_indicator,
            "by_timeframe": self.by_timeframe,
            "by_asset_class": self.by_asset_class,
            "by_market": self.by_market,
            "by_pattern": self.by_pattern,
            "tp1_hits": self.tp1_hits,
            "tp2_hits": self.tp2_hits,
            "tp3_hits": self.tp3_hits,
            "sl_hits": self.sl_hits
        }


@dataclass
class RnDReport:
    """
    گزارش تحقیق و توسعه (Research & Development).
    
    این گزارش نتایج آزمایش‌ها، بک‌تست‌ها و تحقیقات را ثبت می‌کند.
    """
    report_id: str = field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    report_type: ReportType = ReportType.R_AND_D_REPORT
    title: str = ""
    description: str = ""
    methodology: str = ""
    findings: str = ""
    conclusion: str = ""
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    
    # داده‌های آزمایش
    test_data: Dict[str, Any] = field(default_factory=dict)
    backtest_results: Optional[Dict[str, Any]] = None
    
    # وضعیت تأیید
    approved_for_production: bool = False
    approval_date: Optional[datetime] = None
    approver: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type.value,
            "title": self.title,
            "description": self.description,
            "methodology": self.methodology,
            "findings": self.findings,
            "conclusion": self.conclusion,
            "recommendations": self.recommendations,
            "generated_at": self.generated_at.isoformat(),
            "test_data": self.test_data,
            "backtest_results": self.backtest_results,
            "approved_for_production": self.approved_for_production,
            "approval_date": self.approval_date.isoformat() if self.approval_date else None,
            "approver": self.approver
        }
