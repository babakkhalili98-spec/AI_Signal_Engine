"""
=========================================================
AI Signal Engine
Signal Validator
Version : 1.0
=========================================================
"""


class SignalValidator:

    def __init__(

        self,

        config,

        logger

    ):

        self.config = config

        self.logger = logger

    # =====================================================
    # SCORE
    # =====================================================

    def validate_score(

        self,

        signal

    ):

        score = signal["score"]["confidence"]

        return score >= self.config.MIN_SIGNAL_SCORE

    # =====================================================
    # MAIN INDICATORS
    # =====================================================

    def validate_main_indicators(

        self,

        signal

    ):

        details = signal["score"]["details"]["indicator"]

        passed = 0

        main = [

            "pivot",

            "rsi",

            "ichimoku",

            "ao",

            "candlestick"

        ]

        for name in main:

            if name in details:

                if details[name]["passed"]:

                    passed += 1

        signal["passed_main_indicators"] = passed

        return passed >= self.config.MIN_MAIN_INDICATORS

    # =====================================================
    # RISK REWARD
    # =====================================================

    def validate_rr(

        self,

        signal

    ):

        rr = signal.get(

            "risk_reward",

            0

        )

        return rr >= self.config.MIN_RISK_REWARD

    # =====================================================
    # NEWS
    # =====================================================

    def validate_news(

        self,

        signal

    ):

        news = signal["analysis"]["news"]

        if news.get(

            "block_signal",

            False

        ):

            return False

        return True

    # =====================================================
    # NOISE
    # =====================================================

    def validate_noise(

        self,

        signal

    ):

        noise = signal["analysis"]["noise"]

        if noise.get(

            "high_noise",

            False

        ):

            return False

        return True
    # =====================================================
    # MULTI TIMEFRAME
    # =====================================================

    def validate_timeframes(

        self,

        signal

    ):

        mtf = signal["analysis"].get(

            "multi_timeframe",

            {}

        )

        if not mtf:

            return True

        return mtf.get(

            "confirmed",

            True

        )

    # =====================================================
    # MARKET PHASE
    # =====================================================

    def validate_market_phase(

        self,

        signal

    ):

        phase = signal["analysis"]["market_dna"].get(

            "phase",

            "UNKNOWN"

        )

        blocked = self.config.BLOCK_MARKET_PHASES

        return phase not in blocked

    # =====================================================
    # VOLUME
    # =====================================================

    def validate_volume(

        self,

        signal

    ):

        volume = signal["analysis"]["indicator"].get(

            "volume",

            {}

        )

        return volume.get(

            "confirmed",

            True

        )

    # =====================================================
    # DUPLICATE SIGNAL
    # =====================================================

    def validate_duplicate(

        self,

        signal

    ):

        return True

    # =====================================================
    # ALL VALIDATIONS
    # =====================================================

    def validate(

        self,

        signal

    ):

        checks = {

            "score": self.validate_score(signal),

            "main_indicators": self.validate_main_indicators(signal),

            "risk_reward": self.validate_rr(signal),

            "news": self.validate_news(signal),

            "noise": self.validate_noise(signal),

            "timeframe": self.validate_timeframes(signal),

            "market_phase": self.validate_market_phase(signal),

            "volume": self.validate_volume(signal),

            "duplicate": self.validate_duplicate(signal)

        }

        signal["validation"] = checks

        signal["valid"] = all(

            checks.values()

        )

        if not signal["valid"]:

            signal["direction"] = "NO TRADE"

        return signal

    # =====================================================
    # SUMMARY
    # =====================================================

    def validation_summary(

        self,

        signal

    ):

        return signal.get(

            "validation",

            {}

        )
    # =====================================================
    # RISK / REWARD
    # =====================================================

    def validate_risk_reward(

        self,

        signal

    ):

        rr = signal.get(

            "risk_reward",

            0

        )

        return rr >= self.config.MIN_RISK_REWARD

    # =====================================================
    # TRADE LEVELS
    # =====================================================

    def validate_trade_levels(

        self,

        signal

    ):

        entry = signal.get(

            "entry"

        )

        sl = signal.get(

            "stop_loss"

        )

        tp1 = signal.get(

            "take_profit_1"

        )

        tp2 = signal.get(

            "take_profit_2"

        )

        tp3 = signal.get(

            "take_profit_3"

        )

        direction = signal.get(

            "direction"

        )

        if None in [

            entry,

            sl,

            tp1,

            tp2,

            tp3

        ]:

            return False

        if direction == "BUY":

            if sl >= entry:

                return False

            if tp1 <= entry:

                return False

            if tp2 <= tp1:

                return False

            if tp3 <= tp2:

                return False

        elif direction == "SELL":

            if sl <= entry:

                return False

            if tp1 >= entry:

                return False

            if tp2 >= tp1:

                return False

            if tp3 >= tp2:

                return False

        return True

    # =====================================================
    # MARKET DATA
    # =====================================================

    def validate_market_data(

        self,

        signal

    ):

        analysis = signal.get(

            "analysis",

            {}

        )

        if not analysis:

            return False

        if "indicator" not in analysis:

            return False

        if "pattern" not in analysis:

            return False

        if "news" not in analysis:

            return False

        return True

    # =====================================================
    # DUPLICATE SIGNAL
    # =====================================================

    def validate_duplicate(

        self,

        signal

    ):

        return True
    # =====================================================
    # FINAL VALIDATION
    # =====================================================

    def validate(

        self,

        signal

    ):

        validation = {}

        validation["score"] = self.validate_score(

            signal

        )

        validation["risk_reward"] = self.validate_risk_reward(

            signal

        )

        validation["trade_levels"] = self.validate_trade_levels(

            signal

        )

        validation["market_data"] = self.validate_market_data(

            signal

        )

        validation["duplicate"] = self.validate_duplicate(

            signal

        )

        signal["validation"] = validation

        signal["valid"] = all(

            validation.values()

        )

        return signal

    # =====================================================
    # IS VALID
    # =====================================================

    def is_valid(

        self,

        signal

    ):

        return signal.get(

            "valid",

            False

        )

    # =====================================================
    # VALIDATION REPORT
    # =====================================================

    def validation_report(

        self,

        signal

    ):

        report = {}

        report["valid"] = signal.get(

            "valid",

            False

        )

        report["checks"] = signal.get(

            "validation",

            {}

        )

        return report