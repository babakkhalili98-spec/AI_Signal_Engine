from signal_engine.pivot_engine import PivotEngine
from signal_engine.rsi_engine import RSIEngine
from signal_engine.ichimoku_engine import IchimokuEngine
from signal_engine.candlestick_engine import CandlestickEngine
from signal_engine.fibonacci_engine import FibonacciEngine
from signal_engine.harmonic_engine import HarmonicEngine
from signal_engine.ao_engine import AOEngine
from signal_engine.smart_money_engine import SmartMoneyEngine
from signal_engine.noise_engine import NoiseEngine


class SignalEngine:

    def __init__(self):

        self.pivot = PivotEngine()

        self.rsi = RSIEngine()

        self.ichimoku = IchimokuEngine()

        self.candlestick = CandlestickEngine()

        self.fibonacci = FibonacciEngine()

        self.harmonic = HarmonicEngine()

        self.ao = AOEngine()

        self.smart_money = SmartMoneyEngine()

        self.noise = NoiseEngine()

    def analyze(self, symbol, timeframe, data):

        engines = []

        engines.append(
            self.pivot.analyze(symbol, timeframe, data)
        )

        engines.append(
            self.rsi.analyze(symbol, timeframe, data)
        )

        engines.append(
            self.ichimoku.analyze(symbol, timeframe, data)
        )

        engines.append(
            self.candlestick.analyze(symbol, timeframe, data)
        )

        engines.append(
            self.fibonacci.analyze(symbol, timeframe, data)
        )

        engines.append(
            self.harmonic.analyze(symbol, timeframe, data)
        )

        engines.append(
            self.ao.analyze(symbol, timeframe, data)
        )

        engines.append(
            self.smart_money.analyze(symbol, timeframe, data)
        )

        noise = self.noise.analyze(symbol, timeframe, data)

        total_score = 0

        buy = 0

        sell = 0

        reasons = []

        for result in engines:

            total_score += result["score"]

            reasons.append(result["reason"])

            if result["direction"] == "BUY":

                buy += 1

            elif result["direction"] == "SELL":

                sell += 1

        confluence = round((max(buy, sell) / len(engines)) * 100, 2)

        direction = "NONE"

        if buy > sell:

            direction = "BUY"

        elif sell > buy:

            direction = "SELL"

        if total_score < 72:

            signal = "NO TRADE"

        else:

            signal = direction

        return {

            "symbol": symbol,

            "timeframe": timeframe,

            "signal": signal,

            "direction": direction,

            "score": total_score,

            "confluence": confluence,

            "noise": noise,

            "reasons": reasons,

            "engines": engines

        }