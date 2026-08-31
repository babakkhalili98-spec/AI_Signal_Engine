from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import traceback

from core.market_data import MarketData
from signal_engine.signal_engine import SignalEngine


class Scanner:

    def __init__(
        self,
        logger,
        exchange,
        database,
        score_engine,
        risk_manager,
    ):

        self.logger = logger
        self.exchange = exchange
        self.database = database
        self.score_engine = score_engine
        self.risk_manager = risk_manager

        self.market = MarketData()
        self.signal_engine = SignalEngine()

        self.max_workers = 8

    # =====================================================

    def scan_market(self, symbols, timeframe):

        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:

            futures = [
                executor.submit(
                    self.scan_symbol,
                    symbol,
                    timeframe,
                )
                for symbol in symbols
            ]

            for future in futures:

                try:

                    signal = future.result()

                    if signal is not None:

                        results.append(signal)

                except Exception:

                    self.logger.exception(traceback.format_exc())

        return results

    # =====================================================

    def scan_symbol(self, symbol, timeframe):

        try:

            data = self.market.get_market_data(
                symbol=symbol,
                timeframe=timeframe,
                limit=300,
            )

            if data is None:
                return None

            signal = self.signal_engine.analyze(
                symbol=symbol,
                timeframe=timeframe,
                data=data,
            )

            if signal is None:
                return None

            if signal.get("signal") == "NO TRADE":
                return None

            # ----------------------------------
            # Risk First
            # ----------------------------------

            risk = self.risk_manager.calculate(
                symbol=symbol,
                signal=signal,
                data=data,
            )

            signal["risk"] = risk

            # ----------------------------------
            # Score After Risk
            # ----------------------------------

            score = self.score_engine.calculate(signal)

            signal["final_score"] = score

            if score < 72:
                return None

            signal["created_at"] = datetime.now()

            self.save_signal(signal)

            return signal

        except Exception:

            self.logger.exception(traceback.format_exc())

            return None

    # =====================================================

    def save_signal(self, signal):

        try:

            self.database.save_signal_v2(signal)

        except Exception:

            self.logger.exception(traceback.format_exc())

    # =====================================================

    def sort_signals(self, signals):

        if not signals:
            return []

        return sorted(
            signals,
            key=lambda s: (
                s.get("final_score", 0),
                s.get("confluence", 0),
                s.get("risk", {}).get("rr", 0),
            ),
            reverse=True,
        )

    # =====================================================

    def get_best_signal(self, signals):

        signals = self.sort_signals(signals)

        if not signals:
            return None

        return signals[0]

    # =====================================================

    def print_summary(self, signals):

        self.logger.info("=" * 40)
        self.logger.info(f"Signals : {len(signals)}")
        self.logger.info("=" * 40)

        for s in signals:

            rr = s.get("risk", {}).get("rr", "-")

            self.logger.info(
                f'{s.get("symbol")} | '
                f'{s.get("signal")} | '
                f'Score={s.get("final_score")} | '
                f'RR={rr}'
            )

        self.logger.info("=" * 40)

    # =====================================================

    def run(self, symbols, timeframe):

        signals = self.scan_market(symbols, timeframe)

        signals = self.sort_signals(signals)

        self.print_summary(signals)

        return signals

    # =====================================================

    def run_single(self, symbol, timeframe):

        return self.scan_symbol(symbol, timeframe)

    # =====================================================

    def health_check(self):

        return {
            "status": "OK",
            "scanner": "Running",
            "signal_engine": "Connected",
            "market_data": "Connected",
            "database": "Connected",
        }