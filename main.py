"""
=========================================================
AI SIGNAL ENGINE
MAIN
Version : 3.0
=========================================================
"""

from datetime import datetime
import traceback
import time
import logging

import config.settings as Settings

from core.database_manager import DatabaseManager
from core.exchange_client import ExchangeClient
from core.market_data import MarketData

from core.scanner import Scanner

from signal_engine.signal_engine import SignalEngine

from score.score_engine import ScoreEngine

from risk.risk_management_engine import RiskManagementEngine

from core.message_dispatcher import MessageDispatcher


# ==========================================================
# AI Signal Engine
# ==========================================================

class AISignalEngine:

    def __init__(self):

        logging.basicConfig(

            level=logging.INFO,

            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"

        )

        self.logger = logging.getLogger(

            "AI_Signal_Engine"

        )

        self.logger.info("=" * 70)
        self.logger.info("AI SIGNAL ENGINE STARTING")
        self.logger.info("=" * 70)

        # ==========================================
        # Core
        # ==========================================

        self.database = DatabaseManager()

        self.exchange = ExchangeClient()

        self.market = MarketData()

        self.market.initialize()

        # ==========================================
        # Engines
        # ==========================================

        self.score_engine = ScoreEngine()

        self.risk_manager = RiskManagementEngine()

        self.signal_engine = SignalEngine()

        self.dispatcher = MessageDispatcher()

        # ==========================================
        # Scanner
        # ==========================================

        self.scanner = Scanner(

            logger=self.logger,

            exchange=self.exchange,

            database=self.database,

            score_engine=self.score_engine,

            risk_manager=self.risk_manager,

        )

        self.symbols = Settings.DEFAULT_SYMBOLS

        self.timeframes = Settings.TIMEFRAMES

        self.logger.info("Initialization Complete")

    # ==========================================================
    # Run One Cycle
    # ==========================================================

    def run_cycle(self):

        self.logger.info("=" * 70)
        self.logger.info("NEW SCAN CYCLE")
        self.logger.info("=" * 70)

        all_signals = []

        for timeframe in self.timeframes:

            self.logger.info(

                f"Scanning TimeFrame : {timeframe}"

            )

            try:

                signals = self.scanner.run(

                    symbols=self.symbols,

                    timeframe=timeframe,

                )

            except Exception:

                self.logger.exception(

                    traceback.format_exc()

                )

                continue

            if signals:

                all_signals.extend(

                    signals

                )

        if len(all_signals) == 0:

            self.logger.info(

                "No Valid Signal"

            )

            return

        # ==========================================
        # انتخاب بهترین سیگنال
        # ==========================================

        best_signal = max(

            all_signals,

            key=lambda x: x["final_score"]

        )

        self.logger.info("=" * 70)
        self.logger.info("BEST SIGNAL")
        self.logger.info("=" * 70)

        self.logger.info(

            f"{best_signal['symbol']} | "

            f"{best_signal['timeframe']} | "

            f"{best_signal['signal']} | "

            f"Score={best_signal['final_score']}"

        )

        # ==========================================
        # ارسال
        # ==========================================

        try:

            self.dispatcher.send_signal(

                best_signal

            )

        except Exception:

            self.logger.exception(

                traceback.format_exc()

            )

        # ==========================================
        # ذخیره
        # ==========================================

        try:

            self.database.save_signal_v2(

                best_signal

            )

        except Exception:

            self.logger.exception(

                traceback.format_exc()

            )

    # ==========================================================
    # Health Check
    # ==========================================================

    def health_check(self):

        self.logger.info(

            "Running Health Check..."

        )

        report = {}

        # ==========================================
        # Exchange
        # ==========================================

        try:

            report["exchange"] = (

                self.exchange.health_check()

            )

        except Exception:

            report["exchange"] = False

        # ==========================================
        # Database
        # ==========================================

        try:

            report["database"] = (

                self.database.health_check()

            )

        except Exception:

            report["database"] = False

        # ==========================================
        # Market
        # ==========================================

        try:

            report["market"] = (

                self.market.health_check()

            )

        except Exception:

            report["market"] = False

        # ==========================================
        # Scanner
        # ==========================================

        try:

            report["scanner"] = (

                self.scanner.health_check()

            )

        except Exception:

            report["scanner"] = False

        # ==========================================
        # Signal Engine
        # ==========================================

        try:

            report["signal_engine"] = {

                "status": "OK"

            }

        except Exception:

            report["signal_engine"] = False

        # ==========================================
        # Dispatcher
        # ==========================================

        try:

            report["dispatcher"] = (

                self.dispatcher.health_check()

            )

        except Exception:

            report["dispatcher"] = False

        return report

    # ==========================================================
    # Shutdown
    # ==========================================================

    def shutdown(self):

        self.logger.info("=" * 70)

        self.logger.info(

            "AI SIGNAL ENGINE SHUTDOWN"

        )

        self.logger.info("=" * 70)

        try:

            self.market.shutdown()

        except Exception:

            pass

        try:

            self.dispatcher.shutdown()

        except Exception:

            pass

        try:

            self.database.close()

        except Exception:

            pass

        try:

            self.exchange.disconnect()

        except Exception:

            pass

    # ==========================================================
    # Start
    # ==========================================================

    def start(self):

        self.logger.info("=" * 70)
        self.logger.info("ENGINE STARTED")
        self.logger.info("=" * 70)

        while True:

            try:

                self.run_cycle()

            except KeyboardInterrupt:

                self.logger.info(

                    "Stopped By User"

                )

                break

            except Exception:

                self.logger.exception(

                    traceback.format_exc()

                )

            time.sleep(

                Settings.SCAN_INTERVAL

            )

        self.shutdown()


# ==========================================================
# Main
# ==========================================================

def main():

    engine = None

    try:

        engine = AISignalEngine()

        health = engine.health_check()

        print()

        print("=" * 70)
        print("SYSTEM HEALTH")
        print("=" * 70)

        for name, status in health.items():

            print(f"{name:20} : {status}")

        print("=" * 70)
        print()

        engine.start()

    except KeyboardInterrupt:

        print()

        print("Stopped By User")

        if engine:

            engine.shutdown()

    except Exception:

        print()

        print(traceback.format_exc())

        if engine:

            engine.shutdown()


# ==========================================================

if __name__ == "__main__":

    main()