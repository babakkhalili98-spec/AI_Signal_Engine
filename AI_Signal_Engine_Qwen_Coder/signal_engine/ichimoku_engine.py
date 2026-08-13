"""
=========================================================
AI SIGNAL ENGINE
Ichimoku Engine
Version : 6.0 Enterprise
=========================================================

وظایف

• Trend Detection
• TK Cross
• Kumo Breakout
• Kumo Twist
• Future Cloud
• Chikou Confirmation

• Flat Tenkan
• Flat Kijun
• Flat Senkou A
• Flat Senkou B

• Dynamic Support
• Dynamic Resistance

• Ichimoku Levels
• Ichimoku Magnetism

• Fake Breakout Detection

• Multi TimeFrame Confirmation

• Signal Score

=========================================================
"""

from __future__ import annotations

import logging
import numpy as np

from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Dict

logger = logging.getLogger("IchimokuEngine")


# ==========================================================
# CONFIG
# ==========================================================

TENKAN_PERIOD = 9

KIJUN_PERIOD = 26

SENKOU_B_PERIOD = 52

CHIKOU_SHIFT = 26


# ==========================================================
# SIGNAL
# ==========================================================

@dataclass

class IchimokuSignal:

    trend: str = "NEUTRAL"

    score: float = 0

    confidence: float = 0

    strength: float = 0

    buy_score: float = 0

    sell_score: float = 0

    reasons: List[str] = None

    # ----------------------

    tenkan: float = 0

    kijun: float = 0

    senkou_a: float = 0

    senkou_b: float = 0

    chikou: float = 0

    # ----------------------

    tk_cross: str = "NONE"

    cloud_break: bool = False

    cloud_twist: bool = False

    future_cloud: str = "NONE"

    chikou_confirm: bool = False

    # ----------------------

    flat_tenkan: bool = False

    flat_kijun: bool = False

    flat_senkou_a: bool = False

    flat_senkou_b: bool = False

    # ----------------------

    support: float = 0

    resistance: float = 0

    # ----------------------

    ichimoku_levels = None

    magnet_level = None

    magnet_distance = 0

    magnet_strength = 0

    # ----------------------

    fake_breakout = False

    # ----------------------

    def __post_init__(self):

        if self.reasons is None:

            self.reasons = []


# ==========================================================
# ENGINE
# ==========================================================

class IchimokuEngine:

    """
    Enterprise Ichimoku Analyzer
    """

    VERSION = "6.0"

    def __init__(self):

        self.logger = logger

        self.last_signal: Optional[IchimokuSignal] = None

        self.initialized = True

        logger.info(

            "Ichimoku Engine Loaded"

        )

    # ======================================================

    def analyze(

        self,

        symbol: str,

        timeframe: str,

        candles: List[Dict],

    ) -> IchimokuSignal:

        """
        Main Analyze

        فقط وظیفه Orchestrator دارد

        هر بخش توسط ماژول جداگانه محاسبه خواهد شد.
        """

        signal = IchimokuSignal()

        signal.symbol = symbol

        signal.timeframe = timeframe

        return signal
# ==========================================================
# Calculate Lines
# ==========================================================

    def _highest(self, values):

        return float(np.max(values))

    # ------------------------------------------------------

    def _lowest(self, values):

        return float(np.min(values))

    # ------------------------------------------------------

    def _midpoint(

        self,

        highs,

        lows,

    ):

        return (

            self._highest(highs)

            +

            self._lowest(lows)

        ) / 2

    # ------------------------------------------------------
    # Tenkan
    # ------------------------------------------------------

    def calculate_tenkan(

        self,

        highs,

        lows,

    ):

        if len(highs) < TENKAN_PERIOD:

            return None

        return self._midpoint(

            highs[-TENKAN_PERIOD:],

            lows[-TENKAN_PERIOD:],

        )

    # ------------------------------------------------------
    # Kijun
    # ------------------------------------------------------

    def calculate_kijun(

        self,

        highs,

        lows,

    ):

        if len(highs) < KIJUN_PERIOD:

            return None

        return self._midpoint(

            highs[-KIJUN_PERIOD:],

            lows[-KIJUN_PERIOD:],

        )

    # ------------------------------------------------------
    # Senkou A
    # ------------------------------------------------------

    def calculate_senkou_a(

        self,

        tenkan,

        kijun,

    ):

        if tenkan is None:

            return None

        if kijun is None:

            return None

        return (

            tenkan

            +

            kijun

        ) / 2

    # ------------------------------------------------------
    # Senkou B
    # ------------------------------------------------------

    def calculate_senkou_b(

        self,

        highs,

        lows,

    ):

        if len(highs) < SENKOU_B_PERIOD:

            return None

        return self._midpoint(

            highs[-SENKOU_B_PERIOD:],

            lows[-SENKOU_B_PERIOD:],

        )

    # ------------------------------------------------------
    # Chikou
    # ------------------------------------------------------

    def calculate_chikou(

        self,

        closes,

    ):

        if len(closes) <= CHIKOU_SHIFT:

            return None

        return closes[-CHIKOU_SHIFT]

    # ------------------------------------------------------
    # Main
    # ------------------------------------------------------

    def calculate_lines(

        self,

        candles,

    ):

        highs = np.array(

            [c["high"] for c in candles],

            dtype=float,

        )

        lows = np.array(

            [c["low"] for c in candles],

            dtype=float,

        )

        closes = np.array(

            [c["close"] for c in candles],

            dtype=float,

        )

        tenkan = self.calculate_tenkan(

            highs,

            lows,

        )

        kijun = self.calculate_kijun(

            highs,

            lows,

        )

        senkou_a = self.calculate_senkou_a(

            tenkan,

            kijun,

        )

        senkou_b = self.calculate_senkou_b(

            highs,

            lows,

        )

        chikou = self.calculate_chikou(

            closes,

        )

        return {

            "tenkan": tenkan,

            "kijun": kijun,

            "senkou_a": senkou_a,

            "senkou_b": senkou_b,

            "chikou": chikou,

            "last_price": closes[-1],

        }
# ==========================================================
# Flat Line Detection
# Ichimoku Levels
# ==========================================================

FLAT_LOOKBACK = 8
FLAT_TOLERANCE = 0.000001


# ----------------------------------------------------------
# Generic Flat Detector
# ----------------------------------------------------------

def _is_flat(
    self,
    values,
    lookback=FLAT_LOOKBACK,
):

    if values is None:
        return False

    if len(values) < lookback:
        return False

    recent = values[-lookback:]

    high = max(recent)
    low = min(recent)

    return abs(high - low) <= FLAT_TOLERANCE


# ----------------------------------------------------------
# Flat Tenkan
# ----------------------------------------------------------

def detect_flat_tenkan(
    self,
    tenkan_history,
):

    return self._is_flat(
        tenkan_history
    )


# ----------------------------------------------------------
# Flat Kijun
# ----------------------------------------------------------

def detect_flat_kijun(
    self,
    kijun_history,
):

    return self._is_flat(
        kijun_history
    )


# ----------------------------------------------------------
# Flat Senkou A
# ----------------------------------------------------------

def detect_flat_senkou_a(
    self,
    senkou_a_history,
):

    return self._is_flat(
        senkou_a_history
    )


# ----------------------------------------------------------
# Flat Senkou B
# ----------------------------------------------------------

def detect_flat_senkou_b(
    self,
    senkou_b_history,
):

    return self._is_flat(
        senkou_b_history
    )


# ==========================================================
# Ichimoku Levels
# ==========================================================

def calculate_levels(
    self,
    signal,
):

    levels = []

    if signal.tenkan is not None:

        levels.append({

            "name": "TENKAN",

            "price": signal.tenkan,

            "weight": 1,

        })

    if signal.kijun is not None:

        levels.append({

            "name": "KIJUN",

            "price": signal.kijun,

            "weight": 3,

        })

    if signal.senkou_a is not None:

        levels.append({

            "name": "SENKOU_A",

            "price": signal.senkou_a,

            "weight": 2,

        })

    if signal.senkou_b is not None:

        levels.append({

            "name": "SENKOU_B",

            "price": signal.senkou_b,

            "weight": 4,

        })

    levels = sorted(

        levels,

        key=lambda x: x["price"]

    )

    return levels


# ==========================================================
# Dynamic Support
# ==========================================================

def calculate_support(
    self,
    last_price,
    levels,
):

    support = None

    for level in levels:

        if level["price"] <= last_price:

            support = level["price"]

    return support


# ==========================================================
# Dynamic Resistance
# ==========================================================

def calculate_resistance(
    self,
    last_price,
    levels,
):

    for level in levels:

        if level["price"] > last_price:

            return level["price"]

    return None


# ==========================================================
# Apply
# ==========================================================

def update_levels(
    self,
    signal,
    tenkan_history,
    kijun_history,
    senkou_a_history,
    senkou_b_history,
):

    signal.flat_tenkan = self.detect_flat_tenkan(
        tenkan_history
    )

    signal.flat_kijun = self.detect_flat_kijun(
        kijun_history
    )

    signal.flat_senkou_a = self.detect_flat_senkou_a(
        senkou_a_history
    )

    signal.flat_senkou_b = self.detect_flat_senkou_b(
        senkou_b_history
    )

    signal.ichimoku_levels = self.calculate_levels(
        signal
    )

    signal.support = self.calculate_support(

        signal.last_price,

        signal.ichimoku_levels,

    )

    signal.resistance = self.calculate_resistance(

        signal.last_price,

        signal.ichimoku_levels,

    )

    return signal
# ==========================================================
# Ichimoku Magnetism Engine
# Version : 1.0 Enterprise
# ==========================================================

MAGNET_MAX_DISTANCE = 0.015      # 1.5 درصد
MAGNET_STRONG = 85
MAGNET_MEDIUM = 60
MAGNET_WEAK = 35


# ----------------------------------------------------------
# Distance %
# ----------------------------------------------------------

def _distance_percent(
    self,
    price,
    level,
):

    if level == 0:
        return 999

    return abs(price - level) / level


# ----------------------------------------------------------
# Find Nearest Level
# ----------------------------------------------------------

def find_nearest_level(
    self,
    price,
    levels,
):

    if not levels:

        return None

    best = None

    best_distance = 999

    for level in levels:

        d = self._distance_percent(

            price,

            level["price"]

        )

        if d < best_distance:

            best_distance = d

            best = level

    return best


# ----------------------------------------------------------
# Magnet Strength
# ----------------------------------------------------------

def calculate_magnet_strength(
    self,
    distance,
    weight,
):

    if distance > MAGNET_MAX_DISTANCE:

        return 0

    score = (

        (1 - (distance / MAGNET_MAX_DISTANCE))

        * 100

    )

    score *= weight / 4

    score = min(score,100)

    return round(score,2)


# ----------------------------------------------------------
# Magnet State
# ----------------------------------------------------------

def magnet_state(
    self,
    score,
):

    if score >= MAGNET_STRONG:

        return "VERY_STRONG"

    if score >= MAGNET_MEDIUM:

        return "STRONG"

    if score >= MAGNET_WEAK:

        return "MEDIUM"

    if score > 0:

        return "WEAK"

    return "NONE"


# ----------------------------------------------------------
# Price Position
# ----------------------------------------------------------

def price_position(
    self,
    price,
    level,
):

    if price > level:

        return "ABOVE"

    if price < level:

        return "BELOW"

    return "ON_LEVEL"


# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

def calculate_magnetism(
    self,
    signal,
):

    if signal.ichimoku_levels is None:

        return signal

    nearest = self.find_nearest_level(

        signal.last_price,

        signal.ichimoku_levels

    )

    if nearest is None:

        return signal

    distance = self._distance_percent(

        signal.last_price,

        nearest["price"]

    )

    strength = self.calculate_magnet_strength(

        distance,

        nearest["weight"]

    )

    signal.magnet_level = nearest["name"]

    signal.magnet_price = nearest["price"]

    signal.magnet_distance = round(

        distance * 100,

        3

    )

    signal.magnet_strength = strength

    signal.magnet_state = self.magnet_state(

        strength

    )

    signal.price_position = self.price_position(

        signal.last_price,

        nearest["price"]

    )

    return signal


# ----------------------------------------------------------
# Breakout Probability
# ----------------------------------------------------------

def breakout_probability(
    self,
    signal,
):

    if signal.magnet_strength >= 85:

        return 25

    if signal.magnet_strength >= 70:

        return 40

    if signal.magnet_strength >= 55:

        return 55

    if signal.magnet_strength >= 40:

        return 70

    return 90


# ----------------------------------------------------------
# Rejection Probability
# ----------------------------------------------------------

def rejection_probability(
    self,
    signal,
):

    return 100 - self.breakout_probability(
        signal
    )
# ==========================================================
# TK CROSS
# ==========================================================

def detect_tk_cross(
    self,
    signal,
):

    t = signal.tenkan
    k = signal.kijun

    if t is None or k is None:

        signal.tk_cross = "NONE"
        return signal

    if abs(t - k) < 1e-8:

        signal.tk_cross = "NONE"
        return signal

    if t > k:

        signal.tk_cross = "BULLISH"

    else:

        signal.tk_cross = "BEARISH"

    return signal


# ==========================================================
# KUMO BREAK
# ==========================================================

def detect_kumo_break(
    self,
    signal,
):

    if signal.senkou_a is None:

        return signal

    if signal.senkou_b is None:

        return signal

    upper = max(

        signal.senkou_a,

        signal.senkou_b,

    )

    lower = min(

        signal.senkou_a,

        signal.senkou_b,

    )

    price = signal.last_price

    if price > upper:

        signal.cloud_break = "BULLISH"

    elif price < lower:

        signal.cloud_break = "BEARISH"

    else:

        signal.cloud_break = "INSIDE"

    return signal


# ==========================================================
# CLOUD TWIST
# ==========================================================

def detect_cloud_twist(
    self,
    signal,
    senkou_a_history,
    senkou_b_history,
):

    if len(senkou_a_history) < 2:

        signal.cloud_twist = "NONE"
        return signal

    if len(senkou_b_history) < 2:

        signal.cloud_twist = "NONE"
        return signal

    prev_a = senkou_a_history[-2]
    prev_b = senkou_b_history[-2]

    now_a = senkou_a_history[-1]
    now_b = senkou_b_history[-1]

    if prev_a < prev_b and now_a > now_b:

        signal.cloud_twist = "BULLISH"

    elif prev_a > prev_b and now_a < now_b:

        signal.cloud_twist = "BEARISH"

    else:

        signal.cloud_twist = "NONE"

    return signal


# ==========================================================
# FUTURE CLOUD
# ==========================================================

def detect_future_cloud(
    self,
    signal,
):

    if signal.senkou_a is None:

        return signal

    if signal.senkou_b is None:

        return signal

    if signal.senkou_a > signal.senkou_b:

        signal.future_cloud = "BULLISH"

    elif signal.senkou_a < signal.senkou_b:

        signal.future_cloud = "BEARISH"

    else:

        signal.future_cloud = "NEUTRAL"

    return signal


# ==========================================================
# CHIKOU CONFIRMATION
# ==========================================================

def detect_chikou_confirmation(
    self,
    signal,
    closes,
):

    if signal.chikou is None:

        signal.chikou_confirm = False
        return signal

    if len(closes) <= CHIKOU_SHIFT:

        signal.chikou_confirm = False
        return signal

    compare_price = closes[-CHIKOU_SHIFT]

    if signal.tk_cross == "BULLISH":

        signal.chikou_confirm = (

            signal.chikou > compare_price

        )

    elif signal.tk_cross == "BEARISH":

        signal.chikou_confirm = (

            signal.chikou < compare_price

        )

    else:

        signal.chikou_confirm = False

    return signal


# ==========================================================
# APPLY SIGNALS
# ==========================================================

def update_signals(
    self,
    signal,
    closes,
    senkou_a_history,
    senkou_b_history,
):

    signal = self.detect_tk_cross(

        signal

    )

    signal = self.detect_kumo_break(

        signal

    )

    signal = self.detect_cloud_twist(

        signal,

        senkou_a_history,

        senkou_b_history,

    )

    signal = self.detect_future_cloud(

        signal

    )

    signal = self.detect_chikou_confirmation(

        signal,

        closes,

    )

    return signal
# ==========================================================
# ENTERPRISE SCORING ENGINE
# ==========================================================

TK_CROSS_WEIGHT = 18

KUMO_BREAK_WEIGHT = 20

CHIKOU_WEIGHT = 12

FUTURE_CLOUD_WEIGHT = 10

CLOUD_TWIST_WEIGHT = 8

MAGNET_WEIGHT = 12

SUP_RES_WEIGHT = 8

FLAT_WEIGHT = 6

TREND_WEIGHT = 20


# ==========================================================
# TREND
# ==========================================================

def calculate_trend_score(
    self,
    signal,
):

    score = 0

    if signal.last_price > signal.senkou_a:
        score += 10

    if signal.last_price > signal.senkou_b:
        score += 10

    return score


# ==========================================================
# TK CROSS
# ==========================================================

def score_tk_cross(
    self,
    signal,
):

    if signal.tk_cross == "BULLISH":

        return TK_CROSS_WEIGHT

    if signal.tk_cross == "BEARISH":

        return -TK_CROSS_WEIGHT

    return 0


# ==========================================================
# KUMO BREAK
# ==========================================================

def score_cloud_break(
    self,
    signal,
):

    if signal.cloud_break == "BULLISH":

        return KUMO_BREAK_WEIGHT

    if signal.cloud_break == "BEARISH":

        return -KUMO_BREAK_WEIGHT

    return 0


# ==========================================================
# FUTURE CLOUD
# ==========================================================

def score_future_cloud(
    self,
    signal,
):

    if signal.future_cloud == "BULLISH":

        return FUTURE_CLOUD_WEIGHT

    if signal.future_cloud == "BEARISH":

        return -FUTURE_CLOUD_WEIGHT

    return 0


# ==========================================================
# CLOUD TWIST
# ==========================================================

def score_cloud_twist(
    self,
    signal,
):

    if signal.cloud_twist == "BULLISH":

        return CLOUD_TWIST_WEIGHT

    if signal.cloud_twist == "BEARISH":

        return -CLOUD_TWIST_WEIGHT

    return 0


# ==========================================================
# CHIKOU
# ==========================================================

def score_chikou(
    self,
    signal,
):

    if signal.chikou_confirm:

        if signal.tk_cross == "BULLISH":

            return CHIKOU_WEIGHT

        if signal.tk_cross == "BEARISH":

            return -CHIKOU_WEIGHT

    return 0


# ==========================================================
# MAGNET
# ==========================================================

def score_magnet(
    self,
    signal,
):

    strength = signal.magnet_strength

    if strength == 0:

        return 0

    if signal.price_position == "BELOW":

        return strength * MAGNET_WEIGHT / 100

    if signal.price_position == "ABOVE":

        return -(strength * MAGNET_WEIGHT / 100)

    return 0


# ==========================================================
# SUPPORT RESISTANCE
# ==========================================================

def score_levels(
    self,
    signal,
):

    score = 0

    if signal.support:

        score += SUP_RES_WEIGHT / 2

    if signal.resistance:

        score += SUP_RES_WEIGHT / 2

    return score


# ==========================================================
# FLAT
# ==========================================================

def score_flat(
    self,
    signal,
):

    score = 0

    if signal.flat_kijun:

        score += FLAT_WEIGHT

    if signal.flat_senkou_b:

        score += FLAT_WEIGHT

    return score


# ==========================================================
# TOTAL
# ==========================================================

def calculate_total_score(
    self,
    signal,
):

    total = 0

    total += self.calculate_trend_score(signal)

    total += self.score_tk_cross(signal)

    total += self.score_cloud_break(signal)

    total += self.score_future_cloud(signal)

    total += self.score_cloud_twist(signal)

    total += self.score_chikou(signal)

    total += self.score_magnet(signal)

    total += self.score_levels(signal)

    total += self.score_flat(signal)

    signal.score = round(total,2)

    signal.buy_score = max(total,0)

    signal.sell_score = abs(min(total,0))

    return signal


# ==========================================================
# CONFIDENCE
# ==========================================================

def calculate_confidence(
    self,
    signal,
):

    confidence = abs(signal.score)

    confidence = min(confidence,100)

    signal.confidence = round(confidence,2)

    return signal


# ==========================================================
# STRENGTH
# ==========================================================

def calculate_strength(
    self,
    signal,
):

    if signal.confidence >= 90:

        signal.strength = "EXTREME"

    elif signal.confidence >= 80:

        signal.strength = "VERY_STRONG"

    elif signal.confidence >= 65:

        signal.strength = "STRONG"

    elif signal.confidence >= 45:

        signal.strength = "MEDIUM"

    elif signal.confidence >= 25:

        signal.strength = "WEAK"

    else:

        signal.strength = "VERY_WEAK"

    return signal


# ==========================================================
# FINAL TREND
# ==========================================================

def calculate_final_trend(
    self,
    signal,
):

    if signal.score >= 25:

        signal.trend = "BULLISH"

    elif signal.score <= -25:

        signal.trend = "BEARISH"

    else:

        signal.trend = "NEUTRAL"

    return signal


# ==========================================================
# APPLY
# ==========================================================

def update_score(
    self,
    signal,
):

    signal = self.calculate_total_score(signal)

    signal = self.calculate_confidence(signal)

    signal = self.calculate_strength(signal)

    signal = self.calculate_final_trend(signal)

    return signal
# ==========================================================
# FINAL DECISION ENGINE
# ==========================================================

BUY_THRESHOLD = 70
SELL_THRESHOLD = -70

STRONG_BUY = 90
STRONG_SELL = -90


# ==========================================================
# Build Reasons
# ==========================================================

def build_reasons(
    self,
    signal,
):

    reasons = []

    if signal.tk_cross == "BULLISH":
        reasons.append("Bullish TK Cross")

    elif signal.tk_cross == "BEARISH":
        reasons.append("Bearish TK Cross")

    # -------------------------

    if signal.cloud_break == "BULLISH":
        reasons.append("Bullish Cloud Break")

    elif signal.cloud_break == "BEARISH":
        reasons.append("Bearish Cloud Break")

    # -------------------------

    if signal.future_cloud == "BULLISH":
        reasons.append("Future Cloud Bullish")

    elif signal.future_cloud == "BEARISH":
        reasons.append("Future Cloud Bearish")

    # -------------------------

    if signal.cloud_twist == "BULLISH":
        reasons.append("Bullish Cloud Twist")

    elif signal.cloud_twist == "BEARISH":
        reasons.append("Bearish Cloud Twist")

    # -------------------------

    if signal.chikou_confirm:
        reasons.append("Chikou Confirmed")

    # -------------------------

    if signal.flat_kijun:
        reasons.append("Flat Kijun")

    if signal.flat_senkou_b:
        reasons.append("Flat Senkou B")

    # -------------------------

    if signal.magnet_state != "NONE":

        reasons.append(

            f"Ichimoku Magnet {signal.magnet_state}"

        )

    signal.reasons = reasons

    return signal
# ==========================================================
# Quality
# ==========================================================

def calculate_quality(
    self,
    signal,
):

    c = signal.confidence

    if c >= 95:

        signal.quality = "A+"

    elif c >= 90:

        signal.quality = "A"

    elif c >= 80:

        signal.quality = "B"

    elif c >= 70:

        signal.quality = "C"

    elif c >= 60:

        signal.quality = "D"

    else:

        signal.quality = "REJECT"

    return signal
# ==========================================================
# Trade Permission
# ==========================================================

def allow_trade(
    self,
    signal,
):

    if signal.quality == "REJECT":

        signal.trade_allowed = False

        return signal

    if signal.decision == "NO_SIGNAL":

        signal.trade_allowed = False

        return signal

    if signal.confidence < 70:

        signal.trade_allowed = False

        return signal

    signal.trade_allowed = True

    return signal
# ==========================================================
# Final
# ==========================================================

def finalize(
    self,
    signal,
):

    signal = self.build_reasons(signal)

    signal = self.calculate_decision(signal)

    signal = self.calculate_quality(signal)

    signal = self.allow_trade(signal)

    return signal
# ==========================================================
# ENTERPRISE TRADE MANAGEMENT
# ==========================================================

MIN_CONFIDENCE = 70

MIN_SCORE = 70

MIN_RR = 1.50

MAX_DISTANCE_FROM_KIJUN = 5.0

MAX_MAGNET_DISTANCE = 8.0
# ==========================================================
# ENTRY
# ==========================================================

def calculate_entry(
    self,
    signal,
):

    signal.entry = signal.last_price

    return signal
# ==========================================================
# STOP LOSS
# ==========================================================

def calculate_stoploss(
    self,
    signal,
):

    if signal.decision in ("BUY","STRONG_BUY"):

        sl = min(

            signal.kijun,

            signal.senkou_b,

            signal.support_level,

        )

    else:

        sl = max(

            signal.kijun,

            signal.senkou_b,

            signal.resistance_level,

        )

    signal.stoploss = round(sl,8)

    return signal
# ==========================================================
# TAKE PROFITS
# ==========================================================

def calculate_targets(
    self,
    signal,
):

    risk = abs(

        signal.entry -

        signal.stoploss

    )

    if signal.decision in ("BUY","STRONG_BUY"):

        signal.tp1 = signal.entry + risk * 1.5

        signal.tp2 = signal.entry + risk * 2.5

        signal.tp3 = signal.entry + risk * 4

    else:

        signal.tp1 = signal.entry - risk * 1.5

        signal.tp2 = signal.entry - risk * 2.5

        signal.tp3 = signal.entry - risk * 4

    return signal
# ==========================================================
# RISK REWARD
# ==========================================================

def calculate_rr(
    self,
    signal,
):

    risk = abs(

        signal.entry -

        signal.stoploss

    )

    reward = abs(

        signal.tp1 -

        signal.entry

    )

    if risk == 0:

        signal.rr = 0

    else:

        signal.rr = round(

            reward / risk,

            2,

        )

    return signal
# ==========================================================
# KIJUN DISTANCE
# ==========================================================

def kijun_distance_filter(
    self,
    signal,
):

    percent = abs(

        signal.entry -

        signal.kijun

    ) / signal.entry * 100

    signal.kijun_distance = round(percent,2)

    signal.kijun_ok = (

        percent <= MAX_DISTANCE_FROM_KIJUN

    )

    return signal
# ==========================================================
# MAGNET FILTER
# ==========================================================

def magnet_filter(
    self,
    signal,
):

    signal.magnet_ok = (

        signal.magnet_strength

        <=

        MAX_MAGNET_DISTANCE

    )

    return signal
# ==========================================================
# RR FILTER
# ==========================================================

def rr_filter(
    self,
    signal,
):

    signal.rr_ok = (

        signal.rr >= MIN_RR

    )

    return signal
# ==========================================================
# CONFIDENCE FILTER
# ==========================================================

def confidence_filter(
    self,
    signal,
):

    signal.confidence_ok = (

        signal.confidence

        >=

        MIN_CONFIDENCE

    )

    return signal
# ==========================================================
# SCORE FILTER
# ==========================================================

def score_filter(
    self,
    signal,
):

    signal.score_ok = (

        abs(signal.score)

        >=

        MIN_SCORE

    )

    return signal
# ==========================================================
# FINAL TRADE FILTER
# ==========================================================

def final_trade_filter(
    self,
    signal,
):

    checks = [

        signal.score_ok,

        signal.confidence_ok,

        signal.rr_ok,

        signal.kijun_ok,

        signal.magnet_ok,

    ]

    signal.trade_allowed = all(checks)

    return signal
# ==========================================================
# APPLY
# ==========================================================

def build_trade(
    self,
    signal,
):

    signal = self.calculate_entry(signal)

    signal = self.calculate_stoploss(signal)

    signal = self.calculate_targets(signal)

    signal = self.calculate_rr(signal)

    signal = self.kijun_distance_filter(signal)

    signal = self.magnet_filter(signal)

    signal = self.confidence_filter(signal)

    signal = self.score_filter(signal)

    signal = self.rr_filter(signal)

    signal = self.final_trade_filter(signal)

    return signal
# ==========================================================
# SECTION 9-1
# KUMO GRAVITY ENGINE
# ==========================================================

from dataclasses import dataclass
from typing import List
from typing import Optional


@dataclass
class GravityLevel:

    """
    یک سطح جاذبه ایچی
    """

    name: str

    price: float

    distance: float = 0.0

    atr_distance: float = 0.0

    strength: float = 0.0

    priority: int = 0

    bonus: float = 0.0

    score: float = 0.0


class KumoGravityEngine:

    """
    Kumo Gravity Engine

    مسئول محاسبه

    Gravity Levels

    فقط قوانین ثابت

    بدون AI
    """

    # -----------------------------------------------------

    def __init__(self):

        self.levels: List[GravityLevel] = []

        self.score = 0

    # -----------------------------------------------------

    def reset(self):

        self.levels.clear()

        self.score = 0

    # -----------------------------------------------------

    def calculate(

        self,

        close,

        senkou_a,

        senkou_b,

    ):

        """
        ساخت سطوح اولیه
        """

        self.reset()

        upper = max(

            senkou_a,

            senkou_b,

        )

        lower = min(

            senkou_a,

            senkou_b,

        )

        center = (

            senkou_a +

            senkou_b

        ) / 2

        # ----------------------------

        if close > upper:

            self.levels.append(

                GravityLevel(

                    name="Gravity_1",

                    price=upper,

                )

            )

            self.levels.append(

                GravityLevel(

                    name="Gravity_2",

                    price=center,

                )

            )

            self.levels.append(

                GravityLevel(

                    name="Gravity_3",

                    price=lower,

                )

            )

        elif close < lower:

            self.levels.append(

                GravityLevel(

                    name="Gravity_1",

                    price=lower,

                )

            )

            self.levels.append(

                GravityLevel(

                    name="Gravity_2",

                    price=center,

                )

            )

            self.levels.append(

                GravityLevel(

                    name="Gravity_3",

                    price=upper,

                )

            )

        else:

            self.levels.append(

                GravityLevel(

                    name="Upper_Gravity",

                    price=upper,

                )

            )

            self.levels.append(

                GravityLevel(

                    name="Center",

                    price=center,

                )

            )

            self.levels.append(

                GravityLevel(

                    name="Lower_Gravity",

                    price=lower,

                )

            )

        return self.levels
# ==========================================================
# SECTION 9-2
# DISTANCE
# ATR NORMALIZATION
# PRIORITY
# ==========================================================

    # -----------------------------------------------------
    # Distance
    # -----------------------------------------------------

    def calculate_distance(
        self,
        close: float,
    ) -> None:

        """
        فاصله قیمت تا هر سطح جاذبه
        """

        for level in self.levels:

            level.distance = abs(
                close - level.price
            )

    # -----------------------------------------------------
    # ATR Normalize
    # -----------------------------------------------------

    def normalize_distance(
        self,
        atr: float,
    ) -> None:

        """
        نرمال سازی فاصله با ATR
        """

        if atr <= 0:

            atr = 1e-8

        for level in self.levels:

            level.atr_distance = (
                level.distance / atr
            )

    # -----------------------------------------------------
    # Base Strength
    # -----------------------------------------------------

    def calculate_strength(self):

        """
        قدرت اولیه هر سطح
        """

        for level in self.levels:

            d = level.atr_distance

            if d <= 0.20:

                level.strength = 100

            elif d <= 0.40:

                level.strength = 95

            elif d <= 0.60:

                level.strength = 90

            elif d <= 0.80:

                level.strength = 85

            elif d <= 1.00:

                level.strength = 80

            elif d <= 1.20:

                level.strength = 70

            elif d <= 1.50:

                level.strength = 60

            elif d <= 2.00:

                level.strength = 45

            elif d <= 3.00:

                level.strength = 25

            else:

                level.strength = 10

    # -----------------------------------------------------
    # Priority
    # -----------------------------------------------------

    def calculate_priority(self):

        """
        تعیین اولویت سطوح جاذبه
        """

        ordered = sorted(

            self.levels,

            key=lambda x: x.distance

        )

        for index, level in enumerate(

            ordered,

            start=1,

        ):

            level.priority = index

    # -----------------------------------------------------
    # Get Nearest Level
    # -----------------------------------------------------

    def nearest_level(self) -> Optional[GravityLevel]:

        """
        نزدیکترین سطح جاذبه
        """

        if not self.levels:

            return None

        return min(

            self.levels,

            key=lambda x: x.distance,

        )

    # -----------------------------------------------------
    # Get Strongest Level
    # -----------------------------------------------------

    def strongest_level(self) -> Optional[GravityLevel]:

        """
        قوی‌ترین سطح جاذبه
        """

        if not self.levels:

            return None

        return max(

            self.levels,

            key=lambda x: x.strength,

        )
# ==========================================================
# SECTION 9-3
# ENTERPRISE GRAVITY BONUS ENGINE
# ==========================================================

    # -----------------------------------------------------
    # Cloud Thickness Bonus
    # -----------------------------------------------------

    def apply_cloud_thickness_bonus(
        self,
        thickness_score: float,
    ):

        """
        افزایش قدرت سطوح بر اساس ضخامت ابر

        thickness_score : 0..100
        """

        bonus = thickness_score * 0.15

        for level in self.levels:

            level.bonus += bonus

    # -----------------------------------------------------
    # Flat Senkou Bonus
    # -----------------------------------------------------

    def apply_flat_senkou_bonus(
        self,
        flat_levels: list,
    ):

        """
        اگر سطح جاذبه نزدیک Flat Senkou باشد

        قدرت آن افزایش پیدا می‌کند.
        """

        if not flat_levels:

            return

        tolerance = 0.001

        for level in self.levels:

            for flat in flat_levels:

                if abs(

                    level.price - flat

                ) <= tolerance * level.price:

                    level.bonus += 10

                    break

    # -----------------------------------------------------
    # Flat Kijun Bonus
    # -----------------------------------------------------

    def apply_flat_kijun_bonus(
        self,
        kijun_price: float,
    ):

        """
        اگر سطح جاذبه نزدیک Kijun باشد
        """

        if kijun_price is None:

            return

        tolerance = 0.001

        for level in self.levels:

            if abs(

                level.price - kijun_price

            ) <= tolerance * level.price:

                level.bonus += 8

    # -----------------------------------------------------
    # Magnet Bonus
    # -----------------------------------------------------

    def apply_magnet_bonus(
        self,
        magnet_score: float,
    ):

        """
        قدرت جاذبه عمومی ایچی
        """

        bonus = magnet_score * 0.10

        for level in self.levels:

            level.bonus += bonus

    # -----------------------------------------------------
    # Center Bonus
    # -----------------------------------------------------

    def apply_center_bonus(self):

        """
        مرکز ابر معمولاً اهمیت بیشتری دارد.
        """

        for level in self.levels:

            if "Center" in level.name:

                level.bonus += 5

    # -----------------------------------------------------
    # Final Strength
    # -----------------------------------------------------

    def calculate_final_strength(self):

        """
        محاسبه قدرت نهایی
        """

        for level in self.levels:

            value = (

                level.strength +

                level.bonus

            )

            value = max(

                0,

                min(

                    100,

                    value,

                ),

            )

            level.strength = value

    # -----------------------------------------------------
    # Confluence
    # -----------------------------------------------------

    def calculate_confluence(self):

        """
        اگر چند سطح تقریباً روی هم باشند

        قدرت افزایش پیدا می‌کند.
        """

        tolerance = 0.002

        count = len(self.levels)

        for i in range(count):

            current = self.levels[i]

            overlap = 0

            for j in range(count):

                if i == j:

                    continue

                other = self.levels[j]

                if abs(

                    current.price -

                    other.price

                ) <= tolerance * current.price:

                    overlap += 1

            current.bonus += overlap * 4

    # -----------------------------------------------------
    # Effective Score
    # -----------------------------------------------------

    def calculate_effective_score(self):

        """
        امتیاز نهایی بخش Gravity

        خروجی : 0..100
        """

        if not self.levels:

            self.score = 0

            return 0

        total = 0

        weight = 0

        for level in self.levels:

            w = (

                4

                if level.priority == 1

                else 3

                if level.priority == 2

                else 2

            )

            total += (

                level.strength * w

            )

            weight += w

        self.score = round(

            total / weight,

            2,

        )

        return self.score
# ==========================================================
# SECTION 9-4
# DYNAMIC GRAVITY ZONES
# ==========================================================

from collections import deque


class GravityMemory:

    """
    ثبت برخوردهای گذشته قیمت
    با سطوح جاذبه

    فقط جهت گزارش

    هیچ یادگیری انجام نمی‌شود.
    """

    def __init__(self):

        self.history = deque(maxlen=300)

    # -------------------------------------------------

    def register(

        self,

        level_name,

        level_price,

        touched,

    ):

        self.history.append({

            "level": level_name,

            "price": level_price,

            "touched": touched,

        })

    # -------------------------------------------------

    def touch_count(

        self,

        level_name,

    ):

        return sum(

            1

            for x in self.history

            if x["level"] == level_name

            and x["touched"]

        )
# -----------------------------------------------------
# Dynamic Gravity Zone
# -----------------------------------------------------

    def calculate_dynamic_zone(

        self,

        atr,

    ):

        """
        محدوده واقعی هر سطح

        Zone = ± ATR درصد
        """

        for level in self.levels:

            zone = atr * 0.30

            level.zone_high = (

                level.price + zone

            )

            level.zone_low = (

                level.price - zone

            )
# -----------------------------------------------------
# Price Inside Gravity Zone
# -----------------------------------------------------

    def price_inside_zone(

        self,

        close,

    ):

        for level in self.levels:

            level.inside_zone = (

                level.zone_low

                <= close

                <= level.zone_high

            )
# -----------------------------------------------------
# Touch Detection
# -----------------------------------------------------

    def detect_touch(

        self,

        close,

        memory,

    ):

        for level in self.levels:

            touched = (

                level.zone_low

                <= close

                <= level.zone_high

            )

            memory.register(

                level.name,

                level.price,

                touched,

            )
# -----------------------------------------------------
# Historical Gravity Bonus
# -----------------------------------------------------

    def historical_bonus(

        self,

        memory,

    ):

        """
        اگر سطح بارها لمس شده باشد

        فقط گزارش می‌شود.

        امتیاز کمی افزایش پیدا می‌کند.
        """

        for level in self.levels:

            count = memory.touch_count(

                level.name

            )

            if count >= 10:

                level.bonus += 3

            elif count >= 20:

                level.bonus += 5

            elif count >= 40:

                level.bonus += 8
# -----------------------------------------------------
# Gravity Rank
# -----------------------------------------------------

    def rank_levels(self):

        self.levels.sort(

            key=lambda x: (

                x.priority,

                -x.strength,

            )

        )
# -----------------------------------------------------
# Enterprise Report
# -----------------------------------------------------

    def report(self):

        report = []

        for level in self.levels:

            report.append({

                "name":

                    level.name,

                "price":

                    round(level.price, 6),

                "strength":

                    round(level.strength, 2),

                "priority":

                    level.priority,

                "distance":

                    round(level.distance, 3),

                "atr_distance":

                    round(level.atr_distance, 3),

                "inside_zone":

                    level.inside_zone,

                "bonus":

                    round(level.bonus, 2),

            })

        return report
# ==========================================================
# SECTION 9-5
# GRAVITY SCORE INTEGRATION
# ==========================================================

class GravityScoreEngine:

    """
    مسئول تبدیل اطلاعات Gravity
    به امتیاز داخلی ایچیموکو
    """

    def __init__(self):

        self.score = 0.0

        self.direction = "NEUTRAL"

        self.confidence = 0.0

        self.reasons = []

    # -------------------------------------------------

    def reset(self):

        self.score = 0

        self.direction = "NEUTRAL"

        self.confidence = 0

        self.reasons.clear()

    # -------------------------------------------------

    def calculate(

        self,

        close,

        gravity_levels,

    ):

        """
        محاسبه امتیاز Gravity
        """

        self.reset()

        if not gravity_levels:

            return self.output()

        nearest = gravity_levels[0]

        # ---------------------------------------------
        # جهت جاذبه
        # ---------------------------------------------

        if nearest.price > close:

            self.direction = "BUY"

        elif nearest.price < close:

            self.direction = "SELL"

        else:

            self.direction = "NEUTRAL"

        # ---------------------------------------------
        # امتیاز اولیه
        # ---------------------------------------------

        self.score = nearest.strength

        # ---------------------------------------------
        # اگر داخل Zone باشد
        # ---------------------------------------------

        if nearest.inside_zone:

            self.score += 5

            self.reasons.append(

                "Inside Gravity Zone"

            )

        # ---------------------------------------------
        # Bonus
        # ---------------------------------------------

        self.score += nearest.bonus

        # ---------------------------------------------
        # محدودسازی
        # ---------------------------------------------

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )

        # ---------------------------------------------
        # Confidence
        # ---------------------------------------------

        self.confidence = self.score

        # ---------------------------------------------

        self.reasons.append(

            f"Nearest Level : {nearest.name}"
# ==========================================================
# SECTION 9-6
# MULTI GRAVITY CLUSTER ENGINE
# ==========================================================

class GravityClusterEngine:

    """
    پیدا کردن خوشه های جاذبه

    Gravity Cluster

    """

    def __init__(self):

        self.clusters = []

    # -------------------------------------------------

    def reset(self):

        self.clusters.clear()

    # -------------------------------------------------

    def detect(

        self,

        gravity_levels,

    ):

        self.reset()

        if len(gravity_levels) == 0:

            return []

        tolerance = 0.003

        used = set()

        for i in range(

            len(gravity_levels)

        ):

            if i in used:

                continue

            base = gravity_levels[i]

            cluster = [

                base

            ]

            used.add(i)

            for j in range(

                i + 1,

                len(gravity_levels)

            ):

                other = gravity_levels[j]

                if abs(

                    base.price -

                    other.price

                ) <= (

                    tolerance *

                    base.price

                ):

                    cluster.append(

                        other

                    )

                    used.add(j)

            self.clusters.append(

                cluster

            )

        return self.clusters
    # -------------------------------------------------

    def calculate_strength(

        self,

    ):

        result = []

        for cluster in self.clusters:

            strength = sum(

                x.strength

                for x in cluster

            )

            strength /= len(cluster)

            result.append({

                "price":

                    cluster[0].price,

                "members":

                    len(cluster),

                "strength":

                    round(

                        strength,

                        2,

                    ),

            })

        return result
    # -------------------------------------------------

    def cluster_bonus(

        self,

        cluster,

    ):

        members = cluster["members"]

        if members == 1:

            return 0

        elif members == 2:

            return 5

        elif members == 3:

            return 10

        elif members >= 4:

            return 15

        return 0

        )

        self.reasons.append(

            f"Priority : {nearest.priority}"

        )

        self.reasons.append(

            f"Strength : {nearest.strength:.1f}"

        )

        return self.output()
    # -------------------------------------------------

    def output(self):

        return {

            "engine":

                "Gravity",

            "direction":

                self.direction,

            "score":

                round(self.score,2),

            "confidence":

                round(self.confidence,2),

            "reasons":

                self.reasons,

        }
    gravity_result = gravity_engine.calculate(
        close,
        gravity_levels,
    ) 

    gravity_score = gravity_result["score"]
    internal_score += gravity_score * 0.10
# ==========================================================
# SECTION 9-6
# MULTI GRAVITY CLUSTER ENGINE
# ==========================================================

class GravityClusterEngine:

    """
    پیدا کردن خوشه های جاذبه

    Gravity Cluster

    """

    def __init__(self):

        self.clusters = []

    # -------------------------------------------------

    def reset(self):

        self.clusters.clear()

    # -------------------------------------------------

    def detect(

        self,

        gravity_levels,

    ):

        self.reset()

        if len(gravity_levels) == 0:

            return []

        tolerance = 0.003

        used = set()

        for i in range(

            len(gravity_levels)

        ):

            if i in used:

                continue

            base = gravity_levels[i]

            cluster = [

                base

            ]

            used.add(i)

            for j in range(

                i + 1,

                len(gravity_levels)

            ):

                other = gravity_levels[j]

                if abs(

                    base.price -

                    other.price

                ) <= (

                    tolerance *

                    base.price

                ):

                    cluster.append(

                        other

                    )

                    used.add(j)

            self.clusters.append(

                cluster

            )

        return self.clusters
    # -------------------------------------------------

    def calculate_strength(

        self,

    ):

        result = []

        for cluster in self.clusters:

            strength = sum(

                x.strength

                for x in cluster

            )

            strength /= len(cluster)

            result.append({

                "price":

                    cluster[0].price,

                "members":

                    len(cluster),

                "strength":

                    round(

                        strength,

                        2,

                    ),

            })

        return result
    # -------------------------------------------------

    def cluster_bonus(

        self,

        cluster,

    ):

        members = cluster["members"]

        if members == 1:

            return 0

        elif members == 2:

            return 5

        elif members == 3:

            return 10

        elif members >= 4:

            return 15

        return 0
    # -------------------------------------------------

    def cluster_score(

        self,

    ):

        data = self.calculate_strength()

        if len(data) == 0:

            return 0

        scores = []

        for item in data:

            value = (

                item["strength"]

                +

                self.cluster_bonus(

                    item

                )

            )

            value = max(

                0,

                min(

                    100,

                    value,

                ),

            )

            scores.append(

                value

            )

        return max(scores)
# ==========================================================
# SECTION 9-7
# KUMO GRAVITY PROJECTION ENGINE
# ==========================================================

class GravityProjectionEngine:

    """
    پیش بینی مقصد بعدی قیمت
    بین سطوح جاذبه
    """

    def __init__(self):

        self.current_level = None

        self.next_level = None

        self.previous_level = None

        self.direction = "NEUTRAL"

        self.score = 0
    # -------------------------------------------------

    def locate_price(

        self,

        close,

        gravity_levels,

    ):

        if len(gravity_levels) == 0:

            return

        ordered = sorted(

            gravity_levels,

            key=lambda x: x.price

        )

        nearest = min(

            ordered,

            key=lambda x: abs(

                close -

                x.price

            )

        )

        self.current_level = nearest
    # -------------------------------------------------

    def project(

        self,

        close,

        gravity_levels,

    ):

        ordered = sorted(

            gravity_levels,

            key=lambda x: x.price

        )

        idx = ordered.index(

            self.current_level

        )

        # ------------------------------

        if close >

            self.current_level.price:

            self.direction = "UP"

            if idx < len(ordered)-1:

                self.next_level = ordered[idx+1]

        # ------------------------------

        elif close <

            self.current_level.price:

            self.direction = "DOWN"

            if idx > 0:

                self.next_level = ordered[idx-1]
    # -------------------------------------------------

    def target_distance(

        self,

        close,

    ):

        if self.next_level is None:

            return None

        return abs(

            self.next_level.price -

            close

        )
    # -------------------------------------------------

    def probability(

        self,

        atr,

    ):

        if self.next_level is None:

            return 0

        d = self.target_distance(

            self.current_level.price

        )

        ratio = d / atr

        if ratio <= 0.5:

            return 95

        elif ratio <= 1:

            return 85

        elif ratio <= 1.5:

            return 70

        elif ratio <= 2:

            return 55

        elif ratio <= 3:

            return 35

        return 10
    # -------------------------------------------------

    def calculate_score(

        self,

        atr,

    ):

        self.score = self.probability(

            atr

        )

        return self.score
    # -------------------------------------------------

    def output(self):

        return {

            "direction":

                self.direction,

            "current":

                None if self.current_level is None

                else self.current_level.price,

            "target":

                None if self.next_level is None

                else self.next_level.price,

            "score":

                self.score,

        }
# ==========================================================
# SECTION 9-8
# KUMO GRAVITY VALIDATION ENGINE
# ==========================================================

class GravityValidationEngine:

    """
    اعتبارسنجی سطوح جاذبه

    این موتور تصمیم نمی‌گیرد معامله انجام شود.

    فقط کیفیت سطح را ارزیابی می‌کند.
    """

    def __init__(self):

        self.score = 0

        self.valid = False

        self.reasons = []
    # -------------------------------------------------

    def reset(self):

        self.score = 0

        self.valid = False

        self.reasons.clear()
    # -------------------------------------------------

    def validate_distance(

        self,

        level,

    ):

        """
        اگر سطح خیلی دور باشد

        کیفیت کاهش پیدا می‌کند.
        """

        if level.atr_distance <= 0.5:

            self.score += 25

            self.reasons.append(

                "Near Gravity"

            )

        elif level.atr_distance <= 1:

            self.score += 18

        elif level.atr_distance <= 1.5:

            self.score += 10

        else:

            self.score += 2
    # -------------------------------------------------

    def validate_strength(

        self,

        level,

    ):

        if level.strength >= 90:

            self.score += 25

            self.reasons.append(

                "Strong Gravity"

            )

        elif level.strength >= 80:

            self.score += 20

        elif level.strength >= 70:

            self.score += 15

        elif level.strength >= 60:

            self.score += 10

        else:

            self.score += 3
    # -------------------------------------------------

    def validate_priority(

        self,

        level,

    ):

        if level.priority == 1:

            self.score += 20

            self.reasons.append(

                "Priority 1"

            )

        elif level.priority == 2:

            self.score += 12

        elif level.priority == 3:

            self.score += 6
    # -------------------------------------------------

    def validate_cluster(

        self,

        cluster_members,

    ):

        if cluster_members >= 4:

            self.score += 20

            self.reasons.append(

                "Large Cluster"

            )

        elif cluster_members == 3:

            self.score += 15

        elif cluster_members == 2:

            self.score += 10
    # -------------------------------------------------

    def validate_zone(

        self,

        inside_zone,

    ):

        if inside_zone:

            self.score += 10

            self.reasons.append(

                "Inside Gravity Zone"

            )
    # -------------------------------------------------

    def finalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )

        self.valid = (

            self.score >= 70

        )

        return self.valid
    # -------------------------------------------------

    def output(self):

        return {

            "validation_score":

                self.score,

            "valid":

                self.valid,

            "reasons":

                self.reasons,

        }
# ==========================================================
# SECTION 9-9
# ENTERPRISE DECISION LAYER
# ==========================================================

class IchimokuDecisionEngine:

    """
    تصمیم نهایی داخلی ایچیموکو

    مستقل

    بدون وابستگی به RSI

    بدون وابستگی به Pivot

    بدون وابستگی به Candle

    """

    def __init__(self):

        self.internal_score = 0

        self.direction = "NEUTRAL"

        self.confidence = 0

        self.reasons = []

        self.state = "NONE"
    # -------------------------------------------------

    def reset(self):

        self.internal_score = 0

        self.direction = "NEUTRAL"

        self.confidence = 0

        self.reasons.clear()

        self.state = "NONE"
    # -------------------------------------------------

    def collect_scores(

        self,

        trend,

        cloud,

        tk,

        chikou,

        magnet,

        gravity,

        projection,

        validation,

    ):

        self.internal_score = (

            trend +

            cloud +

            tk +

            chikou +

            magnet +

            gravity +

            projection +

            validation

        )
    # -------------------------------------------------

    def normalize(self):

        self.internal_score = max(

            0,

            min(

                100,

                self.internal_score,

            ),

        )
    # -------------------------------------------------

    def calculate_confidence(self):

        self.confidence = self.internal_score
    # -------------------------------------------------

    def determine_state(self):

        score = self.internal_score

        if score >= 90:

            self.state = "VERY_STRONG"

        elif score >= 80:

            self.state = "STRONG"

        elif score >= 70:

            self.state = "GOOD"

        elif score >= 60:

            self.state = "NORMAL"

        elif score >= 40:

            self.state = "WEAK"

        else:

            self.state = "VERY_WEAK"
    # -------------------------------------------------

    def determine_direction(

        self,

        trend_direction,

        projection_direction,

    ):

        if (

            trend_direction ==

            projection_direction

        ):

            self.direction = trend_direction

        else:

            self.direction = "NEUTRAL"
    # -------------------------------------------------

    def quality(self):

        if self.internal_score >= 90:

            return "A+"

        elif self.internal_score >= 80:

            return "A"

        elif self.internal_score >= 70:

            return "B"

        elif self.internal_score >= 60:

            return "C"

        elif self.internal_score >= 50:

            return "D"

        return "F"
    # -------------------------------------------------

    def report(self):

        return {

            "engine":

                "Ichimoku",

            "direction":

                self.direction,

            "internal_score":

                round(

                    self.internal_score,

                    2,

                ),

            "confidence":

                round(

                    self.confidence,

                    2,

                ),

            "quality":

                self.quality(),

            "state":

                self.state,

            "reasons":

                self.reasons,

        }
{

"engine":"Ichimoku",

"direction":"BUY",

"internal_score":86.4,

"confidence":86.4,

"quality":"A",

"state":"STRONG",

"reasons":[

"Strong Trend",

"TK Cross",

"Strong Cloud",

"Gravity Cluster",

"Projection"

]

}
# ==========================================================
# SECTION 9-10
# ENTERPRISE VALIDATION & SAFETY LAYER
# ==========================================================

import math
import numpy as np


class IchimokuValidationEngine:

    """
    اعتبارسنجی کامل داده‌ها

    این موتور هیچ سیگنالی تولید نمی‌کند.

    فقط بررسی می‌کند که داده‌ها
    قابل اعتماد هستند یا خیر.
    """

    def __init__(self):

        self.valid = True

        self.errors = []

        self.warnings = []

        self.score = 100
    # -----------------------------------------------------

    def reset(self):

        self.valid = True

        self.errors.clear()

        self.warnings.clear()

        self.score = 100
    # -----------------------------------------------------

    def validate_candle_count(

        self,

        candles,

        minimum,

    ):

        if candles is None:

            self.valid = False

            self.errors.append(

                "No Candle Data"

            )

            return

        if len(candles) < minimum:

            self.valid = False

            self.errors.append(

                f"Need {minimum} Candles"

            )
    # -----------------------------------------------------

    def validate_columns(

        self,

        candles,

    ):

        required = [

            "open",

            "high",

            "low",

            "close",

            "volume",

        ]

        for c in required:

            if c not in candles.columns:

                self.valid = False

                self.errors.append(

                    f"Missing Column : {c}"

                )
    # -----------------------------------------------------

    def validate_nan(

        self,

        candles,

    ):

        if candles.isnull().values.any():

            self.score -= 20

            self.warnings.append(

                "NaN Detected"

            )
    # -----------------------------------------------------

    def validate_zero_price(

        self,

        candles,

    ):

        if (

            candles["close"] <= 0

        ).any():

            self.valid = False

            self.errors.append(

                "Invalid Close"

            )
    # -----------------------------------------------------

    def validate_high_low(

        self,

        candles,

    ):

        bad = (

            candles["high"]

            <

            candles["low"]

        )

        if bad.any():

            self.valid = False

            self.errors.append(

                "High < Low"

            )
    # -----------------------------------------------------

    def validate_volume(

        self,

        candles,

    ):

        if (

            candles["volume"]

            == 0

        ).all():

            self.score -= 10

            self.warnings.append(

                "Volume Zero"

            )
    # -----------------------------------------------------

    def validate_atr(

        self,

        atr,

    ):

        if atr is None:

            self.valid = False

            self.errors.append(

                "ATR Missing"

            )

            return

        if math.isnan(atr):

            self.valid = False

            self.errors.append(

                "ATR NaN"

            )
    # -----------------------------------------------------

    def validate_timeframe(

        self,

        timeframe,

    ):

        allowed = [

            "1m",

            "5m",

            "15m",

            "30m",

            "1h",

            "2h",

            "4h",

            "8h",

            "12h",

            "1d",

            "2d",

            "3d",

        ]

        if timeframe not in allowed:

            self.valid = False

            self.errors.append(

                "Invalid TimeFrame"

            )
    # -----------------------------------------------------

    def finalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )

        return self.valid
    # -----------------------------------------------------

    def report(self):

        return {

            "valid": self.valid,

            "score": self.score,

            "errors": self.errors,

            "warnings": self.warnings,

        }
{

"valid":True,

"score":90,

"errors":[],

"warnings":[

"Volume Zero"

]

}
validator.reset()

validator.validate_candle_count(
    candles,
    minimum=52
)

validator.validate_columns(
    candles
)

validator.validate_nan(
    candles
)

validator.validate_zero_price(
    candles
)

validator.validate_high_low(
    candles
)

validator.validate_volume(
    candles
)

validator.validate_atr(
    atr
)

validator.validate_timeframe(
    timeframe
)

validator.finalize()
if not validator.valid:

    return validator.report()
# ==========================================================
# SECTION 9-11
# MULTI TIMEFRAME SYNCHRONIZATION ENGINE
# ==========================================================

from dataclasses import dataclass
from typing import Dict
from typing import List


@dataclass
class TimeFrameState:

    timeframe: str

    direction: str

    score: float


class IchimokuSynchronizationEngine:

    """
    بررسی همسو بودن ایچی در تایم فریم های مختلف

    مستقل

    بدون وابستگی به سایر Engine ها
    """

    def __init__(self):

        self.states: List[TimeFrameState] = []

        self.buy_count = 0

        self.sell_count = 0

        self.neutral_count = 0

        self.score = 0

        self.direction = "NEUTRAL"

        self.confidence = 0

    # ------------------------------------------------------

    def reset(self):

        self.states.clear()

        self.buy_count = 0

        self.sell_count = 0

        self.neutral_count = 0

        self.score = 0

        self.direction = "NEUTRAL"

        self.confidence = 0

    # ------------------------------------------------------

    def add_timeframe(

        self,

        timeframe: str,

        direction: str,

        score: float,

    ):

        self.states.append(

            TimeFrameState(

                timeframe=timeframe,

                direction=direction,

                score=score,

            )

        )
    # ------------------------------------------------------

    def classify(self):

        self.buy_count = 0

        self.sell_count = 0

        self.neutral_count = 0

        for state in self.states:

            if state.direction == "BUY":

                self.buy_count += 1

            elif state.direction == "SELL":

                self.sell_count += 1

            else:

                self.neutral_count += 1
    # ------------------------------------------------------

    def determine_direction(self):

        if self.buy_count > self.sell_count:

            self.direction = "BUY"

        elif self.sell_count > self.buy_count:

            self.direction = "SELL"

        else:

            self.direction = "NEUTRAL"
# ------------------------------------------------------
# Timeframe Weight
# ------------------------------------------------------

TIMEFRAME_WEIGHT = {

    "1m": 1,
    "5m": 2,
    "15m": 3,
    "30m": 5,

    "1h": 8,
    "2h": 9,
    "4h": 12,

    "8h": 8,
    "12h": 7,

    "1d": 15,
    "2d": 12,
    "3d": 10,

}
# ------------------------------------------------------
# Synchronization Score
# ------------------------------------------------------

def calculate_score(self):

    total_weight = 0

    agree_weight = 0

    for state in self.states:

        w = TIMEFRAME_WEIGHT.get(

            state.timeframe,

            1,

        )

        total_weight += w

        if state.direction == self.direction:

            agree_weight += w

    if total_weight == 0:

        self.score = 0

        return

    self.score = (

        agree_weight /

        total_weight

    ) * 100
# ------------------------------------------------------
# Higher Timeframe Conflict
# ------------------------------------------------------

def detect_htf_conflict(self):

    penalty = 0

    high_tf = [

        "4h",

        "8h",

        "12h",

        "1d",

        "2d",

        "3d",

    ]

    for state in self.states:

        if (

            state.timeframe in high_tf

            and

            state.direction != self.direction

            and

            state.direction != "NEUTRAL"

        ):

            penalty += 8

    self.score -= penalty
# ------------------------------------------------------
# Lower Timeframe Conflict
# ------------------------------------------------------

def detect_ltf_conflict(self):

    penalty = 0

    low_tf = [

        "1m",

        "5m",

        "15m",

        "30m",

    ]

    for state in self.states:

        if (

            state.timeframe in low_tf

            and

            state.direction != self.direction

            and

            state.direction != "NEUTRAL"

        ):

            penalty += 2

    self.score -= penalty
# ------------------------------------------------------
# Perfect Alignment Bonus
# ------------------------------------------------------

def perfect_alignment_bonus(self):

    total = len(self.states)

    agree = sum(

        1

        for s in self.states

        if s.direction == self.direction

    )

    if agree == total:

        self.score += 5
# ------------------------------------------------------
# Clamp
# ------------------------------------------------------

def normalize(self):

    self.score = max(

        0,

        min(

            100,

            self.score,

        ),

    )
# ------------------------------------------------------
# Confidence
# ------------------------------------------------------

def calculate_confidence(self):

    self.confidence = self.score
# ------------------------------------------------------
# Output
# ------------------------------------------------------

def output(self):

    return {

        "direction":

            self.direction,

        "score":

            round(

                self.score,

                2,

            ),

        "confidence":

            round(

                self.confidence,

                2,

            ),

        "buy":

            self.buy_count,

        "sell":

            self.sell_count,

        "neutral":

            self.neutral_count,

    }
{

    "direction":"BUY",

    "score":91.4,

    "confidence":91.4,

    "buy":10,

    "sell":1,

    "neutral":1,

}
# ==========================================================
# SECTION 9-12
# INTERNAL CONFLICT DETECTOR
# ==========================================================

class IchimokuConflictEngine:

    """
    بررسی تضادهای داخلی ایچیموکو

    فقط اجزای خود ایچی بررسی می‌شوند.

    خروجی:

    Penalty

    Conflict Count

    Conflict Score

    """

    def __init__(self):

        self.reset()

    # -----------------------------------------------------

    def reset(self):

        self.penalty = 0

        self.conflicts = []

        self.score = 100
    # -----------------------------------------------------

    def trend_vs_tk(

        self,

        trend,

        tk,

    ):

        if trend == "NEUTRAL":

            return

        if tk == "NEUTRAL":

            return

        if trend != tk:

            self.penalty += 8

            self.conflicts.append(

                "Trend vs TK"

            )
    # -----------------------------------------------------

    def trend_vs_cloud(

        self,

        trend,

        cloud,

    ):

        if trend == "NEUTRAL":

            return

        if cloud == "NEUTRAL":

            return

        if trend != cloud:

            self.penalty += 10

            self.conflicts.append(

                "Trend vs Cloud"

            )
    # -----------------------------------------------------

    def trend_vs_chikou(

        self,

        trend,

        chikou,

    ):

        if trend == "NEUTRAL":

            return

        if chikou == "NEUTRAL":

            return

        if trend != chikou:

            self.penalty += 6

            self.conflicts.append(

                "Trend vs Chikou"

            )
    # -----------------------------------------------------

    def trend_vs_projection(

        self,

        trend,

        projection,

    ):

        if trend == "NEUTRAL":

            return

        if projection == "NEUTRAL":

            return

        if trend != projection:

            self.penalty += 5

            self.conflicts.append(

                "Trend vs Projection"

            )
    # -----------------------------------------------------

    def trend_vs_gravity(

        self,

        trend,

        gravity,

    ):

        if trend == "NEUTRAL":

            return

        if gravity == "NEUTRAL":

            return

        if trend != gravity:

            self.penalty += 5

            self.conflicts.append(

                "Trend vs Gravity"

            )
    # -----------------------------------------------------

    def tk_vs_cloud(

        self,

        tk,

        cloud,

    ):

        if tk == "NEUTRAL":

            return

        if cloud == "NEUTRAL":

            return

        if tk != cloud:

            self.penalty += 5

            self.conflicts.append(

                "TK vs Cloud"

            )
    # -----------------------------------------------------

    def tk_vs_chikou(

        self,

        tk,

        chikou,

    ):

        if tk == "NEUTRAL":

            return

        if chikou == "NEUTRAL":

            return

        if tk != chikou:

            self.penalty += 4

            self.conflicts.append(

                "TK vs Chikou"

            )
    # -----------------------------------------------------

    def projection_vs_gravity(

        self,

        projection,

        gravity,

    ):

        if projection == "NEUTRAL":

            return

        if gravity == "NEUTRAL":

            return

        if projection != gravity:

            self.penalty += 4

            self.conflicts.append(

                "Projection vs Gravity"

            )
    # -----------------------------------------------------

    def finalize(self):

        self.score = max(

            0,

            100 -

            self.penalty,

        )

        return self.score
    # -----------------------------------------------------

    def report(self):

        return {

            "penalty":

                self.penalty,

            "score":

                self.score,

            "count":

                len(

                    self.conflicts

                ),

            "conflicts":

                self.conflicts,

        }
{

"penalty":18,

"score":82,

"count":3,

"conflicts":[

"Trend vs Cloud",

"Trend vs Chikou",

"Projection vs Gravity"

]

}
conflict = conflict_engine.report()

internal_score = max(

    0,

    internal_score -

    conflict["penalty"]

)
# ==========================================================
# SECTION 9-13
# MARKET PHASE DETECTOR
# ==========================================================

class IchimokuMarketPhase:

    def __init__(self):

        self.phase = "UNKNOWN"

        self.score = 0

        self.confidence = 0

        self.reasons = []
    def reset(self):

        self.phase = "UNKNOWN"

        self.score = 0

        self.confidence = 0

        self.reasons.clear()
    def detect_uptrend(

        self,

        trend,

        cloud,

        chikou,

        price_position,

    ):

        if (

            trend == "BUY"

            and

            cloud == "BUY"

            and

            chikou == "BUY"

            and

            price_position == "ABOVE"

        ):

            self.phase = "TREND_UP"

            self.score = 100

            self.reasons.append(

                "Strong Bull Trend"

            )
    def detect_downtrend(

        self,

        trend,

        cloud,

        chikou,

        price_position,

    ):

        if (

            trend == "SELL"

            and

            cloud == "SELL"

            and

            chikou == "SELL"

            and

            price_position == "BELOW"

        ):

            self.phase = "TREND_DOWN"

            self.score = 100

            self.reasons.append(

                "Strong Bear Trend"

            )
    def detect_pullback(

        self,

        trend,

        tk,

        price_position,

    ):

        if (

            trend == "BUY"

            and

            tk == "SELL"

            and

            price_position == "ABOVE"

        ):

            self.phase = "PULLBACK"

            self.score = 80

            self.reasons.append(

                "Bull Pullback"

            )
    def detect_breakout(

        self,

        cloud_break,

        chikou,

    ):

        if (

            cloud_break

            and

            chikou == "BUY"

        ):

            self.phase = "BREAKOUT"

            self.score = 90

            self.reasons.append(

                "Cloud Breakout"

            )
    def detect_range(

        self,

        cloud_flat,

        tk_flat,

    ):

        if (

            cloud_flat

            and

            tk_flat

        ):

            self.phase = "RANGE"

            self.score = 60

            self.reasons.append(

                "Flat Market"

            )
    def detect_compression(

        self,

        cloud_thickness,

    ):

        if cloud_thickness < 20:

            self.phase = "COMPRESSION"

            self.score = 75

            self.reasons.append(

                "Thin Cloud"

            )
    def detect_expansion(

        self,

        cloud_thickness,

    ):

        if cloud_thickness > 70:

            self.phase = "EXPANSION"

            self.score = 90

            self.reasons.append(

                "Strong Expansion"

            )
    def detect_exhaustion(

        self,

        trend_score,

        momentum,

    ):

        if (

            trend_score > 85

            and

            momentum < 30

        ):

            self.phase = "TREND_EXHAUSTION"

            self.score = 70

            self.reasons.append(

                "Momentum Weak"

            )
    def detect_fake_breakout(

        self,

        breakout,

        chikou,

    ):

        if (

            breakout

            and

            chikou == "SELL"

        ):

            self.phase = "FAKE_BREAKOUT"

            self.score = 40

            self.reasons.append(

                "Weak Confirmation"

            )
    def detect_reversal(

        self,

        trend,

        projection,

    ):

        if (

            trend != projection

            and

            trend != "NEUTRAL"

        ):

            self.phase = "REVERSAL"

            self.score = 65

            self.reasons.append(

                "Projection Conflict"

            )
    def calculate_confidence(self):

        self.confidence = self.score
    def report(self):

        return {

            "phase": self.phase,

            "score": self.score,

            "confidence": self.confidence,

            "reasons": self.reasons,

        }
{

"phase":"TREND_UP",

"score":95,

"confidence":95,

"reasons":[

"Strong Bull Trend",

"Cloud Bullish",

"Chikou Confirmed"

]

}
phase = phase_engine.report()

internal_score += phase["score"] * 0.05
# ==========================================================
# SECTION 9-14
# SIGNAL QUALITY ENGINE
# ==========================================================

class IchimokuSignalQualityEngine:

    """
    Enterprise Signal Quality Engine

    این موتور فقط کیفیت تحلیل ایچی را می‌سنجد.

    هیچ تصمیم معامله‌ای نمی‌گیرد.

    هیچ وابستگی به سایر Engine ها ندارد.
    """

    def __init__(self):

        self.reset()

    # -----------------------------------------------------

    def reset(self):

        self.internal_score = 0

        self.quality = "UNKNOWN"

        self.grade = "F"

        self.reasons = []

        self.direction = "NEUTRAL"

        self.confidence = 0
    # -----------------------------------------------------

    def load_scores(

        self,

        trend,

        cloud,

        tk,

        chikou,

        gravity,

        projection,

        validation,

        synchronization,

        phase,

        conflict_penalty,

    ):

        self.internal_score = (

            trend +

            cloud +

            tk +

            chikou +

            gravity +

            projection +

            validation +

            synchronization +

            phase

        )

        self.internal_score -= conflict_penalty
    # -----------------------------------------------------

    def normalize(self):

        self.internal_score = max(

            0,

            min(

                100,

                self.internal_score,

            ),

        )
    # -----------------------------------------------------

    def classify(self):

        s = self.internal_score

        if s >= 95:

            self.quality = "ELITE"

            self.grade = "A+"

        elif s >= 90:

            self.quality = "VERY_HIGH"

            self.grade = "A"

        elif s >= 80:

            self.quality = "HIGH"

            self.grade = "B"

        elif s >= 70:

            self.quality = "GOOD"

            self.grade = "C"

        elif s >= 60:

            self.quality = "NORMAL"

            self.grade = "D"

        else:

            self.quality = "WEAK"

            self.grade = "F"
    # -----------------------------------------------------

    def calculate_confidence(self):

        self.confidence = self.internal_score
    # -----------------------------------------------------

    def set_direction(

        self,

        trend_direction,

    ):

        self.direction = trend_direction
    # -----------------------------------------------------

    def build_reason(

        self,

        trend,

        gravity,

        phase,

    ):

        if trend > 20:

            self.reasons.append(

                "Trend Confirmed"

            )

        if gravity > 8:

            self.reasons.append(

                "Strong Gravity"

            )

        if phase > 4:

            self.reasons.append(

                "Market Phase Confirmed"

            )
    # -----------------------------------------------------

    def report(self):

        return {

            "engine":

                "ICHIMOKU",

            "direction":

                self.direction,

            "internal_score":

                round(

                    self.internal_score,

                    2,

                ),

            "confidence":

                round(

                    self.confidence,

                    2,

                ),

            "quality":

                self.quality,

            "grade":

                self.grade,

            "reasons":

                self.reasons,

        }
{

"engine":"ICHIMOKU",

"direction":"BUY",

"internal_score":92.40,

"confidence":92.40,

"quality":"VERY_HIGH",

"grade":"A",

"reasons":[

"Trend Confirmed",

"Strong Gravity",

"Market Phase Confirmed"

]

}
ichimoku_result = quality_engine.report()
class IchimokuReliabilityEngine:

    def __init__(self):

        self.score = 100

        self.reasons = []

        self.stability = "UNKNOWN"
Penalty = 8
10
{
    "engine": "ICHIMOKU",

    "direction": "BUY",

    "engine_score": 82,

    "weight": 20,

    "final_score": 16.4,

    "confidence": 91,

    "market_phase": "TREND_UP",

    "quality": "VERY_HIGH",

    "grade": "A",

    "reasons": [

        "Strong Trend",

        "Cloud Bullish",

        "Gravity Cluster",

        "Projection Confirmed"

    ],

    "warnings": [

        "Minor TK Conflict"

    ],

    "valid": True

}