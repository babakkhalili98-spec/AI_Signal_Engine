"""
=========================================================
AI SIGNAL ENGINE
ENGINE INTERFACES
Version : 1.0
=========================================================

تعریف قراردادهای مشترک بین تمام Engineها.
این ماژول Interfaceها و مدل‌های داده مشترک را تعریف می‌کند
تا تمام Engineها بتوانند بدون وابستگی مستقیم با هم کار کنند.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


# ==========================================================
# MARKET DATA TYPES
# ==========================================================

@dataclass
class MarketDataBundle:
    """
    بسته کامل داده بازار برای یک Symbol و Timeframe مشخص.
    
    این کلاس توسط Market Data Engine تولید می‌شود
    و به Indicator Engine و Pattern Engine ارسال می‌گردد.
    """
    instrument_id: str
    symbol: str
    asset_class: str
    market_region: str
    timeframe: str
    timestamp: datetime
    
    # داده‌های اصلی
    candles: List[Any] = field(default_factory=list)  # List[Candle]
    current_price: float = 0.0
    volume_24h: float = 0.0
    
    # متادیتا
    provider_name: str = ""
    received_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "instrument_id": self.instrument_id,
            "symbol": self.symbol,
            "asset_class": self.asset_class,
            "market_region": self.market_region,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp.isoformat(),
            "candles_count": len(self.candles),
            "current_price": self.current_price,
            "volume_24h": self.volume_24h,
            "provider_name": self.provider_name,
            "received_at": self.received_at.isoformat()
        }


# ==========================================================
# INDICATOR RESULT TYPES
# ==========================================================

class IndicatorName(Enum):
    """نام تمام Indicatorهای پشتیبانی‌شده"""
    RSI = "rsi"
    MACD = "macd"
    ICHIMOKU = "ichimoku"
    AO = "ao"
    PIVOT = "pivot"
    FIBONACCI = "fibonacci"
    MA = "ma"
    EMA = "ema"
    VOLUME = "volume"
    ATR = "atr"
    STOCHASTIC = "stochastic"
    ADX = "adx"
    BOLLINGER_BANDS = "bollinger_bands"
    CCI = "cci"
    WILLIAMS_R = "williams_r"
    OBV = "obv"
    VWAP = "vwap"


@dataclass
class IndicatorResult:
    """
    نتیجه محاسبه یک Indicator.
    
    این کلاس توسط Indicator Engine تولید می‌شود
    و به Scanner Engine ارسال می‌گردد.
    """
    indicator_name: IndicatorName
    instrument_id: str
    timeframe: str
    timestamp: datetime
    
    # مقادیر اصلی
    values: Dict[str, float] = field(default_factory=dict)
    
    # سیگنال‌های تحلیلی (نه سیگنال معاملاتی)
    is_overbought: bool = False
    is_oversold: bool = False
    has_divergence: bool = False
    has_hidden_divergence: bool = False
    trend_direction: str = ""  # "BULLISH", "BEARISH", "NEUTRAL"
    
    # پارامترهای استفاده‌شده
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # متادیتا
    confidence: float = 0.0
    provider_name: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "indicator_name": self.indicator_name.value,
            "instrument_id": self.instrument_id,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp.isoformat(),
            "values": self.values,
            "is_overbought": self.is_overbought,
            "is_oversold": self.is_oversold,
            "has_divergence": self.has_divergence,
            "has_hidden_divergence": self.has_hidden_divergence,
            "trend_direction": self.trend_direction,
            "parameters": self.parameters,
            "confidence": self.confidence,
            "provider_name": self.provider_name
        }


# ==========================================================
# PATTERN RESULT TYPES
# ==========================================================

class PatternCategory(Enum):
    """دسته‌بندی الگوها"""
    CANDLESTICK = "candlestick"
    CLASSIC = "classic"
    HARMONIC = "harmonic"
    SUPPORT_RESISTANCE = "support_resistance"
    BREAKOUT = "breakout"
    PULLBACK = "pullback"
    FALSE_BREAKOUT = "false_breakout"
    TREND_STRUCTURE = "trend_structure"


@dataclass
class PatternResult:
    """
    نتیجه شناسایی یک Pattern.
    
    این کلاس توسط Pattern Engine تولید می‌شود
    و به Scanner Engine ارسال می‌گردد.
    """
    pattern_name: str
    category: PatternCategory
    instrument_id: str
    timeframe: str
    timestamp: datetime
    
    # جهت الگو
    direction: str = ""  # "BULLISH", "BEARISH", "NEUTRAL"
    
    # نقاط کلیدی
    price_level: float = 0.0
    confidence: float = 0.0
    
    # شواهد
    evidence: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # متادیتا
    provider_name: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_name": self.pattern_name,
            "category": self.category.value,
            "instrument_id": self.instrument_id,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp.isoformat(),
            "direction": self.direction,
            "price_level": self.price_level,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "context": self.context,
            "provider_name": self.provider_name
        }


# ==========================================================
# MARKET CONTEXT TYPES
# ==========================================================

@dataclass
class DominanceContext:
    """
    زمینه قدرت بازار (Dominance/Market Strength).
    
    این کلاس توسط Dominance Engine تولید می‌شود.
    """
    asset_class: str
    market_region: str
    timestamp: datetime
    
    strength_score: float = 0.0  # 0-100
    direction: str = ""  # "BULLISH", "BEARISH", "NEUTRAL"
    trend: str = ""  # "UPTREND", "DOWNTREND", "SIDEWAYS"
    volatility: str = ""  # "HIGH", "MEDIUM", "LOW"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_class": self.asset_class,
            "market_region": self.market_region,
            "timestamp": self.timestamp.isoformat(),
            "strength_score": self.strength_score,
            "direction": self.direction,
            "trend": self.trend,
            "volatility": self.volatility
        }


@dataclass
class NewsContext:
    """
    زمینه خبری بازار.
    
    این کلاس توسط News Engine تولید می‌شود.
    """
    event_name: str
    impact: str  # "HIGH", "MEDIUM", "LOW"
    event_time: Optional[datetime]
    time_until_event: Optional[str]
    affected_symbols: List[str] = field(default_factory=list)
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_name": self.event_name,
            "impact": self.impact,
            "event_time": self.event_time.isoformat() if self.event_time else None,
            "time_until_event": self.time_until_event,
            "affected_symbols": self.affected_symbols,
            "description": self.description
        }


@dataclass
class SmartMoneyContext:
    """
    زمینه جریان سرمایه هوشمند.
    
    این کلاس توسط Smart Money Engine تولید می‌شود.
    """
    instrument_id: str
    timestamp: datetime
    
    inflow: float = 0.0
    outflow: float = 0.0
    net_flow: float = 0.0
    flow_direction: str = ""  # "INFLOW", "OUTFLOW", "NEUTRAL"
    flow_strength: float = 0.0  # 0-100
    accumulation_distribution: str = ""  # "ACCUMULATION", "DISTRIBUTION", "NEUTRAL"
    
    # داده‌های اختیاری
    order_book_imbalance: Optional[float] = None
    open_interest: Optional[float] = None
    funding_rate: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "instrument_id": self.instrument_id,
            "timestamp": self.timestamp.isoformat(),
            "inflow": self.inflow,
            "outflow": self.outflow,
            "net_flow": self.net_flow,
            "flow_direction": self.flow_direction,
            "flow_strength": self.flow_strength,
            "accumulation_distribution": self.accumulation_distribution,
            "order_book_imbalance": self.order_book_imbalance,
            "open_interest": self.open_interest,
            "funding_rate": self.funding_rate
        }


# ==========================================================
# ANALYSIS BUNDLE
# ==========================================================

@dataclass
class AnalysisBundle:
    """
    بسته کامل تحلیل برای یک Symbol و Timeframe.
    
    این کلاس توسط Scanner Engine جمع‌آوری می‌شود
    و به Score Engine ارسال می‌گردد.
    """
    instrument_id: str
    symbol: str
    asset_class: str
    market_region: str
    timeframe: str
    timestamp: datetime
    
    # داده‌های بازار
    market_data: Optional[MarketDataBundle] = None
    
    # نتایج Indicatorها
    indicator_results: List[IndicatorResult] = field(default_factory=list)
    
    # نتایج Patternها
    pattern_results: List[PatternResult] = field(default_factory=list)
    
    # زمینه بازار
    dominance_context: Optional[DominanceContext] = None
    news_context: Optional[NewsContext] = None
    smart_money_context: Optional[SmartMoneyContext] = None
    
    # متادیتا
    scan_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "instrument_id": self.instrument_id,
            "symbol": self.symbol,
            "asset_class": self.asset_class,
            "market_region": self.market_region,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp.isoformat(),
            "market_data": self.market_data.to_dict() if self.market_data else None,
            "indicator_results": [r.to_dict() for r in self.indicator_results],
            "pattern_results": [r.to_dict() for r in self.pattern_results],
            "dominance_context": self.dominance_context.to_dict() if self.dominance_context else None,
            "news_context": self.news_context.to_dict() if self.news_context else None,
            "smart_money_context": self.smart_money_context.to_dict() if self.smart_money_context else None,
            "scan_timestamp": self.scan_timestamp.isoformat()
        }


# ==========================================================
# SCORE INPUT/OUTPUT
# ==========================================================

@dataclass
class ScoreInput:
    """
    ورودی Score Engine.
    
    این کلاس از AnalysisBundle ساخته می‌شود.
    """
    analysis_bundle: AnalysisBundle
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "analysis_bundle": self.analysis_bundle.to_dict()
        }


@dataclass
class ScoreOutput:
    """
    خروجی Score Engine.
    
    این کلاس به Signal Engine ارسال می‌شود.
    """
    instrument_id: str
    symbol: str
    asset_class: str
    market_region: str
    timeframe: str
    timestamp: datetime
    
    raw_score: float = 0.0
    adjusted_score: float = 0.0
    confidence: float = 0.0
    
    reasons: List[Dict[str, Any]] = field(default_factory=list)
    modules: Dict[str, float] = field(default_factory=dict)
    
    signal_generated: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "instrument_id": self.instrument_id,
            "symbol": self.symbol,
            "asset_class": self.asset_class,
            "market_region": self.market_region,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp.isoformat(),
            "raw_score": round(self.raw_score, 2),
            "adjusted_score": round(self.adjusted_score, 2),
            "confidence": round(self.confidence, 2),
            "reasons": self.reasons,
            "modules": self.modules,
            "signal_generated": self.signal_generated
        }


# ==========================================================
# SIGNAL INPUT/OUTPUT
# ==========================================================

@dataclass
class SignalInput:
    """
    ورودی Signal Engine.
    
    این کلاس از ScoreOutput ساخته می‌شود.
    """
    score_output: ScoreOutput
    entry_price: float = 0.0
    sl_price: float = 0.0
    tp1_price: float = 0.0
    tp2_price: float = 0.0
    tp3_price: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "score_output": self.score_output.to_dict(),
            "entry_price": self.entry_price,
            "sl_price": self.sl_price,
            "tp1_price": self.tp1_price,
            "tp2_price": self.tp2_price,
            "tp3_price": self.tp3_price
        }


@dataclass
class SignalOutput:
    """
    خروجی Signal Engine.
    
    این کلاس نهایی‌ترین سیگنال است که به Database و Message Dispatcher ارسال می‌شود.
    """
    signal_id: str
    instrument_id: str
    symbol: str
    asset_class: str
    market_region: str
    timeframe: str
    timestamp: datetime
    
    direction: str  # "LONG", "SHORT"
    entry_price: float
    sl_price: float
    tp1_price: float
    tp2_price: float
    tp3_price: float
    
    score: float
    confidence: float
    
    indicators_used: List[str] = field(default_factory=list)
    patterns_used: List[str] = field(default_factory=list)
    reasons: List[Dict[str, Any]] = field(default_factory=list)
    
    news_warning: Optional[str] = None
    dominance_context: Optional[Dict[str, Any]] = None
    smart_money_context: Optional[Dict[str, Any]] = None
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "instrument_id": self.instrument_id,
            "symbol": self.symbol,
            "asset_class": self.asset_class,
            "market_region": self.market_region,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp.isoformat(),
            "direction": self.direction,
            "entry_price": self.entry_price,
            "sl_price": self.sl_price,
            "tp1_price": self.tp1_price,
            "tp2_price": self.tp2_price,
            "tp3_price": self.tp3_price,
            "score": round(self.score, 2),
            "confidence": round(self.confidence, 2),
            "indicators_used": self.indicators_used,
            "patterns_used": self.patterns_used,
            "reasons": self.reasons,
            "news_warning": self.news_warning,
            "dominance_context": self.dominance_context,
            "smart_money_context": self.smart_money_context,
            "created_at": self.created_at.isoformat()
        }
