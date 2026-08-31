"""
=========================================================
AI Signal Engine
Professional Fibonacci Engine
Version : 2.0
=========================================================
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd


class FibonacciEngine:

    def __init__(self):

        self.logger = logging.getLogger("FibonacciEngine")

        self.lookback = 250

        self.swing_window = 5

        self.levels = [

            0.236,
            0.382,
            0.500,
            0.618,
            0.786,
            0.886,
            1.000,
            1.272,
            1.382,
            1.618,
            2.618

        ]

    # =====================================================
    # Public Analyze
    # =====================================================

    def analyze(

        self,

        symbol,

        timeframe,

        candles

    ):

        if candles is None:

            return None

        if len(candles) < self.lookback:

            return None

        df = pd.DataFrame(candles).copy()

        if df.empty:

            return None

        # استاندارد سازی ستون ها

        df.columns = [

            c.lower()

            for c in df.columns

        ]

        for col in [

            "open",
            "high",
            "low",
            "close"

        ]:

            df[col] = df[col].astype(float)

        # Swing ها

        swing_high = self.find_last_swing_high(df)

        swing_low = self.find_last_swing_low(df)

        if swing_high is None:

            return None

        if swing_low is None:

            return None

        return self.build_fibonacci(

            symbol,

            timeframe,

            df,

            swing_high,

            swing_low

        )

    # =====================================================
    # Last Swing High
    # =====================================================

    def find_last_swing_high(

        self,

        df

    ):

        highs = df["high"].values

        win = self.swing_window

        index = None

        for i in range(

            len(highs) - win - 1,

            win,

            -1

        ):

            left = highs[i-win:i]

            right = highs[i+1:i+win+1]

            current = highs[i]

            if current > left.max():

                if current > right.max():

                    index = i

                    break

        if index is None:

            return None

        return {

            "index": index,

            "price": float(

                highs[index]

            )

        }

    # =====================================================
    # Last Swing Low
    # =====================================================

    def find_last_swing_low(

        self,

        df

    ):

        lows = df["low"].values

        win = self.swing_window

        index = None

        for i in range(

            len(lows)-win-1,

            win,

            -1

        ):

            left = lows[i-win:i]

            right = lows[i+1:i+win+1]

            current = lows[i]

            if current < left.min():

                if current < right.min():

                    index = i

                    break

        if index is None:

            return None

        return {

            "index": index,

            "price": float(

                lows[index]

            )

        }
    # =====================================================
    # Build Fibonacci
    # =====================================================

    def build_fibonacci(

        self,

        symbol,

        timeframe,

        df,

        swing_high,

        swing_low

    ):

        high = swing_high["price"]

        low = swing_low["price"]

        last = float(

            df.iloc[-1]["close"]

        )

        # --------------------------------------------

        # Trend

        # --------------------------------------------

        if swing_low["index"] < swing_high["index"]:

            trend = "UP"

            move = high - low

        else:

            trend = "DOWN"

            move = high - low

        if move <= 0:

            return None

        # --------------------------------------------

        # Fibonacci Levels

        # --------------------------------------------

        fib = {}

        if trend == "UP":

            for level in self.levels:

                if level <= 1:

                    fib[level] = (

                        high -

                        move * level

                    )

                else:

                    fib[level] = (

                        high +

                        move *

                        (level - 1)

                    )

        else:

            for level in self.levels:

                if level <= 1:

                    fib[level] = (

                        low +

                        move * level

                    )

                else:

                    fib[level] = (

                        low -

                        move *

                        (level - 1)

                    )

        # --------------------------------------------

        # نزدیک‌ترین سطح

        # --------------------------------------------

        nearest_level = None

        nearest_price = None

        nearest_distance = 999999999

        for level, price in fib.items():

            d = abs(

                last - price

            )

            if d < nearest_distance:

                nearest_distance = d

                nearest_level = level

                nearest_price = price

        # --------------------------------------------

        # Distance %

        # --------------------------------------------

        distance_percent = (

            nearest_distance /

            last

        ) * 100

        # --------------------------------------------

        # ATR

        # --------------------------------------------

        atr = self.calculate_atr(df)

        # ادامه تحلیل در بخش ۳

        return self.detect_signal(

            symbol=symbol,

            timeframe=timeframe,

            trend=trend,

            last_price=last,

            atr=atr,

            fib_levels=fib,

            nearest_level=nearest_level,

            nearest_price=nearest_price,

            distance_percent=distance_percent

        )

    # =====================================================
    # ATR

    # =====================================================

    def calculate_atr(

        self,

        df,

        period=14

    ):

        high = df["high"]

        low = df["low"]

        close = df["close"]

        tr1 = high - low

        tr2 = (

            high -

            close.shift()

        ).abs()

        tr3 = (

            low -

            close.shift()

        ).abs()

        tr = pd.concat(

            [

                tr1,

                tr2,

                tr3

            ],

            axis=1

        ).max(axis=1)

        atr = tr.rolling(

            period

        ).mean()

        return float(

            atr.iloc[-1]

        )
    # =====================================================
    # Detect Signal
    # =====================================================

    def detect_signal(

        self,

        symbol,

        timeframe,

        trend,

        last_price,

        atr,

        fib_levels,

        nearest_level,

        nearest_price,

        distance_percent

    ):

        score = 40

        confidence = 40

        direction = "NEUTRAL"

        signal_type = "NONE"

        reason = "No Fibonacci Signal"

        # --------------------------------------------
        # نزدیک بودن به سطح
        # --------------------------------------------

        tolerance = max(

            atr,

            last_price * 0.002

        )

        near_level = abs(

            last_price - nearest_price

        ) <= tolerance

        # --------------------------------------------
        # Bounce
        # --------------------------------------------

        if trend == "UP":

            if nearest_level in [

                0.618,

                0.786,

                0.886

            ]:

                if near_level:

                    score += 25

                    confidence += 20

                    direction = "BUY"

                    signal_type = "BOUNCE"

                    reason = (

                        f"Bounce Near {nearest_level}"

                    )

        else:

            if nearest_level in [

                0.618,

                0.786,

                0.886

            ]:

                if near_level:

                    score += 25

                    confidence += 20

                    direction = "SELL"

                    signal_type = "BOUNCE"

                    reason = (

                        f"Bounce Near {nearest_level}"

                    )

        # --------------------------------------------
        # Extension Breakout
        # --------------------------------------------

        if trend == "UP":

            if nearest_level in [

                1.272,

                1.382,

                1.618,

                2.618

            ]:

                if last_price >= nearest_price:

                    score += 20

                    confidence += 15

                    signal_type = "BREAKOUT"

                    direction = "BUY"

                    reason = (

                        f"Extension Breakout {nearest_level}"

                    )

        else:

            if nearest_level in [

                1.272,

                1.382,

                1.618,

                2.618

            ]:

                if last_price <= nearest_price:

                    score += 20

                    confidence += 15

                    signal_type = "BREAKOUT"

                    direction = "SELL"

                    reason = (

                        f"Extension Breakout {nearest_level}"

                    )

        # --------------------------------------------
        # Fake Breakout
        # --------------------------------------------

        if distance_percent < 0.05:

            score += 5

            confidence += 5

        # --------------------------------------------
        # Normalize
        # --------------------------------------------

        score = min(

            int(score),

            100

        )

        confidence = min(

            int(confidence),

            100

        )

        return {

            "engine": "FIBONACCI",

            "symbol": symbol,

            "timeframe": timeframe,

            "trend": trend,

            "direction": direction,

            "signal": signal_type,

            "score": score,

            "confidence": confidence,

            "reason": reason,

            "nearest_level": nearest_level,

            "nearest_price": nearest_price,

            "distance_percent": distance_percent,

            "atr": atr,

            "fib_levels": fib_levels

        }
    # =====================================================
    # Market DNA Update
    # =====================================================

    def update_market_dna(

        self,

        market_dna_engine,

        signal

    ):

        if market_dna_engine is None:

            return

        try:

            market_dna_engine.update(

                symbol=signal["symbol"],

                timeframe=signal["timeframe"],

                score=signal["score"],

                confidence=signal["confidence"],

                direction=signal["direction"],

                metadata={

                    "engine": "FIBONACCI",

                    "nearest_level": signal["nearest_level"],

                    "trend": signal["trend"]

                }

            )

        except Exception:

            self.logger.exception(

                "MarketDNA Update Error"

            )

    # =====================================================
    # Fibonacci Cluster
    # =====================================================

    def detect_cluster(

        self,

        fib_levels,

        current_price,

        tolerance

    ):

        cluster = []

        for level, price in fib_levels.items():

            if abs(

                current_price - price

            ) <= tolerance:

                cluster.append(level)

        return cluster

    # =====================================================
    # Nearest Support
    # =====================================================

    def nearest_support(

        self,

        fib_levels,

        current_price

    ):

        below = [

            p

            for p in fib_levels.values()

            if p <= current_price

        ]

        if not below:

            return None

        return max(below)

    # =====================================================
    # Nearest Resistance
    # =====================================================

    def nearest_resistance(

        self,

        fib_levels,

        current_price

    ):

        above = [

            p

            for p in fib_levels.values()

            if p >= current_price

        ]

        if not above:

            return None

        return min(above)

    # =====================================================
    # Extension Targets
    # =====================================================

    def extension_targets(

        self,

        fib_levels

    ):

        targets = {}

        for level in [

            1.272,

            1.382,

            1.618,

            2.618

        ]:

            if level in fib_levels:

                targets[str(level)] = fib_levels[level]

        return targets

    # =====================================================
    # Health Check
    # =====================================================

    def health_check(self):

        return {

            "engine": "FIBONACCI",

            "status": "OK",

            "levels": len(self.levels),

            "lookback": self.lookback,

            "swing_window": self.swing_window

        }

    # =====================================================
    # Version
    # =====================================================

    @property

    def version(self):

        return "2.0"
