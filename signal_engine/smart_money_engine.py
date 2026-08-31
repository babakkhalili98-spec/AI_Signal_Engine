"""
=========================================================
AI Signal Engine
Smart Money Engine
Version : 1.0
=========================================================
"""

from __future__ import annotations

import logging
import pandas as pd


class SmartMoneyEngine:

    def __init__(self):

        self.logger = logging.getLogger("SmartMoneyEngine")

    # -----------------------------------------------------

    def analyze(

        self,

        symbol,

        timeframe,

        candles

    ):

        if candles is None:

            return None

        if len(candles) < 50:

            return None

        df = pd.DataFrame(candles)

        last = df.iloc[-1]

        last_close = float(last["close"])

        last_high = float(last["high"])

        last_low = float(last["low"])

        recent_high = float(df["high"].tail(20).max())

        recent_low = float(df["low"].tail(20).min())

        score = 50
        confidence = 50
        direction = "NEUTRAL"
        reason = "No Smart Money Signal"

        # ------------------------------------------
        # Break Of Structure
        # ------------------------------------------

        if last_close >= recent_high:

            score = 85
            confidence = 80
            direction = "BUY"
            reason = "Bullish Break Of Structure"

        elif last_close <= recent_low:

            score = 85
            confidence = 80
            direction = "SELL"
            reason = "Bearish Break Of Structure"

        # ------------------------------------------
        # Fake Break
        # ------------------------------------------

        elif last_high > recent_high and last_close < recent_high:

            score = 75
            confidence = 70
            direction = "SELL"
            reason = "Liquidity Grab Above High"

        elif last_low < recent_low and last_close > recent_low:

            score = 75
            confidence = 70
            direction = "BUY"
            reason = "Liquidity Grab Below Low"

        return {

            "engine": "SMART_MONEY",

            "score": score,

            "confidence": confidence,

            "direction": direction,

            "reason": reason,

            "recent_high": recent_high,

            "recent_low": recent_low

        }