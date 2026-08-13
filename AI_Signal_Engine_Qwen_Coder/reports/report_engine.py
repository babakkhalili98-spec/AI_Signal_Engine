"""
=========================================================
AI SIGNAL ENGINE
Report Engine
Version : 5.0
=========================================================

وظایف

✓ ساخت گزارش نهایی
✓ ساخت Header
✓ ساخت Verdict
✓ ساخت Confidence
✓ ساخت Score
✓ ساخت Trade
✓ ساخت Market
✓ ساخت Analysis
✓ ساخت Risk
✓ ساخت News
✓ ساخت Recovery
✓ ساخت Learning
✓ ساخت Queue
✓ ساخت Summary
✓ ساخت Metadata

=========================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any
import uuid


# =========================================================
# Report Engine
# =========================================================

class ReportEngine:

    def __init__(
        self,
        config,
        logger,
        database
    ):

        self.config = config
        self.logger = logger
        self.database = database

    # =====================================================
    # BUILD REPORT
    # =====================================================

    def build(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:

        report = {

            "report_id":
                self.generate_report_id(),

            "header":
                self.build_header(signal),

            "verdict":
                self.build_verdict(signal),

            "confidence":
                self.build_confidence(signal),

            "score":
                self.build_score(signal),

            "trade":
                self.build_trade(signal),

            "market":
                self.build_market(signal),

            "analysis":
                self.build_analysis(signal),

            "risk":
                self.build_risk(signal),

            "news":
                self.build_news(signal),

            "recovery":
                self.build_recovery(signal),

            "learning":
                self.build_learning(signal),

            "queue":
                self.build_queue(signal),

            "summary":
                self.build_summary(signal),

            "metadata":
                self.build_metadata(signal)

        }

        return report

    # =====================================================
    # REPORT ID
    # =====================================================

    def generate_report_id(self) -> str:

        now = datetime.utcnow().strftime(
            "%Y%m%d%H%M%S"
        )

        uid = uuid.uuid4().hex[:8].upper()

        return f"REP-{now}-{uid}"

    # =====================================================
    # HEADER
    # =====================================================

    def build_header(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {

            "market":
                signal.get(
                    "market",
                    "UNKNOWN"
                ),

            "symbol":
                signal.get(
                    "symbol",
                    "UNKNOWN"
                ),

            "timeframe":
                signal.get(
                    "timeframe",
                    "UNKNOWN"
                ),

            "direction":
                signal.get(
                    "direction",
                    "NONE"
                ),

            "created_at":
                datetime.utcnow().isoformat(),

            "engine_version":
                getattr(
                    self.config,
                    "VERSION",
                    "5.0"
                )

        }

    # =====================================================
    # VERDICT
    # =====================================================

    def build_verdict(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:

        score = float(

            signal.get(
                "score",
                {}
            ).get(
                "score",
                0
            )

        )

        if score >= 90:

            verdict = "VERY_STRONG"
            stars = 5

        elif score >= 80:

            verdict = "STRONG"
            stars = 4

        elif score >= 70:

            verdict = "GOOD"
            stars = 3

        elif score >= 60:

            verdict = "WEAK"
            stars = 2

        else:

            verdict = "IGNORE"
            stars = 1

        return {

            "stars": stars,

            "verdict": verdict,

            "reason":

                signal.get(
                    "best_reason",
                    ""
                )

        }

    # =====================================================
    # CONFIDENCE
    # =====================================================

    def build_confidence(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:

        score = signal.get(
            "score",
            {}
        )

        confidence = float(

            score.get(
                "confidence",
                0
            )

        )

        return {

            "value":
                confidence,

            "percent":
                f"{confidence:.1f}%",

            "bars":
                round(confidence / 10),

            "max_bars":
                10

        }

    # =====================================================
    # SCORE
    # =====================================================

    def build_score(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:

        score = signal.get(
            "score",
            {}
        )

        return {

            "total_score":
                score.get(
                    "score",
                    0
                ),

            "raw_score":
                score.get(
                    "raw_score",
                    0
                ),

            "confidence":
                score.get(
                    "confidence",
                    0
                ),

            "modules":
                score.get(
                    "modules",
                    {}
                ),

            "evidence":
                score.get(
                    "reasons",
                    []
                )

        }
    # =====================================================
    # TRADE
    # =====================================================

    def build_trade(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:

        risk = signal.get(
            "risk",
            {}
        )

        return {

            "direction":
                signal.get("direction"),

            "entry":
                signal.get("entry"),

            "stop_loss":
                signal.get("stop_loss"),

            "tp1":
                signal.get("tp1"),

            "tp2":
                signal.get("tp2"),

            "tp3":
                signal.get("tp3"),

            "break_even":
                signal.get(
                    "break_even",
                    False
                ),

            "partial_close":
                signal.get(
                    "partial_close_percent",
                    0
                ),

            "risk_reward":
                risk.get(
                    "risk_reward"
                ),

            "capital_percent":
                risk.get(
                    "capital_percent"
                ),

            "position_size":
                risk.get(
                    "position_size"
                ),

            "leverage":
                risk.get(
                    "leverage"
                )

        }

    # =====================================================
    # MARKET
    # =====================================================

    def build_market(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:

        market = signal.get(
            "market_state",
            {}
        )

        return {

            "trend":
                market.get("trend"),

            "structure":
                market.get("structure"),

            "market_phase":
                market.get("market_phase"),

            "volatility":
                market.get("volatility"),

            "volume":
                market.get("volume"),

            "spread":
                market.get("spread"),

            "session":
                market.get("session"),

            "noise":
                market.get("noise")

        }

    # =====================================================
    # ANALYSIS
    # =====================================================

    def build_analysis(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {

            "pivot":
                signal.get("pivot"),

            "rsi":
                signal.get("rsi"),

            "ichimoku":
                signal.get("ichimoku"),

            "ao":
                signal.get("ao"),

            "candlestick":
                signal.get("candlestick"),

            "harmonic":
                signal.get("harmonic"),

            "fibonacci":
                signal.get("fibonacci"),

            "smart_money":
                signal.get("smart_money"),

            "order_book":
                signal.get("order_book"),

            "capital_flow":
                signal.get("capital_flow"),

            "pattern_dna":
                signal.get("pattern_dna"),

            "quality_score":
                signal.get("quality_score"),

            "indicators":
                signal.get(
                    "indicators",
                    {}
                )

        }

    # =====================================================
    # RISK
    # =====================================================

    def build_risk(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:

        risk = signal.get(
            "risk",
            {}
        )

        return {

            "approved":
                risk.get(
                    "approved",
                    False
                ),

            "risk_level":
                risk.get(
                    "risk_level"
                ),

            "risk_reward":
                risk.get(
                    "risk_reward"
                ),

            "expected_profit":
                risk.get(
                    "expected_profit"
                ),

            "expected_loss":
                risk.get(
                    "expected_loss"
                ),

            "max_drawdown":
                risk.get(
                    "max_drawdown"
                ),

            "position_size":
                risk.get(
                    "position_size"
                ),

            "capital_percent":
                risk.get(
                    "capital_percent"
                ),

            "recommendation":
                risk.get(
                    "recommendation"
                )

        }
    # =====================================================
    # NEWS
    # =====================================================

    def build_news(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:

        news = signal.get(
            "news",
            {}
        )

        return {

            "red_news":
                news.get(
                    "red_news",
                    False
                ),

            "orange_news":
                news.get(
                    "orange_news",
                    False
                ),

            "impact":
                news.get(
                    "impact",
                    "UNKNOWN"
                ),

            "remaining_effect":
                news.get(
                    "remaining_effect"
                ),

            "event_name":
                news.get(
                    "event_name"
                ),

            "country":
                news.get(
                    "country"
                ),

            "currency":
                news.get(
                    "currency"
                ),

            "importance":
                news.get(
                    "importance"
                )

        }

    # =====================================================
    # RECOVERY
    # =====================================================

    def build_recovery(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:

        recovery = signal.get(
            "recovery",
            {}
        )

        return {

            "recovered":
                recovery.get(
                    "recovered",
                    False
                ),

            "recovery_time":
                recovery.get(
                    "recovery_time"
                ),

            "gap_recovery":
                recovery.get(
                    "gap_recovery",
                    False
                ),

            "ambiguous":
                recovery.get(
                    "ambiguous",
                    False
                ),

            "lifecycle_stage":
                recovery.get(
                    "lifecycle_stage",
                    "NEW"
                )

        }

    # =====================================================
    # LEARNING
    # =====================================================

    def build_learning(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:

        learning = signal.get(
            "learning",
            {}
        )

        return {

            "expected_result":
                learning.get(
                    "expected_result"
                ),

            "actual_result":
                learning.get(
                    "actual_result"
                ),

            "difference":
                learning.get(
                    "difference"
                ),

            "learning_weight":
                learning.get(
                    "learning_weight"
                ),

            "quality_score":
                learning.get(
                    "quality_score"
                ),

            "next_adjustment":
                learning.get(
                    "next_adjustment"
                )

        }

    # =====================================================
    # QUEUE
    # =====================================================

    def build_queue(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:

        queue = signal.get(
            "queue",
            {}
        )

        return {

            "database_saved":
                queue.get(
                    "database_saved",
                    False
                ),

            "telegram_sent":
                queue.get(
                    "telegram_sent",
                    False
                ),

            "bale_sent":
                queue.get(
                    "bale_sent",
                    False
                ),

            "dispatcher_status":
                queue.get(
                    "dispatcher_status",
                    "WAITING"
                ),

            "retry_count":
                queue.get(
                    "retry_count",
                    0
                )

        }

    # =====================================================
    # SUMMARY
    # =====================================================

    def build_summary(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:

        return {

            "ai_summary":
                signal.get(
                    "ai_summary",
                    ""
                ),

            "final_decision":
                signal.get(
                    "final_decision",
                    "NO_TRADE"
                ),

            "best_reason":
                signal.get(
                    "best_reason",
                    ""
                ),

            "warning":
                signal.get(
                    "warning",
                    ""
                )

        }
    # =====================================================
    # SAVE REPORT
    # =====================================================

    def save_report(
        self,
        report: Dict[str, Any]
    ) -> bool:

        try:

            if hasattr(self.database, "save_report"):

                self.database.save_report(report)

            else:

                self.logger.warning(
                    "DatabaseManager.save_report() not found."
                )

            return True

        except Exception as ex:

            self.logger.exception(ex)

            return False

    # =====================================================
    # EXPORT REPORT
    # =====================================================

    def export_report(
        self,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:

        report = self.build(signal)

        saved = self.save_report(report)

        report["queue"]["database_saved"] = saved

        return report

    # =====================================================
    # VALIDATE
    # =====================================================

    def validate(
        self,
        report: Dict[str, Any]
    ) -> bool:

        required = [

            "report_id",
            "header",
            "verdict",
            "confidence",
            "score",
            "trade",
            "market",
            "analysis",
            "risk",
            "summary",
            "metadata"

        ]

        for key in required:

            if key not in report:

                self.logger.error(

                    f"Missing Report Field : {key}"

                )

                return False

        return True

    # =====================================================
    # PRINT REPORT
    # =====================================================

    def print_report(
        self,
        report: Dict[str, Any]
    ) -> None:

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info(f"REPORT : {report['report_id']}")
        self.logger.info("=" * 70)

        self.logger.info(
            f"Symbol : {report['header']['symbol']}"
        )

        self.logger.info(
            f"Direction : {report['header']['direction']}"
        )

        self.logger.info(
            f"Verdict : {report['verdict']['verdict']}"
        )

        self.logger.info(
            f"Score : {report['score']['total_score']}"
        )

        self.logger.info(
            f"Confidence : {report['confidence']['percent']}"
        )

        self.logger.info("=" * 70)