"""
=========================================================
AI Signal Engine
Learning Engine
Version : 2.0
=========================================================
"""

from datetime import datetime


class LearningEngine:

    def __init__(
        self,
        database,
        logger,
        config
    ):

        self.database = database

        self.logger = logger

        self.config = config

        self.trade_memory = []

        self.signal_memory = []

        self.market_memory = []

        self.news_memory = []

        self.pattern_memory = []

    # =====================================================
    # REGISTER TRADE
    # =====================================================

    def register_trade(
        self,
        position
    ):

        trade = {

            "symbol": position["symbol"],

            "side": position["side"],

            "entry": position["entry_price"],

            "stop_loss": position["stop_loss"],

            "tp1": position["take_profit_1"],

            "tp2": position["take_profit_2"],

            "tp3": position["take_profit_3"],

            "signal_score": position["signal_score"],

            "risk_score": position["risk_score"],

            "open_time": position["open_time"]

        }

        self.trade_memory.append(

            trade

        )

        return trade

    # =====================================================
    # REGISTER SIGNAL
    # =====================================================

    def register_signal(
        self,
        signal
    ):

        self.signal_memory.append(

            signal

        )

    # =====================================================
    # REGISTER MARKET
    # =====================================================

    def register_market(
        self,
        market_snapshot
    ):

        self.market_memory.append(

            market_snapshot

        )

    # =====================================================
    # REGISTER NEWS
    # =====================================================

    def register_news(
        self,
        news
    ):

        self.news_memory.append(

            news

        )

    # =====================================================
    # REGISTER PATTERN
    # =====================================================

    def register_pattern(
        self,
        pattern
    ):

        self.pattern_memory.append(

            pattern

        )

    # =====================================================
    # SAVE DATABASE
    # =====================================================

    def save_trade(
        self,
        trade
    ):

        try:

            self.database.save_learning_trade(

                trade

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # AFTER OPEN
    # =====================================================

    def after_open(
        self,
        position
    ):

        trade = self.register_trade(

            position

        )

        self.save_trade(

            trade

        )

    # =====================================================
    # HEARTBEAT
    # =====================================================

    def heartbeat(self):

        self.logger.info(

            f"Learning | "

            f"Trades:{len(self.trade_memory)} "

            f"Signals:{len(self.signal_memory)} "

            f"Markets:{len(self.market_memory)} "

            f"News:{len(self.news_memory)}"

        )
    # =====================================================
    # MARKET DNA
    # =====================================================

    def register_market_dna(
        self,
        symbol,
        dna
    ):

        try:

            self.database.save_market_dna(

                symbol,

                dna

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # LOAD MARKET DNA
    # =====================================================

    def load_market_dna(
        self,
        symbol
    ):

        try:

            return self.database.load_market_dna(

                symbol

            )

        except Exception as e:

            self.logger.exception(e)

            return None

    # =====================================================
    # PATTERN MEMORY
    # =====================================================

    def remember_pattern(

        self,

        symbol,

        pattern,

        result

    ):

        data = {

            "symbol": symbol,

            "pattern": pattern,

            "result": result,

            "time": datetime.utcnow()

        }

        self.pattern_memory.append(

            data

        )

        try:

            self.database.save_pattern_memory(

                data

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # NEWS MEMORY
    # =====================================================

    def remember_news(

        self,

        news

    ):

        self.news_memory.append(

            news

        )

        try:

            self.database.save_news_memory(

                news

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # CURRENCY MEMORY
    # =====================================================

    def remember_currency(

        self,

        symbol,

        data

    ):

        try:

            self.database.save_currency_memory(

                symbol,

                data

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # LOAD CURRENCY MEMORY
    # =====================================================

    def load_currency_memory(

        self,

        symbol

    ):

        try:

            return self.database.load_currency_memory(

                symbol

            )

        except Exception as e:

            self.logger.exception(e)

            return None

    # =====================================================
    # LAST PATTERN
    # =====================================================

    def last_pattern(

        self,

        symbol

    ):

        for pattern in reversed(

            self.pattern_memory

        ):

            if pattern["symbol"] == symbol:

                return pattern

        return None

    # =====================================================
    # LAST NEWS
    # =====================================================

    def last_news(self):

        if len(

            self.news_memory

        ) == 0:

            return None

        return self.news_memory[-1]

    # =====================================================
    # MEMORY STATUS
    # =====================================================

    def memory_status(self):

        return {

            "trades": len(

                self.trade_memory

            ),

            "patterns": len(

                self.pattern_memory

            ),

            "news": len(

                self.news_memory

            ),

            "market": len(

                self.market_memory

            )

        }
    # =====================================================
    # WIN RATE
    # =====================================================

    def win_rate(
        self,
        symbol=None
    ):

        trades = self.database.closed_trades(symbol)

        if not trades:

            return 0

        wins = sum(

            1

            for trade in trades

            if trade["profit"] > 0

        )

        return round(

            wins / len(trades) * 100,

            2

        )

    # =====================================================
    # LOSS RATE
    # =====================================================

    def loss_rate(
        self,
        symbol=None
    ):

        return round(

            100 - self.win_rate(symbol),

            2

        )

    # =====================================================
    # AVERAGE PROFIT
    # =====================================================

    def average_profit(
        self,
        symbol=None
    ):

        trades = self.database.closed_trades(symbol)

        profits = [

            t["profit"]

            for t in trades

            if t["profit"] > 0

        ]

        if not profits:

            return 0

        return round(

            sum(profits) / len(profits),

            2

        )

    # =====================================================
    # AVERAGE LOSS
    # =====================================================

    def average_loss(
        self,
        symbol=None
    ):

        trades = self.database.closed_trades(symbol)

        losses = [

            abs(t["profit"])

            for t in trades

            if t["profit"] < 0

        ]

        if not losses:

            return 0

        return round(

            sum(losses) / len(losses),

            2

        )

    # =====================================================
    # PROFIT FACTOR
    # =====================================================

    def profit_factor(
        self,
        symbol=None
    ):

        trades = self.database.closed_trades(symbol)

        gross_profit = sum(

            t["profit"]

            for t in trades

            if t["profit"] > 0

        )

        gross_loss = abs(

            sum(

                t["profit"]

                for t in trades

                if t["profit"] < 0

            )

        )

        if gross_loss == 0:

            return 999

        return round(

            gross_profit / gross_loss,

            2

        )

    # =====================================================
    # CONFIDENCE SCORE
    # =====================================================

    def confidence_score(
        self,
        symbol=None
    ):

        wr = self.win_rate(symbol)

        pf = self.profit_factor(symbol)

        score = wr * 0.6 + min(pf, 5) * 8

        return round(

            min(score, 100),

            2

        )

    # =====================================================
    # QUALITY SCORE
    # =====================================================

    def quality_score(
        self,
        signal
    ):

        score = signal.signal_score

        score += self.confidence_score(

            signal.symbol

        ) * 0.20

        return round(

            min(score, 100),

            2

        )

    # =====================================================
    # SYMBOL REPORT
    # =====================================================

    def symbol_statistics(
        self,
        symbol
    ):

        return {

            "symbol": symbol,

            "win_rate": self.win_rate(symbol),

            "loss_rate": self.loss_rate(symbol),

            "average_profit": self.average_profit(symbol),

            "average_loss": self.average_loss(symbol),

            "profit_factor": self.profit_factor(symbol),

            "confidence": self.confidence_score(symbol)

        }

    # =====================================================
    # GLOBAL REPORT
    # =====================================================

    def global_statistics(self):

        return {

            "win_rate": self.win_rate(),

            "loss_rate": self.loss_rate(),

            "profit_factor": self.profit_factor(),

            "confidence": self.confidence_score()

        }
    # =====================================================
    # BEST TIMEFRAME
    # =====================================================

    def best_timeframe(self, symbol):

        return self.database.best_timeframe(symbol)

    # =====================================================
    # BEST SESSION
    # =====================================================

    def best_session(self, symbol):

        return self.database.best_session(symbol)

    # =====================================================
    # BEST INDICATORS
    # =====================================================

    def best_indicators(self, symbol):

        return self.database.best_indicators(symbol)

    # =====================================================
    # OPTIMIZE STOP LOSS
    # =====================================================

    def optimize_stop_loss(self, symbol):

        value = self.database.average_stop_loss(symbol)

        if value is None:

            return None

        return round(value, 2)

    # =====================================================
    # OPTIMIZE TAKE PROFIT
    # =====================================================

    def optimize_take_profit(self, symbol):

        value = self.database.average_take_profit(symbol)

        if value is None:

            return None

        return round(value, 2)

    # =====================================================
    # OPTIMIZE POSITION SIZE
    # =====================================================

    def optimize_position_size(self, symbol):

        value = self.database.best_position_size(symbol)

        if value is None:

            return self.config.RISK_PER_TRADE

        return value

    # =====================================================
    # MARKET CONDITION
    # =====================================================

    def best_market_condition(self, symbol):

        return self.database.best_market_condition(symbol)

    # =====================================================
    # NEWS IMPACT
    # =====================================================

    def news_impact(self, symbol):

        return self.database.news_statistics(symbol)

    # =====================================================
    # BUILD OPTIMIZATION
    # =====================================================

    def optimization_report(self, symbol):

        return {

            "symbol": symbol,

            "timeframe": self.best_timeframe(symbol),

            "session": self.best_session(symbol),

            "indicators": self.best_indicators(symbol),

            "stop_loss": self.optimize_stop_loss(symbol),

            "take_profit": self.optimize_take_profit(symbol),

            "position_size": self.optimize_position_size(symbol),

            "market_condition": self.best_market_condition(symbol),

            "news": self.news_impact(symbol)

        }

    # =====================================================
    # APPLY OPTIMIZATION
    # =====================================================

    def apply_optimization(self, signal):

        report = self.optimization_report(

            signal.symbol

        )

        if report["stop_loss"]:

            signal.stop_loss = report["stop_loss"]

        if report["take_profit"]:

            signal.take_profit_1 = report["take_profit"]

        return signal

    # =====================================================
    # AUTO UPDATE
    # =====================================================

    def auto_update(self):

        self.logger.info(

            "Learning Engine Updated"

        )
    # =====================================================
    # SCANNER FEEDBACK
    # =====================================================

    def scanner_feedback(
        self,
        symbol
    ):

        return {

            "confidence_score": self.confidence_score(symbol),

            "quality_score": self.symbol_statistics(symbol)["confidence"],

            "optimization": self.optimization_report(symbol)

        }

    # =====================================================
    # RISK FEEDBACK
    # =====================================================

    def risk_feedback(
        self,
        symbol
    ):

        report = self.optimization_report(symbol)

        return {

            "recommended_position_size":
                report["position_size"],

            "recommended_stop_loss":
                report["stop_loss"],

            "recommended_take_profit":
                report["take_profit"]

        }

    # =====================================================
    # POSITION FEEDBACK
    # =====================================================

    def position_feedback(
        self,
        symbol
    ):

        return {

            "best_session":
                self.best_session(symbol),

            "best_timeframe":
                self.best_timeframe(symbol)

        }

    # =====================================================
    # NEWS FEEDBACK
    # =====================================================

    def news_feedback(
        self,
        symbol
    ):

        return self.news_impact(symbol)

    # =====================================================
    # AI DECISION
    # =====================================================

    def ai_decision(
        self,
        signal
    ):

        report = self.optimization_report(

            signal.symbol

        )

        confidence = self.confidence_score(

            signal.symbol

        )

        quality = self.quality_score(

            signal

        )

        return {

            "symbol": signal.symbol,

            "confidence": confidence,

            "quality": quality,

            "optimization": report

        }

    # =====================================================
    # FULL REPORT
    # =====================================================

    def full_report(
        self,
        symbol
    ):

        return {

            "statistics":
                self.symbol_statistics(symbol),

            "optimization":
                self.optimization_report(symbol),

            "memory":
                self.memory_status(),

            "news":
                self.news_impact(symbol)

        }

    # =====================================================
    # EXPORT
    # =====================================================

    def export_learning(
        self
    ):

        return {

            "trade_memory":
                self.trade_memory,

            "signal_memory":
                self.signal_memory,

            "market_memory":
                self.market_memory,

            "pattern_memory":
                self.pattern_memory,

            "news_memory":
                self.news_memory

        }

    # =====================================================
    # RESET MEMORY
    # =====================================================

    def reset_memory(
        self
    ):

        self.trade_memory.clear()

        self.signal_memory.clear()

        self.market_memory.clear()

        self.pattern_memory.clear()

        self.news_memory.clear()

        self.logger.info(

            "Learning Memory Reset"

        )

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self
    ):

        self.logger.info(

            "Learning Engine Shutdown"

        )