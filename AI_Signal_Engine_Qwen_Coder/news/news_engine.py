"""
=========================================================
AI Signal Engine
News Engine
Version : 1.0
=========================================================
"""

from __future__ import annotations

import logging
from datetime import datetime


class NewsEngine:

    def __init__(self):

        self.logger = logging.getLogger("NewsEngine")

        self.news_cache = []

    # --------------------------------------------------

    def load_news(self):

        """
        در نسخه‌های بعدی:
        ForexFactory
        Investing
        TradingEconomics
        API News
        """

        return self.news_cache

    # --------------------------------------------------

    def analyze(

        self,

        symbol,

        timeframe

    ):

        news = self.load_news()

        if len(news) == 0:

            return {

                "engine": "NEWS",

                "score": 80,

                "confidence": 80,

                "direction": "NEUTRAL",

                "reason": "No Important News",

                "effect": "NONE",

                "description": ""

            }

        red_news = 0
        orange_news = 0

        for item in news:

            impact = item.get("impact", "").lower()

            if impact == "red":

                red_news += 1

            elif impact == "orange":

                orange_news += 1

        if red_news > 0:

            return {

                "engine": "NEWS",

                "score": 20,

                "confidence": 95,

                "direction": "NEUTRAL",

                "reason": "High Impact News",

                "effect": "RED",

                "description": f"{red_news} Red News"

            }

        if orange_news > 0:

            return {

                "engine": "NEWS",

                "score": 55,

                "confidence": 80,

                "direction": "NEUTRAL",

                "reason": "Medium Impact News",

                "effect": "ORANGE",

                "description": f"{orange_news} Orange News"

            }

        return {

            "engine": "NEWS",

            "score": 80,

            "confidence": 80,

            "direction": "NEUTRAL",

            "reason": "News Normal",

            "effect": "NONE",

            "description": ""

        }

    # --------------------------------------------------

    def update_news(

        self,

        news_list

    ):

        self.news_cache = news_list

    # --------------------------------------------------

    def clear(self):

        self.news_cache = []

    # --------------------------------------------------

    def status(self):

        return {

            "cached_news": len(self.news_cache),

            "updated": datetime.now().isoformat()

        }