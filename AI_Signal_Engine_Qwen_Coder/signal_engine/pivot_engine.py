"""
=========================================================
AI SIGNAL ENGINE
Pivot Engine
Version : 10.0 Enterprise
=========================================================

وظایف

• Multi TimeFrame Pivot
• Classic Pivot
• Fibonacci Pivot
• Camarilla
• Woodie
• DeMark

• Trend Detection
• Breakout Detection
• Fake Breakout
• Pullback
• Retest

• Multi TimeFrame Confluence

Supported TimeFrames

1m
3m
5m
15m
30m

1h
2h
4h
6h
8h
12h

1d
2d
3d

1w     <- Aggregated From Daily

1M     <- Aggregated From Daily

=========================================================
"""

from __future__ import annotations

import logging
import threading
import math

from typing import Dict
from typing import Any
from typing import Optional


class PivotEngine:

    """
    Enterprise Pivot Engine
    """

    VERSION = "10.0"

    ENGINE_NAME = "Pivot"

    # -------------------------------------------------

    def __init__(self):

        self.logger = logging.getLogger("PivotEngine")

        self.lock = threading.Lock()

        self.initialized = False

        self.cache = {}

        self.cache_timeout = 60

        self.supported_timeframes = [

            "1m",
            "3m",
            "5m",
            "15m",
            "30m",

            "1h",
            "2h",
            "4h",
            "6h",
            "8h",
            "12h",

            "1d",
            "2d",
            "3d",

            "1w",
            "1M",

        ]

        self.logger.info(

            "Pivot Engine V10 Loaded"

        )

    # -------------------------------------------------

    def initialize(self):

        if self.initialized:

            return

        self.initialized = True

        self.logger.info(

            "Pivot Engine Initialized"

        )

    # -------------------------------------------------

    def shutdown(self):

        self.cache.clear()

        self.initialized = False

        self.logger.info(

            "Pivot Engine Closed"

        )

    # -------------------------------------------------

    def health_check(self):

        return {

            "engine": self.ENGINE_NAME,

            "version": self.VERSION,

            "initialized": self.initialized,

            "cache": len(self.cache),

            "timeframes": len(self.supported_timeframes),

        }

    # -------------------------------------------------

    def validate_input(

        self,

        symbol,

        timeframe,

        data,

    ) -> bool:

        """
        اعتبارسنجی اولیه
        """

        if symbol is None:

            return False

        if timeframe not in self.supported_timeframes:

            self.logger.warning(

                f"Unsupported TimeFrame : {timeframe}"

            )

            return False

        if data is None:

            return False

        if not isinstance(data, dict):

            return False

        if "candles" not in data:

            return False

        candles = data["candles"]

        if not isinstance(candles, list):

            return False

        if len(candles) < 2:

            return False

        required = [

            "open",
            "high",
            "low",
            "close",
            "volume",
            "time",

        ]

        for candle in candles:

            for field in required:

                if field not in candle:

                    return False

        return True
    # -------------------------------------------------
    # Cache
    # -------------------------------------------------

    def _cache_key(

        self,

        symbol,

        timeframe,

    ):

        return f"{symbol}_{timeframe}"

    # -------------------------------------------------

    def _load_cache(

        self,

        key,

    ):

        if key not in self.cache:

            return None

        item = self.cache[key]

        import time

        if (

            time.time()

            -

            item["time"]

            >

            self.cache_timeout

        ):

            del self.cache[key]

            return None

        return item["data"]

    # -------------------------------------------------

    def _save_cache(

        self,

        key,

        data,

    ):

        import time

        self.cache[key] = {

            "time": time.time(),

            "data": data,

        }

    # -------------------------------------------------
    # Prepare Candles
    # -------------------------------------------------

    def _prepare_candles(

        self,

        data,

    ):

        """
        دریافت کندل‌ها از MarketData

        ساختار استاندارد:

        data["candles"]

        """

        candles = data["candles"]

        candles = sorted(

            candles,

            key=lambda x: x["time"]

        )

        cleaned = []

        last_time = None

        for candle in candles:

            if candle["time"] == last_time:

                continue

            cleaned.append(candle)

            last_time = candle["time"]

        return cleaned

    # -------------------------------------------------
    # Previous Candle
    # -------------------------------------------------

    def _previous_candle(

        self,

        candles,

    ):

        """
        کندل بسته شده قبلی

        Pivot همیشه از کندل قبلی محاسبه می‌شود.
        """

        if len(candles) < 2:

            return None

        return candles[-2]

    # -------------------------------------------------
    # Current Candle
    # -------------------------------------------------

    def _current_candle(

        self,

        candles,

    ):

        """
        آخرین کندل
        """

        if len(candles) == 0:

            return None

        return candles[-1]

    # -------------------------------------------------
    # Extract Prices
    # -------------------------------------------------

    def _extract_prices(

        self,

        candle,

    ):

        if candle is None:

            return None

        return {

            "open": float(candle["open"]),

            "high": float(candle["high"]),

            "low": float(candle["low"]),

            "close": float(candle["close"]),

            "volume": float(candle["volume"]),

            "time": candle["time"],

        }

    # -------------------------------------------------
    # Get Previous OHLC
    # -------------------------------------------------

    def _previous_ohlc(

        self,

        data,

    ):

        """
        استخراج OHLC کندل قبلی
        """

        candles = self._prepare_candles(data)

        previous = self._previous_candle(candles)

        return self._extract_prices(previous)

    # -------------------------------------------------
    # Get Current OHLC
    # -------------------------------------------------

    def _current_ohlc(

        self,

        data,

    ):

        candles = self._prepare_candles(data)

        current = self._current_candle(candles)

        return self._extract_prices(current)

    # -------------------------------------------------
    # Candle Count
    # -------------------------------------------------

    def _candle_count(

        self,

        data,

    ):

        return len(

            data["candles"]

        )

    # -------------------------------------------------
    # TimeFrame Validation
    # -------------------------------------------------

    def _validate_timeframe(

        self,

        timeframe,

    ):

        return (

            timeframe

            in

            self.supported_timeframes

        )

    # -------------------------------------------------
    # Cache Wrapper
    # -------------------------------------------------

    def _load_or_prepare(

        self,

        symbol,

        timeframe,

        data,

    ):

        key = self._cache_key(

            symbol,

            timeframe,

        )

        cached = self._load_cache(key)

        if cached is not None:

            return cached

        prepared = self._prepare_candles(data)

        self._save_cache(

            key,

            prepared,

        )

        return prepared
    # -------------------------------------------------
    # Classic Pivot
    # -------------------------------------------------

    def _classic_pivot(self, ohlc):

        h = ohlc["high"]
        l = ohlc["low"]
        c = ohlc["close"]

        pp = (h + l + c) / 3

        r1 = (2 * pp) - l
        s1 = (2 * pp) - h

        r2 = pp + (h - l)
        s2 = pp - (h - l)

        r3 = h + 2 * (pp - l)
        s3 = l - 2 * (h - pp)

        return {

            "PP": round(pp, 8),

            "R1": round(r1, 8),
            "R2": round(r2, 8),
            "R3": round(r3, 8),

            "S1": round(s1, 8),
            "S2": round(s2, 8),
            "S3": round(s3, 8),

        }

    # -------------------------------------------------
    # Fibonacci Pivot
    # -------------------------------------------------

    def _fibonacci_pivot(self, ohlc):

        h = ohlc["high"]
        l = ohlc["low"]
        c = ohlc["close"]

        rng = h - l

        pp = (h + l + c) / 3

        return {

            "PP": round(pp, 8),

            "R1": round(pp + 0.382 * rng, 8),
            "R2": round(pp + 0.618 * rng, 8),
            "R3": round(pp + 1.000 * rng, 8),

            "S1": round(pp - 0.382 * rng, 8),
            "S2": round(pp - 0.618 * rng, 8),
            "S3": round(pp - 1.000 * rng, 8),

        }

    # -------------------------------------------------
    # Woodie Pivot
    # -------------------------------------------------

    def _woodie_pivot(self, ohlc):

        h = ohlc["high"]
        l = ohlc["low"]
        c = ohlc["close"]

        pp = (h + l + (2 * c)) / 4

        r1 = (2 * pp) - l
        s1 = (2 * pp) - h

        r2 = pp + (h - l)
        s2 = pp - (h - l)

        return {

            "PP": round(pp, 8),

            "R1": round(r1, 8),
            "R2": round(r2, 8),

            "S1": round(s1, 8),
            "S2": round(s2, 8),

        }

    # -------------------------------------------------
    # Camarilla Pivot
    # -------------------------------------------------

    def _camarilla_pivot(self, ohlc):

        h = ohlc["high"]
        l = ohlc["low"]
        c = ohlc["close"]

        rng = h - l

        return {

            "R1": round(c + rng * 1.1 / 12, 8),
            "R2": round(c + rng * 1.1 / 6, 8),
            "R3": round(c + rng * 1.1 / 4, 8),
            "R4": round(c + rng * 1.1 / 2, 8),

            "S1": round(c - rng * 1.1 / 12, 8),
            "S2": round(c - rng * 1.1 / 6, 8),
            "S3": round(c - rng * 1.1 / 4, 8),
            "S4": round(c - rng * 1.1 / 2, 8),

        }

    # -------------------------------------------------
    # DeMark Pivot
    # -------------------------------------------------

    def _demark_pivot(self, ohlc):

        h = ohlc["high"]
        l = ohlc["low"]
        c = ohlc["close"]
        o = ohlc["open"]

        if c < o:

            x = h + (2 * l) + c

        elif c > o:

            x = (2 * h) + l + c

        else:

            x = h + l + (2 * c)

        pp = x / 4

        r1 = (x / 2) - l
        s1 = (x / 2) - h

        return {

            "PP": round(pp, 8),

            "R1": round(r1, 8),

            "S1": round(s1, 8),

        }

    # -------------------------------------------------
    # Calculate All Pivot Models
    # -------------------------------------------------

    def _calculate_all_models(self, ohlc):

        return {

            "classic": self._classic_pivot(ohlc),

            "fibonacci": self._fibonacci_pivot(ohlc),

            "woodie": self._woodie_pivot(ohlc),

            "camarilla": self._camarilla_pivot(ohlc),

            "demark": self._demark_pivot(ohlc),

        }
    # -------------------------------------------------
    # Current Price
    # -------------------------------------------------

    def _current_price(

        self,

        candles,

    ):

        if len(candles) == 0:

            return None

        return float(

            candles[-1]["close"]

        )

    # -------------------------------------------------
    # Pivot Trend
    # -------------------------------------------------

    def _detect_trend(

        self,

        price,

        levels,

    ):

        pp = levels["PP"]

        if price > pp:

            return "Bullish"

        if price < pp:

            return "Bearish"

        return "Neutral"

    # -------------------------------------------------
    # Breakout Detection
    # -------------------------------------------------

    def _detect_breakout(

        self,

        price,

        levels,

    ):

        if price > levels["R3"]:

            return "Strong Bull Breakout"

        if price > levels["R2"]:

            return "Bull Breakout"

        if price > levels["R1"]:

            return "Weak Bull Breakout"

        if price < levels["S3"]:

            return "Strong Bear Breakout"

        if price < levels["S2"]:

            return "Bear Breakout"

        if price < levels["S1"]:

            return "Weak Bear Breakout"

        return None

    # -------------------------------------------------
    # Pullback
    # -------------------------------------------------

    def _detect_pullback(

        self,

        candles,

        levels,

    ):

        if len(candles) < 3:

            return False

        last = candles[-1]["close"]

        prev = candles[-2]["close"]

        pp = levels["PP"]

        if prev > pp and last <= pp:

            return True

        if prev < pp and last >= pp:

            return True

        return False

    # -------------------------------------------------
    # Retest
    # -------------------------------------------------

    def _detect_retest(

        self,

        candles,

        levels,

    ):

        if len(candles) < 4:

            return False

        last = candles[-1]["close"]

        pp = levels["PP"]

        distance = abs(

            last - pp

        ) / pp

        return distance < 0.001

    # -------------------------------------------------
    # Fake Breakout
    # -------------------------------------------------

    def _detect_fake_breakout(

        self,

        candles,

        levels,

    ):

        if len(candles) < 3:

            return False

        last = candles[-1]

        prev = candles[-2]

        r1 = levels["R1"]

        s1 = levels["S1"]

        if (

            prev["close"] > r1

            and

            last["close"] < r1

        ):

            return True

        if (

            prev["close"] < s1

            and

            last["close"] > s1

        ):

            return True

        return False

    # -------------------------------------------------
    # Near Pivot
    # -------------------------------------------------

    def _nearest_level(

        self,

        price,

        levels,

    ):

        nearest = None

        distance = 999999999

        for name, value in levels.items():

            d = abs(

                price - value

            )

            if d < distance:

                distance = d

                nearest = name

        return nearest

    # -------------------------------------------------
    # Position
    # -------------------------------------------------

    def _price_position(

        self,

        price,

        levels,

    ):

        if price > levels["R3"]:

            return "Above R3"

        if price > levels["R2"]:

            return "Between R2-R3"

        if price > levels["R1"]:

            return "Between R1-R2"

        if price > levels["PP"]:

            return "Between PP-R1"

        if price > levels["S1"]:

            return "Between S1-PP"

        if price > levels["S2"]:

            return "Between S2-S1"

        if price > levels["S3"]:

            return "Between S3-S2"

        return "Below S3"

    # -------------------------------------------------
    # Analyze Price
    # -------------------------------------------------

    def _price_analysis(

        self,

        candles,

        levels,

    ):

        price = self._current_price(

            candles

        )

        return {

            "price": price,

            "trend":

                self._detect_trend(

                    price,

                    levels,

                ),

            "breakout":

                self._detect_breakout(

                    price,

                    levels,

                ),

            "pullback":

                self._detect_pullback(

                    candles,

                    levels,

                ),

            "retest":

                self._detect_retest(

                    candles,

                    levels,

                ),

            "fake_breakout":

                self._detect_fake_breakout(

                    candles,

                    levels,

                ),

            "nearest":

                self._nearest_level(

                    price,

                    levels,

                ),

            "position":

                self._price_position(

                    price,

                    levels,

                ),

        }
# -------------------------------------------------
# Confluence Distance
# -------------------------------------------------

def _confluence_distance(

    self,

    price1,

    price2,

):

    if price1 == 0:

        return 999

    return abs(

        price1 - price2

    ) / price1


# -------------------------------------------------
# Is Confluence
# -------------------------------------------------

def _is_confluence(

    self,

    level1,

    level2,

    tolerance=0.002,

):

    """
    دو سطح اگر کمتر از 0.2 درصد اختلاف داشته باشند
    Confluence محسوب می‌شوند.
    """

    d = self._confluence_distance(

        level1,

        level2,

    )

    return d <= tolerance


# -------------------------------------------------
# Multi TimeFrame Confluence
# -------------------------------------------------

def _detect_confluence(

    self,

    pivots,

):

    """
    pivots = {

        "1h": {...},

        "4h": {...},

        "1d": {...},

        "1w": {...},

        "1M": {...},

    }

    """

    result = []

    frames = list(

        pivots.keys()

    )

    for i in range(

        len(frames)

    ):

        for j in range(

            i + 1,

            len(frames),

        ):

            tf1 = frames[i]

            tf2 = frames[j]

            p1 = pivots[tf1]["PP"]

            p2 = pivots[tf2]["PP"]

            if self._is_confluence(

                p1,

                p2,

            ):

                result.append({

                    "tf1": tf1,

                    "tf2": tf2,

                    "level": (

                        p1 + p2

                    ) / 2,

                    "type": "PP",

                })

    return result


# -------------------------------------------------
# Strong Confluence
# -------------------------------------------------

def _strong_confluence(

    self,

    confluences,

):

    """
    اگر بیش از 2 Confluence وجود داشته باشد
    منطقه بسیار مهم محسوب می‌شود.
    """

    if len(

        confluences

    ) >= 3:

        return True

    return False


# -------------------------------------------------
# Confluence Score
# -------------------------------------------------

def _confluence_score(

    self,

    confluences,

):

    if len(

        confluences

    ) == 0:

        return 0

    if len(

        confluences

    ) == 1:

        return 10

    if len(

        confluences

    ) == 2:

        return 20

    if len(

        confluences

    ) == 3:

        return 30

    return 40


# -------------------------------------------------
# Nearest Confluence
# -------------------------------------------------

def _nearest_confluence(

    self,

    price,

    confluences,

):

    if len(

        confluences

    ) == 0:

        return None

    nearest = None

    distance = 999999999

    for item in confluences:

        d = abs(

            item["level"]

            - price

        )

        if d < distance:

            distance = d

            nearest = item

    return nearest


# -------------------------------------------------
# Analyze Confluence
# -------------------------------------------------

def _analyze_confluence(

    self,

    price,

    pivots,

):

    confluences = self._detect_confluence(

        pivots

    )

    return {

        "count":

            len(

                confluences

            ),

        "score":

            self._confluence_score(

                confluences

            ),

        "strong":

            self._strong_confluence(

                confluences

            ),

        "nearest":

            self._nearest_confluence(

                price,

                confluences,

            ),

        "zones":

            confluences,

    }
    # -------------------------------------------------
    # Analyze
    # -------------------------------------------------

    def analyze(

        self,

        symbol,

        timeframe,

        data,

    ):

        """
        خروجی کامل Pivot Engine
        """

        if not self.validate_input(

            symbol,

            timeframe,

            data,

        ):

            return None

        candles = self._load_or_prepare(

            symbol,

            timeframe,

            data,

        )

        if len(candles) < 2:

            return None

        previous = self._extract_prices(

            self._previous_candle(

                candles

            )

        )

        if previous is None:

            return None

        models = self._calculate_all_models(

            previous

        )

        price_analysis = {}

        for model_name, levels in models.items():

            price_analysis[model_name] = (

                self._price_analysis(

                    candles,

                    levels,

                )

            )

        result = {

            "engine": self.ENGINE_NAME,

            "version": self.VERSION,

            "symbol": symbol,

            "timeframe": timeframe,

            "time": candles[-1]["time"],

            "pivot_models": models,

            "analysis": price_analysis,

            "status": "OK",

        }

        return result

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------

    def summary(

        self,

        result,

    ):

        if result is None:

            return None

        classic = result["pivot_models"]["classic"]

        analysis = result["analysis"]["classic"]

        return {

            "trend": analysis["trend"],

            "position": analysis["position"],

            "nearest": analysis["nearest"],

            "breakout": analysis["breakout"],

            "pullback": analysis["pullback"],

            "retest": analysis["retest"],

            "fake_breakout": analysis["fake_breakout"],

            "pivot": classic,

        }

    # -------------------------------------------------
    # Clear Cache
    # -------------------------------------------------

    def clear_cache(self):

        self.cache.clear()

    # -------------------------------------------------
    # Version
    # -------------------------------------------------

    @property

    def version(self):

        return self.VERSION

    # -------------------------------------------------
    # Name
    # -------------------------------------------------

    @property

    def name(self):

        return self.ENGINE_NAME

    # -------------------------------------------------
    # String
    # -------------------------------------------------

    def __repr__(self):

        return (

            f"<PivotEngine "

            f"version={self.VERSION}>"

        )
# =====================================================
# Pivot Memory Engine
# =====================================================

class PivotMemory:

    """
    نگهداری تاریخچه Pivotها
    """

    def __init__(self):

        self.memory = {}

        self.max_history = 500

    # -------------------------------------------------

    def _key(

        self,

        symbol,

        timeframe,

    ):

        return f"{symbol}_{timeframe}"

    # -------------------------------------------------

    def save(

        self,

        symbol,

        timeframe,

        pivot,

    ):

        key = self._key(

            symbol,

            timeframe,

        )

        if key not in self.memory:

            self.memory[key] = []

        self.memory[key].append(

            pivot

        )

        if len(

            self.memory[key]

        ) > self.max_history:

            self.memory[key].pop(0)

    # -------------------------------------------------

    def history(

        self,

        symbol,

        timeframe,

    ):

        return self.memory.get(

            self._key(

                symbol,

                timeframe,

            ),

            [],

        )

    # -------------------------------------------------

    def last(

        self,

        symbol,

        timeframe,

    ):

        h = self.history(

            symbol,

            timeframe,

        )

        if len(h) == 0:

            return None

        return h[-1]

    # -------------------------------------------------

    def count(

        self,

        symbol,

        timeframe,

    ):

        return len(

            self.history(

                symbol,

                timeframe,

            )

        )

# =====================================================
# Save Pivot
# =====================================================

def _save_memory(

    self,

    symbol,

    timeframe,

    pivots,

):

    if not hasattr(

        self,

        "memory_engine",

    ):

        self.memory_engine = PivotMemory()

    self.memory_engine.save(

        symbol,

        timeframe,

        {

            "time": int(

                time.time()

            ),

            "pivot": pivots,

        },

    )

# =====================================================
# Load Memory
# =====================================================

def _load_memory(

    self,

    symbol,

    timeframe,

):

    if not hasattr(

        self,

        "memory_engine",

    ):

        self.memory_engine = PivotMemory()

    return self.memory_engine.history(

        symbol,

        timeframe,

    )

# =====================================================
# Pivot Stability
# =====================================================

def _pivot_stability(

    self,

    history,

):

    """
    بررسی ثبات Pivotها
    """

    if len(history) < 5:

        return 0

    values = []

    for item in history:

        values.append(

            item["pivot"]["classic"]["PP"]

        )

    avg = sum(values) / len(values)

    diff = 0

    for v in values:

        diff += abs(

            v - avg

        )

    diff /= len(values)

    if avg == 0:

        return 0

    score = 100 - (

        diff / avg

    ) * 100

    if score < 0:

        score = 0

    if score > 100:

        score = 100

    return round(

        score,

        2,

    )

# =====================================================
# Historical Reaction
# =====================================================

def _historical_reaction(

    self,

    history,

    current_price,

):

    """
    تعداد دفعات برخورد قیمت به Pivot
    """

    touches = 0

    for item in history:

        pp = item["pivot"]["classic"]["PP"]

        if abs(

            current_price - pp

        ) / pp < 0.003:

            touches += 1

    return touches

# =====================================================
# Memory Analyze
# =====================================================

def _memory_analysis(

    self,

    symbol,

    timeframe,

    pivots,

    current_price,

):

    self._save_memory(

        symbol,

        timeframe,

        pivots,

    )

    history = self._load_memory(

        symbol,

        timeframe,

    )

    return {

        "history_count":

            len(history),

        "stability":

            self._pivot_stability(

                history,

            ),

        "touches":

            self._historical_reaction(

                history,

                current_price,

            ),

    }
# =====================================================
# Pivot Zone Strength Engine
# =====================================================

class PivotZoneStrengthEngine:

    """
    تحلیل قدرت نواحی پیوت
    """

    def __init__(self):

        self.touch_distance = 0.002

    # -------------------------------------------------

    def analyze(

        self,

        candles,

        pivots,

    ):

        result = {}

        for name, level in pivots.items():

            result[name] = self._analyze_level(

                candles,

                level,

            )

        return result

    # -------------------------------------------------

    def _analyze_level(

        self,

        candles,

        level,

    ):

        touches = 0

        fake_breaks = 0

        breaks = 0

        rejects = 0

        max_reaction = 0

        for candle in candles:

            high = candle["high"]

            low = candle["low"]

            close = candle["close"]

            open_price = candle["open"]

            # ---------------- Touch

            if (

                abs(high - level) / level

                <= self.touch_distance

                or

                abs(low - level) / level

                <= self.touch_distance

            ):

                touches += 1

            # ---------------- Reject

            if (

                high > level

                and close < level

            ):

                rejects += 1

            if (

                low < level

                and close > level

            ):

                rejects += 1

            # ---------------- Break

            if (

                close > level

                and open_price < level

            ):

                breaks += 1

            if (

                close < level

                and open_price > level

            ):

                breaks += 1

            # ---------------- Fake Break

            if (

                high > level

                and close < level

            ):

                fake_breaks += 1

            if (

                low < level

                and close > level

            ):

                fake_breaks += 1

            reaction = abs(

                close - level

            )

            if reaction > max_reaction:

                max_reaction = reaction

        score = self._score(

            touches,

            rejects,

            breaks,

            fake_breaks,

        )

        return {

            "touches": touches,

            "rejects": rejects,

            "breaks": breaks,

            "fake_breaks": fake_breaks,

            "reaction": round(

                max_reaction,

                8,

            ),

            "score": score,

        }

    # -------------------------------------------------

    def _score(

        self,

        touches,

        rejects,

        breaks,

        fake_breaks,

    ):

        score = 50

        score += touches * 2

        score += rejects * 5

        score -= breaks * 3

        score += fake_breaks * 4

        score = max(

            0,

            min(

                100,

                score,

            ),

        )

        return round(

            score,

            2,

        )
# =====================================================
# Pivot Confluence Engine
# =====================================================

class PivotConfluenceEngine:

    def __init__(self):

        self.tolerance = 0.002

    # -------------------------------------------------

    def analyze(

        self,

        pivot_pack,

    ):

        """
        pivot_pack = {

            "1h": {...},

            "4h": {...},

            "8h": {...},

            "12h": {...},

            "1d": {...},

            "2d": {...},

            "3d": {...},

            "1w": {...},

            "1month": {...}

        }
        """

        zones = []

        frames = list(

            pivot_pack.keys()

        )

        for tf in frames:

            levels = pivot_pack[tf]

            for level_name, level_price in levels.items():

                zones.append({

                    "tf": tf,

                    "name": level_name,

                    "price": level_price,

                })

        clusters = self._cluster(

            zones

        )

        return {

            "zones": clusters,

            "count": len(clusters),

            "strongest":

                self._strongest(

                    clusters

                ),

        }

    # -------------------------------------------------

    def _cluster(

        self,

        zones,

    ):

        result = []

        used = set()

        for i, zone in enumerate(zones):

            if i in used:

                continue

            cluster = [zone]

            used.add(i)

            for j in range(i + 1, len(zones)):

                if j in used:

                    continue

                d = abs(

                    zone["price"]

                    -

                    zones[j]["price"]

                ) / zone["price"]

                if d <= self.tolerance:

                    cluster.append(

                        zones[j]

                    )

                    used.add(j)

            result.append(

                self._cluster_info(

                    cluster

                )

            )

        return result

    # -------------------------------------------------

    def _cluster_info(

        self,

        cluster,

    ):

        avg = sum(

            x["price"]

            for x in cluster

        ) / len(cluster)

        return {

            "price": round(

                avg,

                8,

            ),

            "members": cluster,

            "frames":

                list(

                    set(

                        x["tf"]

                        for x in cluster

                    )

                ),

            "levels":

                [

                    x["name"]

                    for x in cluster

                ],

            "strength":

                len(cluster),

            "score":

                self._score(

                    cluster

                ),

        }

    # -------------------------------------------------

    def _score(

        self,

        cluster,

    ):

        score = 0

        frames = len(

            set(

                x["tf"]

                for x in cluster

            )

        )

        levels = len(cluster)

        score += frames * 15

        score += levels * 5

        return min(

            100,

            score,

        )

    # -------------------------------------------------

    def _strongest(

        self,

        clusters,

    ):

        if len(clusters) == 0:

            return None

        return max(

            clusters,

            key=lambda x: x["score"],

        )
# =====================================================
# Final Pivot Decision Engine
# =====================================================

def _final_score(

    self,

    memory,

    zone_strength,

    confluence,

):

    score = 0

    # ------------------------------------
    # Memory
    # ------------------------------------

    score += memory["stability"] * 0.20

    score += min(

        memory["touches"] * 2,

        20,

    )

    # ------------------------------------
    # Zone Strength
    # ------------------------------------

    total = 0

    count = 0

    for level in zone_strength.values():

        total += level["score"]

        count += 1

    if count:

        score += (

            total / count

        ) * 0.40

    # ------------------------------------
    # Confluence
    # ------------------------------------

    strongest = confluence["strongest"]

    if strongest:

        score += strongest["score"] * 0.40

    return round(

        min(

            score,

            100,

        ),

        2,

    )


# =====================================================
# Final Decision
# =====================================================

def _decision(

    self,

    score,

):

    if score >= 90:

        return "VERY_STRONG"

    if score >= 80:

        return "STRONG"

    if score >= 65:

        return "GOOD"

    if score >= 50:

        return "NORMAL"

    return "WEAK"


# =====================================================
# Risk Level
# =====================================================

def _risk(

    self,

    score,

):

    if score >= 90:

        return "LOW"

    if score >= 75:

        return "MEDIUM"

    return "HIGH"


# =====================================================
# Final Analyze
# =====================================================

def build_final_output(

    self,

    symbol,

    timeframe,

    pivots,

    memory,

    zone_strength,

    confluence,

):

    score = self._final_score(

        memory,

        zone_strength,

        confluence,

    )

    return {

        "engine":

            self.ENGINE_NAME,

        "version":

            self.VERSION,

        "symbol":

            symbol,

        "timeframe":

            timeframe,

        "pivot":

            pivots,

        "memory":

            memory,

        "zone_strength":

            zone_strength,

        "confluence":

            confluence,

        "score":

            score,

        "decision":

            self._decision(

                score,

            ),

        "risk":

            self._risk(

                score,

            ),

    }


# =====================================================
# Public
# =====================================================

def analyze(

    self,

    symbol,

    timeframe,

    candles,

    pivot_pack,

):

    pivots = self._calculate_all_models(

        self._extract_prices(

            self._previous_candle(

                candles,

            )

        )

    )

    price = candles[-1]["close"]

    memory = self._memory_analysis(

        symbol,

        timeframe,

        pivots,

        price,

    )

    zone = self.zone_engine.analyze(

        candles,

        pivots["classic"],

    )

    confluence = self.confluence_engine.analyze(

        pivot_pack,

    )

    return self.build_final_output(

        symbol,

        timeframe,

        pivots,

        memory,

        zone,

        confluence,

    )
    # =====================================================
    # Pivot Strength
    # =====================================================

    def calculate_pivot_strength(
        self,
        pivot: Dict,
        candles: List[Dict],
    ) -> float:
        """
        محاسبه قدرت پیوت
        خروجی:
            0 → 100
        """

        score = 0.0

        if pivot is None:
            return 0.0

        # ---------------------------------------
        # تعداد برخورد
        # ---------------------------------------

        touches = pivot.get("touches", 0)

        if touches >= 5:
            score += 35

        elif touches == 4:
            score += 28

        elif touches == 3:
            score += 20

        elif touches == 2:
            score += 10

        # ---------------------------------------
        # سن پیوت
        # ---------------------------------------

        age = pivot.get("age", 0)

        if age >= 200:
            score += 20

        elif age >= 100:
            score += 15

        elif age >= 50:
            score += 10

        # ---------------------------------------
        # حجم معاملات
        # ---------------------------------------

        volume = pivot.get("volume_score", 0)

        score += min(volume, 15)

        # ---------------------------------------
        # فاصله قیمت فعلی
        # ---------------------------------------

        last = candles[-1]

        distance = abs(

            last["close"] -

            pivot["price"]

        ) / pivot["price"]

        if distance < 0.003:

            score += 20

        elif distance < 0.006:

            score += 12

        elif distance < 0.010:

            score += 5

        # ---------------------------------------
        # شکست قبلی؟
        # ---------------------------------------

        if pivot.get("broken"):

            score -= 25

        # ---------------------------------------

        return max(
            0,
            min(score, 100),
        )
# =====================================================
# Multi TimeFrame Pivot Cluster
# =====================================================

def build_cluster(
    self,
    pivots_by_tf: dict,
):
    """
    ادغام پیوت‌های تایم‌فریم‌های مختلف
    """

    clusters = []

    tolerance = 0.003

    for timeframe, pivots in pivots_by_tf.items():

        for pivot in pivots:

            price = pivot["price"]

            found = False

            for cluster in clusters:

                center = cluster["price"]

                distance = abs(price-center)/center

                if distance <= tolerance:

                    cluster["levels"].append(pivot)

                    cluster["timeframes"].add(timeframe)

                    cluster["touches"] += pivot["touches"]

                    found = True

                    break

            if not found:

                clusters.append({

                    "price": price,

                    "levels": [pivot],

                    "touches": pivot["touches"],

                    "timeframes": {timeframe},

                })

    return clusters
# =====================================================
# Cluster Strength
# =====================================================

def calculate_cluster_strength(
    self,
    cluster,
):

    score = 0

    tf_count = len(cluster["timeframes"])

    touches = cluster["touches"]

    score += min(tf_count*12,50)

    score += min(touches*3,35)

    if tf_count >= 5:

        score += 15

    return min(score,100)
# =====================================================
# Sort Clusters
# =====================================================

def sort_clusters(
    self,
    clusters,
):

    for cluster in clusters:

        cluster["strength"] = self.calculate_cluster_strength(cluster)

    clusters.sort(

        key=lambda x:x["strength"],

        reverse=True,

    )

    return clusters
