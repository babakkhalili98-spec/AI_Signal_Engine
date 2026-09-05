"""
=========================================================
AI Signal Engine
Market DNA Engine
Version : 1.0
=========================================================
"""

from __future__ import annotations

import logging


class MarketDNAEngine:

    def __init__(self):

        self.logger = logging.getLogger("MarketDNAEngine")

        self.memory = {}

    # --------------------------------------------------

    def update(

        self,

        symbol,

        timeframe,

        score,

        confidence,

        direction

    ):

        if symbol not in self.memory:

            self.memory[symbol] = {}

        if timeframe not in self.memory[symbol]:

            self.memory[symbol][timeframe] = {

                "count": 0,

                "score_sum": 0,

                "confidence_sum": 0,

                "buy": 0,

                "sell": 0

            }

        item = self.memory[symbol][timeframe]

        item["count"] += 1

        item["score_sum"] += score

        item["confidence_sum"] += confidence

        if direction == "BUY":

            item["buy"] += 1

        elif direction == "SELL":

            item["sell"] += 1

    # --------------------------------------------------

    def best_timeframe(

        self,

        symbol

    ):

        if symbol not in self.memory:

            return None

        best = None

        best_score = -1

        for tf, data in self.memory[symbol].items():

            if data["count"] == 0:

                continue

            avg = data["score_sum"] / data["count"]

            if avg > best_score:

                best_score = avg

                best = tf

        return best

    # --------------------------------------------------

    def report(

        self,

        symbol

    ):

        if symbol not in self.memory:

            return {}

        report = {}

        for tf, data in self.memory[symbol].items():

            if data["count"] == 0:

                continue

            report[tf] = {

                "signals": data["count"],

                "avg_score":

                    round(

                        data["score_sum"]

                        /

                        data["count"],

                        2

                    ),

                "avg_confidence":

                    round(

                        data["confidence_sum"]

                        /

                        data["count"],

                        2

                    ),

                "buy": data["buy"],

                "sell": data["sell"]

            }

        return report

    # --------------------------------------------------

    def analyze(

        self,

        symbol,

        timeframe,

        candles=None

    ):

        best = self.best_timeframe(symbol)

        if best is None:

            return {

                "engine": "MARKET_DNA",

                "score": 50,

                "confidence": 50,

                "direction": "NEUTRAL",

                "reason": "DNA Not Ready",

                "dna": {}

            }

        report = self.report(symbol)

        avg = report[best]["avg_score"]

        return {

            "engine": "MARKET_DNA",

            "score": avg,

            "confidence": report[best]["avg_confidence"],

            "direction": "NEUTRAL",

            "reason": f"Best TF = {best}",

            "dna": report

        }