"""
=========================================================
 AI Signal Engine
 Signal Engine
 Version : 2.0.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import logging

from config.settings import *


# =========================================================
# SIGNAL MODEL
# =========================================================

@dataclass
class Signal:

    # -----------------------------------------------------
    # Basic
    # -----------------------------------------------------

    symbol: str

    timeframe: str

    direction: str

    # -----------------------------------------------------
    # Scores
    # -----------------------------------------------------

    score: float

    confidence: float

    # -----------------------------------------------------
    # Trading
    # -----------------------------------------------------

    entry: float

    sl: float

    tp1: float

    tp2: float

    tp3: float

    # -----------------------------------------------------
    # Reasons
    # -----------------------------------------------------

    reasons: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    tags: List[str] = field(default_factory=list)

    # -----------------------------------------------------
    # Engine Scores
    # -----------------------------------------------------

    engine_scores: Dict[str, float] = field(default_factory=dict)

    engine_reasons: Dict[str, str] = field(default_factory=dict)

    engine_confidence: Dict[str, float] = field(default_factory=dict)

    # -----------------------------------------------------
    # AI
    # -----------------------------------------------------

    ai_summary: str = ""

    ai_verdict: str = ""

    ai_reason: List[str] = field(default_factory=list)

    # -----------------------------------------------------
    # News
    # -----------------------------------------------------

    news_effect: str = ""

    news_score: float = 0

    news_description: str = ""

    # -----------------------------------------------------
    # Noise
    # -----------------------------------------------------

    noise_level: str = ""

    noise_score: float = 0

    # -----------------------------------------------------
    # Market DNA
    # -----------------------------------------------------

    market_dna: Dict[str, Any] = field(default_factory=dict)

    # -----------------------------------------------------
    # Metadata
    # -----------------------------------------------------

    report_id: str = ""

    created_at: str = ""


# =========================================================
# SIGNAL ENGINE
# =========================================================

class SignalEngine:

    """
    این کلاس فقط موتورهای تحلیل را مدیریت می‌کند.

    خودش هیچ اندیکاتوری را محاسبه نمی‌کند.

    تمام اندیکاتورها باید خروجی استاندارد برگردانند.
    """

    def __init__(

        self,

        pivot_engine=None,

        rsi_engine=None,

        ichimoku_engine=None,

        ao_engine=None,

        candlestick_engine=None,

        harmonic_engine=None,

        fibonacci_engine=None,

        smart_money_engine=None,

        market_dna_engine=None,

        news_engine=None,

        noise_engine=None,

        logger=None

    ):


        self.logger = logger or logging.getLogger("SignalEngine")

        self.pivot_engine = pivot_engine

        self.rsi_engine = rsi_engine

        self.ichimoku_engine = ichimoku_engine

        self.ao_engine = ao_engine

        self.candlestick_engine = candlestick_engine

        self.harmonic_engine = harmonic_engine

        self.fibonacci_engine = fibonacci_engine

        self.smart_money_engine = smart_money_engine

        self.market_dna_engine = market_dna_engine

        self.news_engine = news_engine

        self.noise_engine = noise_engine
    # -----------------------------------------------------
    # ANALYZE
    # -----------------------------------------------------

    def analyze(

        self,

        symbol: str,

        timeframe: str,

        candles

    ) -> Optional[Signal]:

        if candles is None:

            return None

        if len(candles) < 100:

            return None

        # =====================================================
        # Last Candle
        # =====================================================

        last = candles[-1]

        close = float(last["close"])

        high = float(last["high"])

        low = float(last["low"])

        # =====================================================
        # Result Containers
        # =====================================================

        total_score = 0.0

        total_confidence = 0.0

        direction = None

        reasons = []

        warnings = []

        tags = []

        engine_scores = {}

        engine_reasons = {}

        engine_confidence = {}

        news_effect = ""

        news_description = ""

        news_score = 0

        noise_level = ""

        noise_score = 0

        market_dna = {}

        ai_reason = []

        # =====================================================
        # Helper
        # =====================================================

        def collect(

            name,

            result

        ):

            nonlocal total_score

            nonlocal total_confidence

            nonlocal direction

            nonlocal news_effect

            nonlocal news_description

            nonlocal news_score

            nonlocal noise_level

            nonlocal noise_score

            nonlocal market_dna

            if result is None:

                return

            score = float(

                result.get(

                    "score",

                    0

                )

            )

            confidence = float(

                result.get(

                    "confidence",

                    0

                )

            )

            total_score += score

            total_confidence += confidence

            engine_scores[name] = score

            engine_reasons[name] = result.get(

                "reason",

                ""

            )

            engine_confidence[name] = confidence

            reason = result.get(

                "reason"

            )

            if reason:

                reasons.append(reason)

            warning = result.get(

                "warning"

            )

            if warning:

                warnings.append(warning)

            tag = result.get(

                "tag"

            )

            if tag:

                tags.append(tag)

            if direction is None:

                direction = result.get(

                    "direction"

                )

            if name == "NEWS":

                news_effect = result.get(

                    "effect",

                    ""

                )

                news_description = result.get(

                    "description",

                    ""

                )

                news_score = score

            if name == "NOISE":

                noise_level = result.get(

                    "level",

                    ""

                )

                noise_score = score

            if name == "MARKET_DNA":

                market_dna = result.get(

                    "dna",

                    {}
                )
        # =====================================================
        # Pivot Engine
        # =====================================================

        if self.pivot_engine:

            collect(

                "PIVOT",

                self.pivot_engine.analyze(

                    symbol,

                    timeframe,

                    candles

                )

            )

        # =====================================================
        # RSI Engine
        # =====================================================

        if self.rsi_engine:

            collect(

                "RSI",

                self.rsi_engine.analyze(

                    symbol,

                    timeframe,

                    candles

                )

            )

        # =====================================================
        # Ichimoku Engine
        # =====================================================

        if self.ichimoku_engine:

            collect(

                "ICHIMOKU",

                self.ichimoku_engine.analyze(

                    symbol,

                    timeframe,

                    candles

                )

            )

        # =====================================================
        # AO Engine
        # =====================================================

        if self.ao_engine:

            collect(

                "AO",

                self.ao_engine.analyze(

                    symbol,

                    timeframe,

                    candles

                )

            )

        # =====================================================
        # Candlestick Engine
        # =====================================================

        if self.candlestick_engine:

            collect(

                "CANDLE",

                self.candlestick_engine.analyze(

                    symbol,

                    timeframe,

                    candles

                )

            )

        # =====================================================
        # Harmonic Engine
        # =====================================================

        if self.harmonic_engine:

            collect(

                "HARMONIC",

                self.harmonic_engine.analyze(

                    symbol,

                    timeframe,

                    candles

                )

            )

        # =====================================================
        # Fibonacci Engine
        # =====================================================

        if self.fibonacci_engine:

            collect(

                "FIBONACCI",

                self.fibonacci_engine.analyze(

                    symbol,

                    timeframe,

                    candles

                )

            )

        # =====================================================
        # Smart Money Engine
        # =====================================================

        if self.smart_money_engine:

            collect(

                "SMART_MONEY",

                self.smart_money_engine.analyze(

                    symbol,

                    timeframe,

                    candles

                )

            )

        # =====================================================
        # Market DNA Engine
        # =====================================================

        if self.market_dna_engine:

            collect(

                "MARKET_DNA",

                self.market_dna_engine.analyze(

                    symbol,

                    timeframe,

                    candles

                )

            )

        # =====================================================
        # News Engine
        # =====================================================

        if self.news_engine:

            collect(

                "NEWS",

                self.news_engine.analyze(

                    symbol,

                    timeframe

                )

            )

        # =====================================================
        # Noise Engine
        # =====================================================

        if self.noise_engine:

            collect(

                "NOISE",

                self.noise_engine.analyze(

                    symbol,

                    timeframe,

                    candles

                )

            )
        # =====================================================
        # SCORE ENGINE
        # =====================================================

        weights = {

            "PIVOT": 1.30,

            "RSI": 1.20,

            "ICHIMOKU": 1.30,

            "CANDLE": 1.20,

            "AO": 1.00,

            "HARMONIC": 1.10,

            "FIBONACCI": 1.00,

            "SMART_MONEY": 1.25,

            "MARKET_DNA": 1.15,

            "NEWS": 1.00,

            "NOISE": 1.00

        }

        weighted_score = 0.0

        weighted_confidence = 0.0

        total_weight = 0.0

        for engine_name, score in engine_scores.items():

            weight = weights.get(

                engine_name,

                1.0

            )

            weighted_score += score * weight

            weighted_confidence += (

                engine_confidence.get(

                    engine_name,

                    0

                ) * weight

            )

            total_weight += weight

        if total_weight > 0:

            final_score = weighted_score / total_weight

            final_confidence = (

                weighted_confidence /

                total_weight

            )

        else:

            final_score = 0

            final_confidence = 0

        # =====================================================
        # AI SUMMARY
        # =====================================================

        ai_summary = (

            f"{direction} signal generated "

            f"with score "

            f"{final_score:.1f} "

            f"and confidence "

            f"{final_confidence:.1f}%."

        )

        # =====================================================
        # AI VERDICT
        # =====================================================

        if final_score >= 90:

            ai_verdict = "VERY STRONG"

            ai_reason.append(

                "Exceptional alignment between engines."

            )

        elif final_score >= 82:

            ai_verdict = "STRONG"

            ai_reason.append(

                "Most engines confirm the signal."

            )

        elif final_score >= MIN_SIGNAL_SCORE:

            ai_verdict = "VALID"

            ai_reason.append(

                "Signal meets minimum quality requirements."

            )

        else:

            ai_verdict = "REJECTED"

            ai_reason.append(

                "Signal quality below required threshold."

            )

        # =====================================================
        # VALIDATION
        # =====================================================

        if final_score < MIN_SIGNAL_SCORE:
            return None

        if final_confidence < AI_CONFIDENCE_LIMIT:
            return None

        if final_confidence < self.config.MIN_CONFIDENCE:

            return None

        if direction is None:

            return None

        # =====================================================
        # ENTRY / SL / TP
        # =====================================================

        entry = close

        if direction == "BUY":

            sl = low

        else:

            sl = high

        risk = abs(

            entry - sl

        )

        if risk <= 0:

            return None

        minimum_rr = max(
            MIN_RISK_REWARD,
            1.0
        )
        reward = risk * minimum_rr

        if direction == "BUY":

            tp1 = entry + reward

            tp2 = entry + reward * 2

            tp3 = entry + reward * 3

        else:

            tp1 = entry - reward

            tp2 = entry - reward * 2

            tp3 = entry - reward * 3

        rr = abs(tp1 - entry) / risk

        if rr < MIN_RISK_REWARD:
            return None

        # =====================================================
        # CREATE SIGNAL
        # =====================================================

        signal = Signal(

            symbol=symbol,

            timeframe=timeframe,

            direction=direction,

            score=round(final_score, 2),

            confidence=round(final_confidence, 2),

            entry=round(entry, 8),

            sl=round(sl, 8),

            tp1=round(tp1, 8),

            tp2=round(tp2, 8),

            tp3=round(tp3, 8),

            reasons=reasons,

            warnings=warnings,

            tags=tags,

            engine_scores=engine_scores,

            engine_reasons=engine_reasons,

            engine_confidence=engine_confidence,

            ai_summary=ai_summary,

            ai_verdict=ai_verdict,

            ai_reason=ai_reason,

            news_effect=news_effect,

            news_score=news_score,

            news_description=news_description,

            noise_level=noise_level,

            noise_score=noise_score,

            market_dna=market_dna

        )

        # =====================================================
        # LOG
        # =====================================================

        self.logger.info(

            f"{symbol} | "

            f"{direction} | "

            f"Score={signal.score:.2f} | "

            f"Confidence={signal.confidence:.2f}"

        )

        return signal