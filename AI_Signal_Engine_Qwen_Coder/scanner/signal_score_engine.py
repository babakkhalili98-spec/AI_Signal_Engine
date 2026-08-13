"""
=========================================================
AI Signal Engine
Signal Score Engine
Version : 3.0
=========================================================
"""

from datetime import datetime


class SignalScoreEngine:

    def __init__(

        self,

        config,

        logger,

        learning_engine,

        market_dna_engine

    ):

        self.config = config

        self.logger = logger

        self.learning = learning_engine

        self.market_dna = market_dna_engine

        # ==============================
        # Base Scores
        # ==============================

        self.base_score = {

            "pivot":20,

            "rsi":15,

            "ichimoku":20,

            "ao":10,

            "candlestick":10,

            "classic":8,

            "harmonic":10,

            "smart_money":20,

            "volume":10,

            "trend":15,

            "fibonacci":12,

            "news":15,

            "market_dna":15,

            "noise":-15

        }

    # =====================================================
    # DYNAMIC WEIGHT
    # =====================================================

    def dynamic_weight(

        self,

        name,

        symbol

    ):

        reliability = self.learning.indicator_success(

            symbol,

            name

        )

        if reliability is None:

            return self.base_score.get(

                name,

                0

            )

        return round(

            self.base_score[name]

            *

            (reliability/100),

            2

        )

    # =====================================================
    # SCORE ITEM
    # =====================================================

    def score_item(

        self,

        symbol,

        name,

        passed

    ):

        if not passed:

            return 0

        return self.dynamic_weight(

            name,

            symbol

        )
    # =====================================================
    # SCORE INDICATORS
    # =====================================================

    def score_indicators(

        self,

        symbol,

        indicator_result

    ):

        total = 0

        details = {}

        for name, result in indicator_result.items():

            passed = result.get(

                "signal",

                False

            )

            score = self.score_item(

                symbol,

                name,

                passed

            )

            details[name] = {

                "passed": passed,

                "score": score,

                "reason": result.get(

                    "reason",

                    ""

                )

            }

            total += score

        return total, details

    # =====================================================
    # SCORE PATTERNS
    # =====================================================

    def score_patterns(

        self,

        symbol,

        pattern_result

    ):

        total = 0

        details = {}

        for name, result in pattern_result.items():

            passed = result.get(

                "signal",

                False

            )

            score = self.score_item(

                symbol,

                name,

                passed

            )

            details[name] = {

                "passed": passed,

                "score": score,

                "reason": result.get(

                    "reason",

                    ""

                )

            }

            total += score

        return total, details

    # =====================================================
    # NEWS SCORE
    # =====================================================

    def score_news(

        self,

        symbol,

        news

    ):

        score = self.score_item(

            symbol,

            "news",

            news.get(

                "signal",

                False

            )

        )

        return score

    # =====================================================
    # MARKET DNA SCORE
    # =====================================================

    def score_market_dna(

        self,

        symbol,

        dna

    ):

        score = self.score_item(

            symbol,

            "market_dna",

            dna.get(

                "signal",

                False

            )

        )

        return score

    # =====================================================
    # NOISE PENALTY
    # =====================================================

    def score_noise(

        self,

        symbol,

        noise

    ):

        if noise.get(

            "high_noise",

            False

        ):

            return self.base_score["noise"]

        return 0
    # =====================================================
    # CALCULATE TOTAL SCORE
    # =====================================================

    def calculate(

        self,

        analysis

    ):

        symbol = analysis["symbol"]

        indicator_score, indicator_details = self.score_indicators(

            symbol,

            analysis["indicator"]

        )

        pattern_score, pattern_details = self.score_patterns(

            symbol,

            analysis["pattern"]

        )

        news_score = self.score_news(

            symbol,

            analysis["news"]

        )

        dna_score = self.score_market_dna(

            symbol,

            analysis["market_dna"]

        )

        noise_penalty = self.score_noise(

            symbol,

            analysis["noise"]

        )

        total = (

            indicator_score

            +

            pattern_score

            +

            news_score

            +

            dna_score

            +

            noise_penalty

        )

        confidence = self.calculate_confidence(

            total

        )

        rank = self.signal_rank(

            confidence

        )

        return {

            "indicator_score": indicator_score,

            "pattern_score": pattern_score,

            "news_score": news_score,

            "market_dna_score": dna_score,

            "noise_penalty": noise_penalty,

            "total": round(total,2),

            "confidence": confidence,

            "rank": rank,

            "details":{

                "indicator":indicator_details,

                "pattern":pattern_details

            }

        }

    # =====================================================
    # CONFIDENCE
    # =====================================================

    def calculate_confidence(

        self,

        score

    ):

        score = max(

            0,

            min(

                score,

                100

            )

        )

        return round(

            score,

            2

        )

    # =====================================================
    # SIGNAL RANK
    # =====================================================

    def signal_rank(

        self,

        confidence

    ):

        if confidence >= 95:

            return "S+"

        elif confidence >= 90:

            return "S"

        elif confidence >= 85:

            return "A+"

        elif confidence >= 80:

            return "A"

        elif confidence >= 70:

            return "B"

        elif confidence >= 60:

            return "C"

        else:

            return "NO TRADE"
    # =====================================================
    # TECHNICAL CONFIDENCE
    # =====================================================

    def technical_confidence(

        self,

        indicator_score,

        pattern_score

    ):

        score = (

            indicator_score * 0.70

            +

            pattern_score * 0.30

        )

        return round(

            min(score,100),

            2

        )

    # =====================================================
    # NEWS CONFIDENCE
    # =====================================================

    def news_confidence(

        self,

        news

    ):

        return news.get(

            "confidence",

            50

        )

    # =====================================================
    # AI CONFIDENCE
    # =====================================================

    def ai_confidence(

        self,

        learning,

        dna

    ):

        learn = learning.get(

            "confidence",

            50

        )

        dna_score = dna.get(

            "confidence",

            50

        )

        return round(

            (learn+dna_score)/2,

            2

        )

    # =====================================================
    # MULTI TIMEFRAME
    # =====================================================

    def timeframe_confidence(

        self,

        analysis

    ):

        return analysis.get(

            "multi_timeframe",

            50

        )

    # =====================================================
    # FINAL CONFIDENCE
    # =====================================================

    def final_confidence(

        self,

        technical,

        news,

        ai,

        timeframe

    ):

        confidence = (

            technical*0.35

            +

            news*0.15

            +

            ai*0.30

            +

            timeframe*0.20

        )

        return round(

            confidence,

            2

        )