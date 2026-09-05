"""
=========================================================
AI Signal Engine
Candlestick Engine
Version : 1.0
=========================================================
"""

from __future__ import annotations

import logging
import pandas as pd


class CandlestickEngine:

    def __init__(self):

        self.logger = logging.getLogger("CandlestickEngine")

    # -----------------------------------------------------

    def analyze(

        self,

        symbol,

        timeframe,

        candles

    ):

        if candles is None:

            return None

        if len(candles) < 5:

            return None

        df = pd.DataFrame(candles)

        last = df.iloc[-1]

        prev = df.iloc[-2]

        open_price = float(last["open"])
        close_price = float(last["close"])
        high = float(last["high"])
        low = float(last["low"])

        body = abs(close_price - open_price)

        upper_shadow = high - max(open_price, close_price)

        lower_shadow = min(open_price, close_price) - low

        score = 50

        confidence = 50

        direction = "NEUTRAL"

        reason = "No Pattern"

        # ==========================================
        # Hammer
        # ==========================================

        if (

            lower_shadow > body * 2

            and

            upper_shadow < body

        ):

            score = 85

            confidence = 85

            direction = "BUY"

            reason = "Hammer"

        # ==========================================
        # Shooting Star
        # ==========================================

        elif (

            upper_shadow > body * 2

            and

            lower_shadow < body

        ):

            score = 85

            confidence = 85

            direction = "SELL"

            reason = "Shooting Star"

        # ==========================================
        # Bullish Engulfing
        # ==========================================

        elif (

            prev["close"] < prev["open"]

            and

            close_price > open_price

            and

            close_price > prev["open"]

            and

            open_price < prev["close"]

        ):

            score = 90

            confidence = 90

            direction = "BUY"

            reason = "Bullish Engulfing"

        # ==========================================
        # Bearish Engulfing
        # ==========================================

        elif (

            prev["close"] > prev["open"]

            and

            close_price < open_price

            and

            close_price < prev["open"]

            and

            open_price > prev["close"]

        ):

            score = 90

            confidence = 90

            direction = "SELL"

            reason = "Bearish Engulfing"

        return {

            "engine": "CANDLE",

            "score": score,

            "confidence": confidence,

            "direction": direction,

            "reason": reason,

        }