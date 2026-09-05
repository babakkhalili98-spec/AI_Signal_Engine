"""
=========================================================
AI Signal Engine
Harmonic Engine
Version : 1.0
=========================================================
"""

from __future__ import annotations

import logging
import pandas as pd


class HarmonicEngine:

    def __init__(self):

        self.logger = logging.getLogger("HarmonicEngine")

    # -----------------------------------------------------

    def analyze(

        self,

        symbol,

        timeframe,

        candles

    ):

        if candles is None:

            return None

        if len(candles) < 100:

            return None

        df = pd.DataFrame(candles)

        close = df["close"]

        last = float(close.iloc[-1])

        high = float(df["high"].tail(50).max())

        low = float(df["low"].tail(50).min())

        score = 50
        confidence = 50
        direction = "NEUTRAL"
        reason = "No Harmonic Pattern"

        # ----------------------------------------
        # موقعیت تقریبی قیمت در موج
        # ----------------------------------------

        rng = high - low

        if rng <= 0:

            return None

        position = (last - low) / rng

        if position < 0.15:

            score = 75
            confidence = 70
            direction = "BUY"
            reason = "Potential Harmonic Reversal Zone"

        elif position > 0.85:

            score = 75
            confidence = 70
            direction = "SELL"
            reason = "Potential Harmonic Completion"

        return {

            "engine": "HARMONIC",

            "score": score,

            "confidence": confidence,

            "direction": direction,

            "reason": reason,

            "position": round(position, 3)

        }