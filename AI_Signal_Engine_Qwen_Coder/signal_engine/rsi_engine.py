# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 1
# DATA VALIDATION ENGINE
# ==========================================================

import math
import numpy as np


class RSIValidationEngine:

    """
    بررسی کیفیت داده‌ها قبل از محاسبه RSI

    مستقل

    بدون وابستگی به سایر Engine ها
    """

    def __init__(self):

        self.reset()

    # ------------------------------------------------------

    def reset(self):

        self.valid = True

        self.score = 100

        self.errors = []

        self.warnings = []

    # ------------------------------------------------------

    def validate_dataframe(

        self,

        df,

    ):

        if df is None:

            self.valid = False

            self.errors.append(

                "DataFrame is None"

            )

            return

        if len(df) == 0:

            self.valid = False

            self.errors.append(

                "Empty DataFrame"

            )

    # ------------------------------------------------------

    def validate_columns(

        self,

        df,

    ):

        required = [

            "open",

            "high",

            "low",

            "close",

            "volume",

        ]

        for col in required:

            if col not in df.columns:

                self.valid = False

                self.errors.append(

                    f"Missing Column : {col}"

                )

    # ------------------------------------------------------

    def validate_candle_count(

        self,

        df,

        minimum=150,

    ):

        if len(df) < minimum:

            self.valid = False

            self.errors.append(

                f"Need {minimum} Candles"

            )

    # ------------------------------------------------------

    def validate_nan(

        self,

        df,

    ):

        if df.isnull().values.any():

            self.score -= 15

            self.warnings.append(

                "NaN Values"

            )

    # ------------------------------------------------------

    def validate_inf(

        self,

        df,

    ):

        if np.isinf(

            df.select_dtypes(

                include=np.number

            )

        ).values.any():

            self.valid = False

            self.errors.append(

                "Infinity Values"

            )

    # ------------------------------------------------------

    def validate_prices(

        self,

        df,

    ):

        if (df["close"] <= 0).any():

            self.valid = False

            self.errors.append(

                "Invalid Close Price"

            )

        if (df["high"] < df["low"]).any():

            self.valid = False

            self.errors.append(

                "High < Low"

            )

    # ------------------------------------------------------

    def validate_duplicates(

        self,

        df,

    ):

        duplicated = df.index.duplicated().sum()

        if duplicated > 0:

            self.score -= 5

            self.warnings.append(

                f"{duplicated} Duplicate Index"

            )

    # ------------------------------------------------------

    def validate_volume(

        self,

        df,

    ):

        if (df["volume"] == 0).all():

            self.score -= 10

            self.warnings.append(

                "Zero Volume"

            )

    # ------------------------------------------------------

    def validate_close_variation(

        self,

        df,

    ):

        if df["close"].std() == 0:

            self.valid = False

            self.errors.append(

                "No Price Variation"

            )

    # ------------------------------------------------------

    def normalize_score(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )

    # ------------------------------------------------------

    def report(self):

        self.normalize_score()

        return {

            "engine": "RSI Validation",

            "valid": self.valid,

            "score": self.score,

            "errors": self.errors,

            "warnings": self.warnings,

        }
{

"engine":"RSI Validation",

"valid":True,

"score":95,

"errors":[],

"warnings":[

"NaN Values"

]

}
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 2
# RSI CALCULATION ENGINE
# ==========================================================

import numpy as np
import pandas as pd


class RSICalculationEngine:

    """
    محاسبه حرفه‌ای RSI

    فقط محاسبه

    بدون تحلیل

    بدون سیگنال
    """

    def __init__(self):

        self.period = 14

    # ------------------------------------------------------

    def calculate(

        self,

        close: pd.Series,

        period: int = 14,

    ) -> pd.Series:

        """
        Wilder RSI
        """

        delta = close.diff()

        gain = delta.where(

            delta > 0,

            0.0,

        )

        loss = -delta.where(

            delta < 0,

            0.0,

        )

        avg_gain = gain.ewm(

            alpha=1 / period,

            adjust=False,

            min_periods=period,

        ).mean()

        avg_loss = loss.ewm(

            alpha=1 / period,

            adjust=False,

            min_periods=period,

        ).mean()

        rs = avg_gain / avg_loss.replace(

            0,

            np.nan,

        )

        rsi = 100 - (

            100 /

            (1 + rs)

        )

        return rsi.fillna(50)
    # ------------------------------------------------------

    def calculate_multi(

        self,

        close,

    ):

        return {

            "rsi7":

                self.calculate(

                    close,

                    7,

                ),

            "rsi14":

                self.calculate(

                    close,

                    14,

                ),

            "rsi21":

                self.calculate(

                    close,

                    21,

                ),

            "rsi50":

                self.calculate(

                    close,

                    50,

                ),

        }
    # ------------------------------------------------------

    def latest(

        self,

        rsi_series,

    ):

        if len(rsi_series) == 0:

            return None

        return float(

            rsi_series.iloc[-1]

        )
    # ------------------------------------------------------

    def last_values(

        self,

        rsi_series,

        count=10,

    ):

        return list(

            rsi_series.tail(

                count

            )

        )
    # ------------------------------------------------------

    def slope(

        self,

        rsi_series,

        length=5,

    ):

        if len(rsi_series) < length:

            return 0

        y = rsi_series.tail(length).values

        x = np.arange(length)

        slope, _ = np.polyfit(

            x,

            y,

            1,

        )

        return float(slope)
    # ------------------------------------------------------

    def report(

        self,

        close,

    ):

        rsi14 = self.calculate(

            close,

            14,

        )

        return {

            "engine":

                "RSI",

            "value":

                round(

                    self.latest(

                        rsi14,

                    ),

                    2,

                ),

            "slope":

                round(

                    self.slope(

                        rsi14,

                    ),

                    4,

                ),

            "series":

                rsi14,

        }
{

"engine":"RSI",

"value":62.41,

"slope":1.84,

"series":...

}
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 3
# DYNAMIC RSI LEVEL ENGINE
# ==========================================================

import numpy as np


class RSIDynamicLevelEngine:

    """
    محاسبه سطوح داینامیک RSI

    مستقل

    فقط سطح ها را محاسبه می‌کند.

    هیچ سیگنالی تولید نمی‌کند.
    """

    def __init__(self):

        self.reset()

    # -------------------------------------------------

    def reset(self):

        self.upper = 80

        self.lower = 20

        self.middle = 50

        self.market_state = "NORMAL"

        self.score = 0

        self.reasons = []
    # -------------------------------------------------

    def detect_market_state(

        self,

        atr_percent,

        trend_strength,

    ):

        if trend_strength >= 80:

            self.market_state = "STRONG_TREND"

        elif atr_percent >= 3:

            self.market_state = "HIGH_VOLATILITY"

        elif atr_percent <= 1:

            self.market_state = "LOW_VOLATILITY"

        else:

            self.market_state = "NORMAL"
    # -------------------------------------------------

    def calculate_levels(self):

        if self.market_state == "STRONG_TREND":

            self.upper = 85

            self.lower = 30

        elif self.market_state == "HIGH_VOLATILITY":

            self.upper = 82

            self.lower = 18

        elif self.market_state == "LOW_VOLATILITY":

            self.upper = 75

            self.lower = 25

        else:

            self.upper = 80

            self.lower = 20

        self.middle = (

            self.upper +

            self.lower

        ) / 2
    # -------------------------------------------------

    def distance_to_upper(

        self,

        rsi,

    ):

        return self.upper - rsi

    # -------------------------------------------------

    def distance_to_lower(

        self,

        rsi,

    ):

        return rsi - self.lower
    # -------------------------------------------------

    def classify_position(

        self,

        rsi,

    ):

        if rsi >= self.upper:

            return "OVERBOUGHT"

        if rsi <= self.lower:

            return "OVERSOLD"

        if rsi > self.middle:

            return "BULLISH"

        if rsi < self.middle:

            return "BEARISH"

        return "NEUTRAL"
    # -------------------------------------------------

    def calculate_score(

        self,

        rsi,

    ):

        pos = self.classify_position(rsi)

        if pos == "OVERBOUGHT":

            self.score = 100

        elif pos == "OVERSOLD":

            self.score = 100

        elif pos == "BULLISH":

            self.score = 60

        elif pos == "BEARISH":

            self.score = 60

        else:

            self.score = 50
    # -------------------------------------------------

    def report(

        self,

        rsi,

    ):

        return {

            "engine": "Dynamic RSI",

            "market_state": self.market_state,

            "upper": self.upper,

            "middle": self.middle,

            "lower": self.lower,

            "position": self.classify_position(rsi),

            "score": self.score,

            "distance_upper":

                round(

                    self.distance_to_upper(rsi),

                    2,

                ),

            "distance_lower":

                round(

                    self.distance_to_lower(rsi),

                    2,

                ),

        }
{

"engine":"Dynamic RSI",

"market_state":"HIGH_VOLATILITY",

"upper":82,

"middle":50,

"lower":18,

"position":"BULLISH",

"score":60,

"distance_upper":13.8,

"distance_lower":50.2

}
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 4
# RSI TREND STRUCTURE ENGINE
# ==========================================================

import numpy as np

class RSITrendEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------------

    def reset(self):

        self.direction = "NEUTRAL"

        self.trend_strength = 0

        self.score = 0

        self.reasons = []

        self.hh = False

        self.hl = False

        self.lh = False

        self.ll = False
    # ------------------------------------------------------

    def detect_higher_high(

        self,

        highs,

    ):

        if len(highs) < 2:

            return

        self.hh = highs[-1] > highs[-2]
    # ------------------------------------------------------

    def detect_higher_low(

        self,

        lows,

    ):

        if len(lows) < 2:

            return

        self.hl = lows[-1] > lows[-2]
    # ------------------------------------------------------

    def detect_lower_high(

        self,

        highs,

    ):

        if len(highs) < 2:

            return

        self.lh = highs[-1] < highs[-2]
    # ------------------------------------------------------

    def detect_lower_low(

        self,

        lows,

    ):

        if len(lows) < 2:

            return

        self.ll = lows[-1] < lows[-2]
    # ------------------------------------------------------

    def determine_direction(self):

        if self.hh and self.hl:

            self.direction = "BUY"

        elif self.lh and self.ll:

            self.direction = "SELL"

        else:

            self.direction = "NEUTRAL"
    # ------------------------------------------------------

    def calculate_slope(

        self,

        rsi,

        length=10,

    ):

        if len(rsi) < length:

            return 0

        x = np.arange(length)

        y = rsi.tail(length).values

        slope = np.polyfit(

            x,

            y,

            1,

        )[0]

        return slope
    # ------------------------------------------------------

    def calculate_strength(

        self,

        slope,

    ):

        s = abs(slope)

        if s >= 2:

            self.trend_strength = 100

        elif s >= 1.5:

            self.trend_strength = 85

        elif s >= 1:

            self.trend_strength = 70

        elif s >= 0.5:

            self.trend_strength = 55

        else:

            self.trend_strength = 35
    # ------------------------------------------------------

    def calculate_score(self):

        self.score = self.trend_strength

        if self.direction == "BUY":

            self.reasons.append(

                "Higher High"

            )

            self.reasons.append(

                "Higher Low"

            )

        elif self.direction == "SELL":

            self.reasons.append(

                "Lower High"

            )

            self.reasons.append(

                "Lower Low"

            )
    # ------------------------------------------------------

    def report(self):

        return {

            "engine":"RSI Trend",

            "direction":self.direction,

            "trend_strength":

                self.trend_strength,

            "score":self.score,

            "reasons":self.reasons,

        }
{

"engine":"RSI Trend",

"direction":"BUY",

"trend_strength":87,

"score":87,

"reasons":[

"Higher High",

"Higher Low"

]

}
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 4-2
# RSI STRUCTURE BREAK ENGINE
# ==========================================================

class RSIStructureBreakEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------------

    def reset(self):

        self.state = "NONE"

        self.score = 0

        self.direction = "NEUTRAL"

        self.reasons = []
    # ------------------------------------------------------

    def bullish_bos(

        self,

        current_high,

        previous_high,

        higher_low,

    ):

        if (

            current_high >

            previous_high

            and

            higher_low

        ):

            self.state = "BULLISH_BOS"

            self.direction = "BUY"

            self.score = 100

            self.reasons.append(

                "Bullish BOS"

            )
    # ------------------------------------------------------

    def bearish_bos(

        self,

        current_low,

        previous_low,

        lower_high,

    ):

        if (

            current_low <

            previous_low

            and

            lower_high

        ):

            self.state = "BEARISH_BOS"

            self.direction = "SELL"

            self.score = 100

            self.reasons.append(

                "Bearish BOS"

            )
    # ------------------------------------------------------

    def bullish_choch(

        self,

        last_direction,

        bullish_break,

    ):

        if (

            last_direction == "SELL"

            and

            bullish_break

        ):

            self.state = "BULLISH_CHOCH"

            self.direction = "BUY"

            self.score = 85

            self.reasons.append(

                "Bullish CHoCH"

            )
    # ------------------------------------------------------

    def bearish_choch(

        self,

        last_direction,

        bearish_break,

    ):

        if (

            last_direction == "BUY"

            and

            bearish_break

        ):

            self.state = "BEARISH_CHOCH"

            self.direction = "SELL"

            self.score = 85

            self.reasons.append(

                "Bearish CHoCH"

            )
    # ------------------------------------------------------

    def failed_break(

        self,

        breakout,

        follow_through,

    ):

        if (

            breakout

            and

            not follow_through

        ):

            self.state = "FAILED_BOS"

            self.score = 35

            self.reasons.append(

                "Failed BOS"

            )
    # ------------------------------------------------------

    def weak_break(

        self,

        breakout,

        momentum,

    ):

        if (

            breakout

            and

            momentum < 40

        ):

            self.state = "WEAK_BOS"

            self.score = 55

            self.reasons.append(

                "Weak BOS"

            )
    # ------------------------------------------------------

    def break_strength(

        self,

        distance,

    ):

        if distance >= 8:

            self.score += 10

        elif distance >= 5:

            self.score += 6

        elif distance >= 3:

            self.score += 3
    # ------------------------------------------------------

    def report(self):

        return {

            "engine":

                "RSI Structure",

            "state":

                self.state,

            "direction":

                self.direction,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"RSI Structure",

"state":"BULLISH_CHOCH",

"direction":"BUY",

"score":92,

"reasons":[

"Bullish CHoCH",

"Strong Break"

]

}
structure = structure_engine.report()

internal_score += structure["score"] * 0.10
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 5
# REGULAR DIVERGENCE ENGINE
# ==========================================================

class RSIRegularDivergence:

    def __init__(self):

        self.reset()

    # ------------------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.score = 0

        self.type = "NONE"

        self.reasons = []
    # ------------------------------------------------------

    def bullish(

        self,

        price_low_1,

        price_low_2,

        rsi_low_1,

        rsi_low_2,

    ):

        if (

            price_low_2 < price_low_1

            and

            rsi_low_2 > rsi_low_1

        ):

            self.direction = "BUY"

            self.type = "REGULAR"

            self.score = 100

            self.reasons.append(

                "Bullish Regular Divergence"

            )
    # ------------------------------------------------------

    def bearish(

        self,

        price_high_1,

        price_high_2,

        rsi_high_1,

        rsi_high_2,

    ):

        if (

            price_high_2 > price_high_1

            and

            rsi_high_2 < rsi_high_1

        ):

            self.direction = "SELL"

            self.type = "REGULAR"

            self.score = 100

            self.reasons.append(

                "Bearish Regular Divergence"

            )
    # ------------------------------------------------------

    def strength(

        self,

        rsi_difference,

    ):

        if rsi_difference >= 20:

            self.score += 10

        elif rsi_difference >= 15:

            self.score += 7

        elif rsi_difference >= 10:

            self.score += 5

        elif rsi_difference >= 5:

            self.score += 2
    # ------------------------------------------------------

    def validate_distance(

        self,

        candle_distance,

    ):

        if 5 <= candle_distance <= 40:

            self.score += 5

        else:

            self.score -= 5
    # ------------------------------------------------------

    def validate_zone(

        self,

        rsi,

    ):

        if self.direction == "BUY":

            if rsi <= 25:

                self.score += 5

        if self.direction == "SELL":

            if rsi >= 75:

                self.score += 5
    # ------------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # ------------------------------------------------------

    def report(self):

        return {

            "engine":"RSI Divergence",

            "direction":self.direction,

            "type":self.type,

            "score":self.score,

            "reasons":self.reasons,

        }
{

"engine":"RSI Divergence",

"direction":"BUY",

"type":"REGULAR",

"score":94,

"reasons":[

"Bullish Regular Divergence"

]

}
divergence = divergence_engine.report()

internal_score += divergence["score"] * 0.15
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 6
# HIDDEN DIVERGENCE ENGINE
# ==========================================================

class RSIHiddenDivergence:

    def __init__(self):

        self.reset()

    # ------------------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.type = "NONE"

        self.score = 0

        self.reasons = []
    # ------------------------------------------------------

    def bullish(

        self,

        price_low_1,

        price_low_2,

        rsi_low_1,

        rsi_low_2,

    ):

        if (

            price_low_2 > price_low_1

            and

            rsi_low_2 < rsi_low_1

        ):

            self.direction = "BUY"

            self.type = "HIDDEN"

            self.score = 100

            self.reasons.append(

                "Hidden Bullish Divergence"

            )
    # ------------------------------------------------------

    def bearish(

        self,

        price_high_1,

        price_high_2,

        rsi_high_1,

        rsi_high_2,

    ):

        if (

            price_high_2 < price_high_1

            and

            rsi_high_2 > rsi_high_1

        ):

            self.direction = "SELL"

            self.type = "HIDDEN"

            self.score = 100

            self.reasons.append(

                "Hidden Bearish Divergence"

            )
    # ------------------------------------------------------

    def calculate_strength(

        self,

        rsi_difference,

    ):

        if rsi_difference >= 20:

            self.score += 10

        elif rsi_difference >= 15:

            self.score += 7

        elif rsi_difference >= 10:

            self.score += 5

        elif rsi_difference >= 5:

            self.score += 2
    # ------------------------------------------------------

    def validate_trend(

        self,

        trend_direction,

    ):

        if trend_direction != self.direction:

            self.score -= 20

            self.reasons.append(

                "Trend Mismatch"

            )
    # ------------------------------------------------------

    def validate_distance(

        self,

        candles,

    ):

        if 5 <= candles <= 40:

            self.score += 5

        else:

            self.score -= 5
    # ------------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # ------------------------------------------------------

    def report(self):

        return {

            "engine":

                "RSI Hidden Divergence",

            "direction":

                self.direction,

            "type":

                self.type,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"RSI Hidden Divergence",

"direction":"BUY",

"type":"HIDDEN",

"score":91,

"reasons":[

"Hidden Bullish Divergence"

]

}
hidden = hidden_engine.report()

internal_score += hidden["score"] * 0.15
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 7
# TRIPLE DIVERGENCE ENGINE
# ==========================================================

class RSITripleDivergenceEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.type = "NONE"

        self.score = 0

        self.confidence = 0

        self.reasons = []
    # ------------------------------------------------------

    def detect_triple_bullish(

        self,

        price_lows,

        rsi_lows,

    ):

        if len(price_lows) < 3:

            return

        if len(rsi_lows) < 3:

            return

        if (

            price_lows[2] < price_lows[1] < price_lows[0]

            and

            rsi_lows[2] > rsi_lows[1] > rsi_lows[0]

        ):

            self.direction = "BUY"

            self.type = "TRIPLE"

            self.score = 100

            self.reasons.append(

                "Triple Bullish Divergence"

            )
    # ------------------------------------------------------

    def detect_triple_bearish(

        self,

        price_highs,

        rsi_highs,

    ):

        if len(price_highs) < 3:

            return

        if len(rsi_highs) < 3:

            return

        if (

            price_highs[2] > price_highs[1] > price_highs[0]

            and

            rsi_highs[2] < rsi_highs[1] < rsi_highs[0]

        ):

            self.direction = "SELL"

            self.type = "TRIPLE"

            self.score = 100

            self.reasons.append(

                "Triple Bearish Divergence"

            )
    # ------------------------------------------------------

    def validate_distance(

        self,

        candle_distance,

    ):

        if 10 <= candle_distance <= 80:

            self.score += 5

        else:

            self.score -= 5

            self.reasons.append(

                "Improper Pivot Distance"

            )
    # ------------------------------------------------------

    def calculate_strength(

        self,

        average_difference,

    ):

        if average_difference >= 20:

            self.score += 10

        elif average_difference >= 15:

            self.score += 7

        elif average_difference >= 10:

            self.score += 5

        else:

            self.score += 2
    # ------------------------------------------------------

    def validate_trend(

        self,

        trend_direction,

    ):

        if (

            trend_direction != self.direction

            and

            trend_direction != "NEUTRAL"

        ):

            self.score -= 20

            self.reasons.append(

                "Trend Mismatch"

            )
    # ------------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )

        self.confidence = self.score
    # ------------------------------------------------------

    def report(self):

        return {

            "engine":

                "RSI Triple Divergence",

            "direction":

                self.direction,

            "type":

                self.type,

            "score":

                self.score,

            "confidence":

                self.confidence,

            "reasons":

                self.reasons,

        }
{

"engine":"RSI Triple Divergence",

"direction":"BUY",

"type":"TRIPLE",

"score":96,

"confidence":96,

"reasons":[

"Triple Bullish Divergence"

]

}
triple = triple_divergence.report()

internal_score += triple["score"] * 0.20
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 8
# FAILURE SWING ENGINE
# ==========================================================

class RSIFailureSwingEngine:

    def __init__(self):

        self.reset()

    # -------------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.type = "NONE"

        self.score = 0

        self.confidence = 0

        self.reasons = []
    # -------------------------------------------------

    def detect_bullish(

        self,

        low1,

        high1,

        low2,

        breakout,

    ):

        if (

            low2 > low1

            and

            breakout

        ):

            self.direction = "BUY"

            self.type = "FAILURE_SWING"

            self.score = 100

            self.reasons.append(

                "Bullish Failure Swing"

            )
    # -------------------------------------------------

    def detect_bearish(

        self,

        high1,

        low1,

        high2,

        breakdown,

    ):

        if (

            high2 < high1

            and

            breakdown

        ):

            self.direction = "SELL"

            self.type = "FAILURE_SWING"

            self.score = 100

            self.reasons.append(

                "Bearish Failure Swing"

            )
    # -------------------------------------------------

    def breakout_strength(

        self,

        distance,

    ):

        if distance >= 10:

            self.score += 10

        elif distance >= 7:

            self.score += 7

        elif distance >= 5:

            self.score += 5

        else:

            self.score += 2
    # -------------------------------------------------

    def validate_zone(

        self,

        rsi,

        upper,

        lower,

    ):

        if (

            self.direction == "BUY"

            and

            rsi <= lower

        ):

            self.score += 5

        elif (

            self.direction == "SELL"

            and

            rsi >= upper

        ):

            self.score += 5

        else:

            self.score -= 5

            self.reasons.append(

                "Weak Failure Zone"

            )
    # -------------------------------------------------

    def validate_trend(

        self,

        trend,

    ):

        if (

            trend != self.direction

            and

            trend != "NEUTRAL"

        ):

            self.score -= 15

            self.reasons.append(

                "Trend Mismatch"

            )
    # -------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )

        self.confidence = self.score
    # -------------------------------------------------

    def report(self):

        return {

            "engine":

                "RSI Failure Swing",

            "direction":

                self.direction,

            "type":

                self.type,

            "score":

                self.score,

            "confidence":

                self.confidence,

            "reasons":

                self.reasons,

        }
{

"engine":"RSI Failure Swing",

"direction":"BUY",

"type":"FAILURE_SWING",

"score":93,

"confidence":93,

"reasons":[

"Bullish Failure Swing"

]

}
failure = failure_engine.report()

internal_score += failure["score"] * 0.12
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 9
# MOMENTUM ENGINE
# ==========================================================

import numpy as np

class RSIMomentumEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.score = 0

        self.momentum = 0

        self.strength = "UNKNOWN"

        self.reasons = []
    # ------------------------------------------------------

    def calculate(

        self,

        rsi,

        period=5,

    ):

        if len(rsi) < period:

            return 0

        self.momentum = (

            rsi.iloc[-1]

            -

            rsi.iloc[-period]

        )

        return self.momentum
    # ------------------------------------------------------

    def detect_direction(self):

        if self.momentum > 0:

            self.direction = "BUY"

        elif self.momentum < 0:

            self.direction = "SELL"

        else:

            self.direction = "NEUTRAL"
    # ------------------------------------------------------

    def classify_strength(self):

        m = abs(self.momentum)

        if m >= 20:

            self.strength = "VERY_STRONG"

            self.score = 100

        elif m >= 15:

            self.strength = "STRONG"

            self.score = 85

        elif m >= 10:

            self.strength = "MEDIUM"

            self.score = 70

        elif m >= 5:

            self.strength = "WEAK"

            self.score = 55

        else:

            self.strength = "FLAT"

            self.score = 35
    # ------------------------------------------------------

    def center_cross(

        self,

        current,

        previous,

    ):

        if previous < 50 <= current:

            self.score += 5

            self.reasons.append(

                "Bull Center Cross"

            )

        elif previous > 50 >= current:

            self.score += 5

            self.reasons.append(

                "Bear Center Cross"

            )
    # ------------------------------------------------------

    def detect_weakening(

        self,

        current,

        previous,

    ):

        if abs(current) < abs(previous):

            self.score -= 5

            self.reasons.append(

                "Momentum Weakening"

            )
    # ------------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # ------------------------------------------------------

    def report(self):

        return {

            "engine":

                "RSI Momentum",

            "direction":

                self.direction,

            "momentum":

                round(

                    self.momentum,

                    2,

                ),

            "strength":

                self.strength,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"RSI Momentum",

"direction":"BUY",

"momentum":17.42,

"strength":"STRONG",

"score":90,

"reasons":[

"Bull Center Cross"

]

}
momentum = momentum_engine.report()

internal_score += momentum["score"] * 0.10
class RSIMomentumPersistence:

    def __init__(self):

        self.persistence = 0

        self.score = 0

        self.direction = "NONE"

        self.reasons = []
def calculate(

    self,

    momentum_series,

):

    if len(momentum_series) == 0:

        return

    last = np.sign(momentum_series.iloc[-1])

    count = 0

    for value in reversed(momentum_series):

        if np.sign(value) == last:

            count += 1

        else:

            break

    self.persistence = count
def score_persistence(self):

    p = self.persistence

    if p >= 10:

        self.score = 100

    elif p >= 8:

        self.score = 90

    elif p >= 6:

        self.score = 80

    elif p >= 4:

        self.score = 65

    elif p >= 2:

        self.score = 50

    else:

        self.score = 30
def detect_direction(

    self,

    last_momentum,

):

    if last_momentum > 0:

        self.direction = "BUY"

    elif last_momentum < 0:

        self.direction = "SELL"

    else:

        self.direction = "NEUTRAL"
def report(self):

    return {

        "engine":

            "Momentum Persistence",

        "direction":

            self.direction,

        "persistence":

            self.persistence,

        "score":

            self.score,

        "reasons":

            self.reasons,

    }
{

"engine":"Momentum Persistence",

"direction":"BUY",

"persistence":9,

"score":90

}
momentum_score = (

    momentum_score * 0.7 +

    persistence_score * 0.3

)
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 10
# RSI VELOCITY ENGINE
# ==========================================================

import numpy as np

class RSIVelocityEngine:

    def __init__(self):

        self.reset()

    # -----------------------------------------------------

    def reset(self):

        self.velocity = 0

        self.direction = "NONE"

        self.score = 0

        self.level = "UNKNOWN"

        self.reasons = []
    # -----------------------------------------------------

    def calculate(

        self,

        rsi,

        period=5,

    ):

        if len(rsi) < period:

            return 0

        diff = np.diff(

            rsi.tail(period)

        )

        self.velocity = np.mean(diff)

        return self.velocity
    # -----------------------------------------------------

    def detect_direction(self):

        if self.velocity > 0:

            self.direction = "BUY"

        elif self.velocity < 0:

            self.direction = "SELL"

        else:

            self.direction = "NEUTRAL"
    # -----------------------------------------------------

    def classify(self):

        v = abs(self.velocity)

        if v >= 6:

            self.level = "EXTREME"

            self.score = 100

        elif v >= 4:

            self.level = "VERY_FAST"

            self.score = 90

        elif v >= 3:

            self.level = "FAST"

            self.score = 80

        elif v >= 2:

            self.level = "NORMAL"

            self.score = 65

        elif v >= 1:

            self.level = "SLOW"

            self.score = 45

        else:

            self.level = "FLAT"

            self.score = 20
    # -----------------------------------------------------

    def weakening(

        self,

        current,

        previous,

    ):

        if abs(current) < abs(previous):

            self.score -= 5

            self.reasons.append(

                "Velocity Weakening"

            )
    # -----------------------------------------------------

    def strengthening(

        self,

        current,

        previous,

    ):

        if abs(current) > abs(previous):

            self.score += 5

            self.reasons.append(

                "Velocity Increasing"

            )
    # -----------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # -----------------------------------------------------

    def report(self):

        return {

            "engine":"RSI Velocity",

            "direction":self.direction,

            "velocity":

                round(

                    self.velocity,

                    2,

                ),

            "level":

                self.level,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"RSI Velocity",

"direction":"BUY",

"velocity":4.82,

"level":"VERY_FAST",

"score":95,

"reasons":[

"Velocity Increasing"

]

}
velocity = velocity_engine.report()

internal_score += velocity["score"] * 0.08
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 10-2
# VELOCITY PERSISTENCE ENGINE
# ==========================================================

import numpy as np

class RSIVelocityPersistence:

    def __init__(self):

        self.reset()

    # -----------------------------------------------------

    def reset(self):

        self.persistence = 0

        self.direction = "NONE"

        self.score = 0

        self.reasons = []
    # -----------------------------------------------------

    def calculate(

        self,

        velocity_series,

    ):

        if len(velocity_series) == 0:

            return

        last_sign = np.sign(

            velocity_series.iloc[-1]

        )

        count = 0

        for value in reversed(

            velocity_series

        ):

            if np.sign(value) == last_sign:

                count += 1

            else:

                break

        self.persistence = count
    # -----------------------------------------------------

    def detect_direction(

        self,

        last_velocity,

    ):

        if last_velocity > 0:

            self.direction = "BUY"

        elif last_velocity < 0:

            self.direction = "SELL"

        else:

            self.direction = "NEUTRAL"
    # -----------------------------------------------------

    def calculate_score(self):

        p = self.persistence

        if p >= 12:

            self.score = 100

        elif p >= 10:

            self.score = 95

        elif p >= 8:

            self.score = 90

        elif p >= 6:

            self.score = 80

        elif p >= 4:

            self.score = 65

        elif p >= 2:

            self.score = 45

        else:

            self.score = 20
    # -----------------------------------------------------

    def detect_decay(

        self,

        velocity_series,

    ):

        if len(velocity_series) < 4:

            return

        last4 = velocity_series.tail(4).values

        if all(

            last4[i] > last4[i+1]

            for i in range(3)

        ):

            self.score -= 10

            self.reasons.append(

                "Velocity Decay"

            )
    # -----------------------------------------------------

    def detect_acceleration(

        self,

        velocity_series,

    ):

        if len(velocity_series) < 4:

            return

        last4 = velocity_series.tail(4).values

        if all(

            last4[i] < last4[i+1]

            for i in range(3)

        ):

            self.score += 10

            self.reasons.append(

                "Velocity Acceleration"

            )
    # -----------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # -----------------------------------------------------

    def report(self):

        return {

            "engine":

                "Velocity Persistence",

            "direction":

                self.direction,

            "persistence":

                self.persistence,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"Velocity Persistence",

"direction":"BUY",

"persistence":9,

"score":90,

"reasons":[

"Velocity Acceleration"

]

}
velocity_persistence = velocity_persistence_engine.report()

internal_score += velocity_persistence["score"] * 0.05
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 11
# COMPRESSION EXPANSION ENGINE
# ==========================================================

import numpy as np


class RSICompressionEngine:

    def __init__(self):

        self.reset()

    # -----------------------------------------------------

    def reset(self):

        self.range = 0

        self.state = "NORMAL"

        self.direction = "NONE"

        self.score = 0

        self.reasons = []
    # -----------------------------------------------------

    def calculate_range(

        self,

        rsi,

        length=14,

    ):

        if len(rsi) < length:

            return

        window = rsi.tail(length)

        self.range = (

            window.max()

            -

            window.min()

        )
    # -----------------------------------------------------

    def classify(self):

        r = self.range

        if r <= 5:

            self.state = "VERY_HIGH_COMPRESSION"

            self.score = 100

        elif r <= 8:

            self.state = "HIGH_COMPRESSION"

            self.score = 90

        elif r <= 15:

            self.state = "NORMAL"

            self.score = 60

        elif r <= 25:

            self.state = "HIGH_EXPANSION"

            self.score = 80

        else:

            self.state = "VERY_HIGH_EXPANSION"

            self.score = 95
    # -----------------------------------------------------

    def detect_direction(

        self,

        velocity,

    ):

        if velocity > 0:

            self.direction = "BUY"

        elif velocity < 0:

            self.direction = "SELL"

        else:

            self.direction = "NONE"
    # -----------------------------------------------------

    def breakout(

        self,

        previous_state,

    ):

        if (

            previous_state ==

            "VERY_HIGH_COMPRESSION"

            and

            self.state ==

            "HIGH_EXPANSION"

        ):

            self.score += 10

            self.reasons.append(

                "Compression Breakout"

            )
    # -----------------------------------------------------

    def weak_expansion(

        self,

        velocity,

    ):

        if (

            self.state ==

            "HIGH_EXPANSION"

            and

            abs(velocity) < 1

        ):

            self.score -= 10

            self.reasons.append(

                "Weak Expansion"

            )
    # -----------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # -----------------------------------------------------

    def report(self):

        return {

            "engine":

                "RSI Compression",

            "state":

                self.state,

            "direction":

                self.direction,

            "range":

                round(

                    self.range,

                    2,

                ),

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"RSI Compression",

"state":"VERY_HIGH_COMPRESSION",

"direction":"BUY",

"range":4.8,

"score":100,

"reasons":[

"Compression Breakout"

]

}
compression = compression_engine.report()

internal_score += compression["score"] * 0.08
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 12
# RSI PIVOT QUALITY ENGINE
# ==========================================================

class RSIPivotQualityEngine:

    def __init__(self):

        self.reset()

    # -------------------------------------------------

    def reset(self):

        self.score = 0

        self.grade = "UNKNOWN"

        self.reasons = []
    # -------------------------------------------------

    def candle_distance(

        self,

        distance,

    ):

        if 10 <= distance <= 40:

            self.score += 20

            self.reasons.append(

                "Healthy Candle Distance"

            )

        elif 5 <= distance < 10:

            self.score += 10

        else:

            self.score += 3
    # -------------------------------------------------

    def rsi_distance(

        self,

        value,

    ):

        if value >= 20:

            self.score += 20

        elif value >= 15:

            self.score += 15

        elif value >= 10:

            self.score += 10

        elif value >= 5:

            self.score += 5
    # -------------------------------------------------

    def noise(

        self,

        std,

    ):

        if std <= 2:

            self.score += 15

            self.reasons.append(

                "Low Noise"

            )

        elif std <= 4:

            self.score += 8

        else:

            self.score += 2
    # -------------------------------------------------

    def symmetry(

        self,

        left,

        right,

    ):

        diff = abs(

            left -

            right

        )

        if diff <= 2:

            self.score += 15

            self.reasons.append(

                "Good Symmetry"

            )

        elif diff <= 5:

            self.score += 8
    # -------------------------------------------------

    def fake_break(

        self,

        fake,

    ):

        if fake:

            self.score -= 20

            self.reasons.append(

                "Fake Pivot"

            )
    # -------------------------------------------------

    def classify(self):

        s = self.score

        if s >= 90:

            self.grade = "A+"

        elif s >= 80:

            self.grade = "A"

        elif s >= 70:

            self.grade = "B"

        elif s >= 60:

            self.grade = "C"

        else:

            self.grade = "D"
    # -------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),
        )
    # -------------------------------------------------

    def report(self):

        return {

            "engine":

                "RSI Pivot Quality",

            "score":

                self.score,

            "grade":

                self.grade,

            "reasons":

                self.reasons,

        }
{

"engine":"RSI Pivot Quality",

"score":91,

"grade":"A+",

"reasons":[

"Healthy Candle Distance",

"Low Noise",

"Good Symmetry"

]

}
pivot_quality = pivot_quality_engine.report()

internal_score += pivot_quality["score"] * 0.07
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 13
# INTERNAL CONFLICT ENGINE
# ==========================================================

class RSIConflictEngine:

    def __init__(self):

        self.reset()

    # -------------------------------------------------

    def reset(self):

        self.buy_votes = 0

        self.sell_votes = 0

        self.neutral_votes = 0

        self.score = 100

        self.reasons = []

        self.state = "UNKNOWN"
    # -------------------------------------------------

    def register(

        self,

        direction,

    ):

        if direction == "BUY":

            self.buy_votes += 1

        elif direction == "SELL":

            self.sell_votes += 1

        else:

            self.neutral_votes += 1
    # -------------------------------------------------

    def detect(self):

        total = (

            self.buy_votes +

            self.sell_votes

        )

        if total == 0:

            self.state = "NO_SIGNAL"

            self.score = 0

            return

        difference = abs(

            self.buy_votes -

            self.sell_votes

        )

        if difference >= 6:

            self.state = "VERY_STRONG"

            self.score = 100

        elif difference >= 4:

            self.state = "STRONG"

            self.score = 90

        elif difference >= 2:

            self.state = "NORMAL"

            self.score = 75

        else:

            self.state = "CONFLICT"

            self.score = 45

            self.reasons.append(

                "Internal Conflict"

            )
    # -------------------------------------------------

    def severe_conflict(self):

        if (

            self.buy_votes >= 4

            and

            self.sell_votes >= 4

        ):

            self.score -= 20

            self.reasons.append(

                "Severe Conflict"

            )
    # -------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # -------------------------------------------------

    def report(self):

        return {

            "engine":

                "RSI Conflict",

            "buy_votes":

                self.buy_votes,

            "sell_votes":

                self.sell_votes,

            "neutral":

                self.neutral_votes,

            "state":

                self.state,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"RSI Conflict",

"buy_votes":8,

"sell_votes":1,

"neutral":2,

"state":"VERY_STRONG",

"score":100

}
{

"engine":"RSI Conflict",

"buy_votes":5,

"sell_votes":5,

"neutral":1,

"state":"CONFLICT",

"score":40,

"reasons":[

"Internal Conflict",

"Severe Conflict"

]

}
conflict = conflict_engine.report()

internal_score += conflict["score"] * 0.10
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 14
# SIGNAL QUALITY ENGINE
# ==========================================================

class RSISignalQualityEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------------

    def reset(self):

        self.score = 0

        self.grade = "UNKNOWN"

        self.confidence = 0

        self.reasons = []

        self.valid = True
    # ------------------------------------------------------

    def calculate(

        self,

        engine_scores,

    ):

        """
        engine_scores

        list

        of

        internal

        scores

        """

        if len(engine_scores) == 0:

            self.valid = False

            return

        self.score = (

            sum(engine_scores)

            /

            len(engine_scores)

        )
    # ------------------------------------------------------

    def apply_conflict(

        self,

        conflict_score,

    ):

        if conflict_score < 50:

            self.score *= 0.80

            self.reasons.append(

                "Internal Conflict"

            )
    # ------------------------------------------------------

    def apply_pivot_quality(

        self,

        pivot_score,

    ):

        if pivot_score < 60:

            self.score *= 0.90

            self.reasons.append(

                "Weak Pivot"

            )
    # ------------------------------------------------------

    def reward_alignment(

        self,

        aligned,

    ):

        if aligned:

            self.score += 5

            self.reasons.append(

                "High Alignment"

            )
    # ------------------------------------------------------

    def classify(self):

        s = self.score

        if s >= 95:

            self.grade = "A+"

        elif s >= 90:

            self.grade = "A"

        elif s >= 80:

            self.grade = "B"

        elif s >= 70:

            self.grade = "C"

        elif s >= 60:

            self.grade = "D"

        else:

            self.grade = "REJECT"
    # ------------------------------------------------------

    def calculate_confidence(self):

        self.confidence = self.score
    # ------------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )

        self.confidence = max(

            0,

            min(

                100,

                self.confidence,

            ),

        )
    # ------------------------------------------------------

    def report(self):

        return {

            "engine":

                "RSI Signal Quality",

            "score":

                round(

                    self.score,

                    2,

                ),

            "grade":

                self.grade,

            "confidence":

                round(

                    self.confidence,

                    2,

                ),

            "valid":

                self.valid,

            "reasons":

                self.reasons,

        }
{

"engine":"RSI Signal Quality",

"score":91.4,

"grade":"A",

"confidence":91.4,

"valid":True,

"reasons":[

"High Alignment"

]

}
signal_quality = signal_quality_engine.report()

internal_score += signal_quality["score"] * 0.10
# ==========================================================
# RSI ENTERPRISE ENGINE
# SECTION 15
# STANDARD OUTPUT ENGINE
# ==========================================================

class RSIOutputEngine:

    def create(

        self,

        signal_direction,

        engine_score,

        weight,

        confidence,

        grade,

        reasons,

        warnings,

        market_state,

        valid,

    ):

        final_score = (

            engine_score *

            weight /

            100

        )

        return {

            "engine":

                "RSI",

            "direction":

                signal_direction,

            "engine_score":

                round(

                    engine_score,

                    2,

                ),

            "weight":

                weight,

            "final_score":

                round(

                    final_score,

                    2,

                ),

            "confidence":

                round(

                    confidence,

                    2,

                ),

            "grade":

                grade,

            "market_state":

                market_state,

            "valid":

                valid,

            "reasons":

                reasons,

            "warnings":

                warnings,

        }
{

"engine":"RSI",

"direction":"BUY",

"engine_score":84,

"weight":20,

"final_score":16.8,

"confidence":91,

"grade":"A",

"market_state":"TREND",

"valid":True,

"reasons":[

"Regular Divergence",

"Momentum Strong",

"Velocity Increasing",

"Compression Breakout"

],

"warnings":[

"Hidden Divergence Missing"

]

}
class ScoreNormalizer:

    def __init__(self):

        pass
def normalize(

    self,

    score,

):

    return max(

        0,

        min(

            100,

            score,

        ),

    )
def apply_weight(

    self,

    score,

    weight,

):

    score = self.normalize(score)

    final = (

        score *

        weight

    ) / 100

    return round(

        final,

        2,

    )
def validate_weight(

    self,

    weight,

):

    if weight < 0:

        raise ValueError

    if weight > 100:

        raise ValueError
def validate_engine_score(

    self,

    score,

):

    return self.normalize(score)
def report(

    self,

    engine,

    score,

    weight,

):

    final = self.apply_weight(

        score,

        weight,

    )

    return {

        "engine":

            engine,

        "engine_score":

            score,

        "weight":

            weight,

        "final_score":

            final,

    }
{

"engine":"RSI",

"engine_score":84,

"weight":20,

"final_score":16.8

}