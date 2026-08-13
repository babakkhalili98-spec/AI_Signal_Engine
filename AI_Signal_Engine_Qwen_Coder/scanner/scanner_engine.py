"""
=========================================================
AI Signal Engine
Scanner Engine
Version : 3.0
=========================================================
"""

from datetime import datetime


class ScannerEngine:

    def __init__(

        self,

        config,

        logger,

        market_data,

        learning_engine,

        news_engine,

        pivot_engine,

        rsi_engine,

        ichimoku_engine,

        ao_engine,

        candlestick_engine,

        harmonic_engine,

        classic_pattern_engine,

        smart_money_engine,

        volume_engine,

        fibonacci_engine,

        trend_engine,

        market_dna_engine,

        noise_filter,

        signal_score_engine,

        signal_validator,

        signal_formatter,

        report_engine

    ):

        self.config = config

        self.logger = logger

        self.market_data = market_data

        self.learning_engine = learning_engine

        self.news_engine = news_engine

        self.pivot_engine = pivot_engine

        self.rsi_engine = rsi_engine

        self.ichimoku_engine = ichimoku_engine

        self.ao_engine = ao_engine

        self.candlestick_engine = candlestick_engine

        self.harmonic_engine = harmonic_engine

        self.classic_pattern_engine = classic_pattern_engine

        self.smart_money_engine = smart_money_engine

        self.volume_engine = volume_engine

        self.fibonacci_engine = fibonacci_engine

        self.trend_engine = trend_engine

        self.market_dna_engine = market_dna_engine

        self.noise_filter = noise_filter

        self.signal_score_engine = signal_score_engine

        self.signal_validator = signal_validator

        self.signal_formatter = signal_formatter

        self.report_engine = report_engine

    # =====================================================
    # LOAD MARKET
    # =====================================================

    def load_market(

        self,

        symbol,

        timeframe

    ):

        return self.market_data.load(

            symbol,

            timeframe

        )

    # =====================================================
    # START SCAN
    # =====================================================

    def start_scan(

        self,

        symbol,

        timeframe

    ):

        market = self.load_market(

            symbol,

            timeframe

        )

        context = {

            "symbol": symbol,

            "timeframe": timeframe,

            "market": market,

            "time": datetime.utcnow()

        }

        return context

    # =====================================================
    # CHECK DATA
    # =====================================================

    def validate_market(

        self,

        context

    ):

        if context["market"] is None:

            return False

        if len(

            context["market"]

        ) < 200:

            return False

        return True

    # =====================================================
    # HEARTBEAT
    # =====================================================

    def heartbeat(self):

        self.logger.info(

            "Scanner Engine Ready"

        )
    # =====================================================
    # INDICATOR ANALYSIS
    # =====================================================

    def indicator_scan(
        self,
        context
    ):

        market = context["market"]

        result = {}

        result["pivot"] = self.pivot_engine.analyze(market)

        result["rsi"] = self.rsi_engine.analyze(market)

        result["ichimoku"] = self.ichimoku_engine.analyze(market)

        result["ao"] = self.ao_engine.analyze(market)

        result["fibonacci"] = self.fibonacci_engine.analyze(market)

        result["trend"] = self.trend_engine.analyze(market)

        result["volume"] = self.volume_engine.analyze(market)

        return result

    # =====================================================
    # PATTERN ANALYSIS
    # =====================================================

    def pattern_scan(
        self,
        context
    ):

        market = context["market"]

        result = {}

        result["candlestick"] = self.candlestick_engine.analyze(market)

        result["classic"] = self.classic_pattern_engine.analyze(market)

        result["harmonic"] = self.harmonic_engine.analyze(market)

        result["smart_money"] = self.smart_money_engine.analyze(market)

        return result

    # =====================================================
    # NEWS ANALYSIS
    # =====================================================

    def news_scan(
        self,
        context
    ):

        return self.news_engine.analyze(

            context["symbol"]

        )

    # =====================================================
    # MARKET DNA
    # =====================================================

    def market_dna_scan(
        self,
        context
    ):

        return self.market_dna_engine.analyze(

            context["symbol"]

        )

    # =====================================================
    # LEARNING
    # =====================================================

    def learning_scan(
        self,
        context
    ):

        return self.learning_engine.ai_decision(

            context

        )

    # =====================================================
    # NOISE FILTER
    # =====================================================

    def noise_scan(
        self,
        context
    ):

        return self.noise_filter.analyze(

            context

        )

    # =====================================================
    # BUILD ANALYSIS
    # =====================================================

    def analyze(
        self,
        context
    ):

        analysis = {}

        analysis["indicator"] = self.indicator_scan(

            context

        )

        analysis["pattern"] = self.pattern_scan(

            context

        )

        analysis["news"] = self.news_scan(

            context

        )

        analysis["market_dna"] = self.market_dna_scan(

            context

        )

        analysis["learning"] = self.learning_scan(

            context

        )

        analysis["noise"] = self.noise_scan(

            context

        )

        return analysis
    # =====================================================
    # SCORE SIGNAL
    # =====================================================

    def score_signal(
        self,
        analysis
    ):

        return self.signal_score_engine.calculate(

            analysis

        )

    # =====================================================
    # VALIDATE SIGNAL
    # =====================================================

    def validate_signal(
        self,
        signal
    ):

        return self.signal_validator.validate(

            signal

        )

    # =====================================================
    # BUILD SIGNAL
    # =====================================================

    def build_signal(
        self,
        context,
        analysis,
        score
    ):

        signal = {

            "symbol": context["symbol"],

            "timeframe": context["timeframe"],

            "time": context["time"],

            "analysis": analysis,

            "score": score,

            "entry": None,

            "stop_loss": None,

            "take_profit_1": None,

            "take_profit_2": None,

            "take_profit_3": None,

            "direction": "NO TRADE",

            "confidence": 0,

            "risk": "UNKNOWN",

            "reasons": []

        }

        return signal

    # =====================================================
    # DECISION
    # =====================================================

    def decision(
        self,
        signal
    ):

        score = signal["score"]["total"]

        if score >= self.config.BUY_SCORE:

            signal["direction"] = "BUY"

        elif score <= self.config.SELL_SCORE:

            signal["direction"] = "SELL"

        else:

            signal["direction"] = "NO TRADE"

        signal["confidence"] = score

        return signal

    # =====================================================
    # FILTER
    # =====================================================

    def final_filter(
        self,
        signal
    ):

        return self.validate_signal(

            signal

        )

    # =====================================================
    # GENERATE SIGNAL
    # =====================================================

    def generate_signal(
        self,
        context
    ):

        analysis = self.analyze(

            context

        )

        score = self.score_signal(

            analysis

        )

        signal = self.build_signal(

            context,

            analysis,

            score

        )

        signal = self.decision(

            signal

        )

        signal = self.final_filter(

            signal

        )

        return signal
    # =====================================================
    # CALCULATE ENTRY / SL / TP
    # =====================================================

    def calculate_trade_levels(
        self,
        signal
    ):

        levels = self.signal_score_engine.calculate_trade_levels(
            signal
        )

        signal["entry"] = levels["entry"]
        signal["stop_loss"] = levels["stop_loss"]

        signal["take_profit_1"] = levels["tp1"]
        signal["take_profit_2"] = levels["tp2"]
        signal["take_profit_3"] = levels["tp3"]

        signal["risk_reward"] = levels["rr"]

        return signal

    # =====================================================
    # ADD REASONS
    # =====================================================

    def add_reasons(
        self,
        signal
    ):

        reasons = []

        analysis = signal["analysis"]

        reasons.extend(
            analysis["indicator"].get("reasons", [])
        )

        reasons.extend(
            analysis["pattern"].get("reasons", [])
        )

        reasons.extend(
            analysis["news"].get("reasons", [])
        )

        reasons.extend(
            analysis["market_dna"].get("reasons", [])
        )

        signal["reasons"] = reasons

        return signal

    # =====================================================
    # ADD WARNINGS
    # =====================================================

    def add_warnings(
        self,
        signal
    ):

        warnings = []

        analysis = signal["analysis"]

        if analysis["noise"].get("high_noise"):

            warnings.append(
                "بازار دارای نویز بالا است."
            )

        if analysis["news"].get("active_red_news"):

            warnings.append(
                "خبر قرمز آمریکا هنوز بر بازار اثرگذار است."
            )

        if analysis["market_dna"].get("low_confidence"):

            warnings.append(
                "Market DNA اعتماد پایینی به این شرایط دارد."
            )

        signal["warnings"] = warnings

        return signal

    # =====================================================
    # FINAL QUALITY
    # =====================================================

    def final_quality(
        self,
        signal
    ):

        signal["quality"] = self.learning_engine.quality_score(
            signal
        )

        return signal

    # =====================================================
    # FORMAT SIGNAL
    # =====================================================

    def format_signal(
        self,
        signal
    ):

        return self.signal_formatter.format(
            signal
        )

    # =====================================================
    # BUILD REPORT
    # =====================================================

    def build_report(
        self,
        signal
    ):

        return self.report_engine.build(
            signal
        )

    # =====================================================
    # COMPLETE SIGNAL
    # =====================================================

    def complete_signal(
        self,
        signal
    ):

        signal = self.calculate_trade_levels(signal)

        signal = self.add_reasons(signal)

        signal = self.add_warnings(signal)

        signal = self.final_quality(signal)

        return signal
    # =====================================================
    # SAVE LEARNING
    # =====================================================

    def save_learning(
        self,
        signal
    ):

        self.learning_engine.register_signal(

            signal

        )

    # =====================================================
    # SAVE MARKET DNA
    # =====================================================

    def save_market_dna(
        self,
        signal
    ):

        self.market_dna_engine.update(

            signal

        )

    # =====================================================
    # LOG SIGNAL
    # =====================================================

    def log_signal(
        self,
        signal
    ):

        self.logger.info(

            f"{signal['symbol']} | "

            f"{signal['direction']} | "

            f"Score:{signal['score']['total']}"

        )

    # =====================================================
    # FINAL SCAN
    # =====================================================

    def scan(

        self,

        symbol,

        timeframe

    ):

        context = self.start_scan(

            symbol,

            timeframe

        )

        if not self.validate_market(

            context

        ):

            return None

        signal = self.generate_signal(

            context

        )

        signal = self.complete_signal(

            signal

        )

        report = self.build_report(

            signal

        )

        self.save_learning(

            signal

        )

        self.save_market_dna(

            signal

        )

        self.log_signal(

            signal

        )

        return report

    # =====================================================
    # MULTI SYMBOL SCAN
    # =====================================================

    def scan_all(

        self,

        symbols,

        timeframe

    ):

        reports = []

        for symbol in symbols:

            try:

                report = self.scan(

                    symbol,

                    timeframe

                )

                if report:

                    reports.append(

                        report

                    )

            except Exception as e:

                self.logger.exception(e)

        reports.sort(

            key=lambda x:

            x["score"],

            reverse=True

        )

        return reports

    # =====================================================
    # BEST SIGNAL
    # =====================================================

    def best_signal(

        self,

        reports

    ):

        if len(

            reports

        ) == 0:

            return None

        return reports[0]