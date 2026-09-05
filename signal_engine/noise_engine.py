"""
=========================================================
AI Signal Engine
Noise Engine
Version : 1.0
=========================================================
"""

from __future__ import annotations

import logging
import pandas as pd


class NoiseEngine:

    def __init__(self):

        self.logger = logging.getLogger("NoiseEngine")

    # -------------------------------------------------

    def analyze(

        self,

        symbol,

        timeframe,

        candles

    ):

        if candles is None:

            return None

        if len(candles) < 30:

            return None

        df = pd.DataFrame(candles)

        body = abs(df["close"] - df["open"])

        candle = df["high"] - df["low"]

        avg_body = float(body.tail(20).mean())

        avg_range = float(candle.tail(20).mean())

        noise = 0

        if avg_range > 0:

            noise = 100 * (1 - (avg_body / avg_range))

        noise = max(0, min(noise, 100))

        level = "LOW"

        score = 90

        confidence = 90

        if noise > 70:

            level = "HIGH"

            score = 40

            confidence = 40

        elif noise > 50:

            level = "MEDIUM"

            score = 60

            confidence = 60

        return {

            "engine": "NOISE",

            "score": score,

            "confidence": confidence,

            "direction": "NEUTRAL",

            "reason": f"Noise={noise:.1f}%",

            "level": level

        }