# ==========================================================
# AO ENTERPRISE ENGINE
# SECTION 1
# DATA VALIDATION ENGINE
# ==========================================================

import pandas as pd
import numpy as np


class AODataValidator:

    def __init__(self):

        self.reset()

    # ------------------------------------------------------

    def reset(self):

        self.valid = True

        self.score = 100

        self.reasons = []

        self.warnings = []
    # ------------------------------------------------------

    def validate_columns(

        self,

        df,

    ):

        required = [

            "High",

            "Low",

            "Close",

        ]

        for col in required:

            if col not in df.columns:

                self.valid = False

                self.score = 0

                self.reasons.append(

                    f"Missing {col}"

                )
    # ------------------------------------------------------

    def validate_nan(

        self,

        df,

    ):

        if df.isnull().sum().sum() > 0:

            self.score -= 20

            self.warnings.append(

                "NaN Detected"

            )
    # ------------------------------------------------------

    def validate_time(

        self,

        df,

    ):

        if "Time" not in df.columns:

            return

        if not df["Time"].is_monotonic_increasing:

            self.score -= 15

            self.warnings.append(

                "Time Disorder"

            )
    # ------------------------------------------------------

    def validate_duplicate(

        self,

        df,

    ):

        if "Time" not in df.columns:

            return

        duplicated = df["Time"].duplicated().sum()

        if duplicated:

            self.score -= 10

            self.warnings.append(

                "Duplicate Candle"

            )
    # ------------------------------------------------------

    def validate_length(

        self,

        df,

    ):

        if len(df) < 50:

            self.valid = False

            self.score = 0

            self.reasons.append(

                "Not Enough Candles"

            )
    # ------------------------------------------------------

    def validate_prices(

        self,

        df,

    ):

        invalid = (

            df["High"] <

            df["Low"]

        ).sum()

        if invalid:

            self.score -= 20

            self.reasons.append(

                "Invalid High Low"

            )
    # ------------------------------------------------------

    def detect_spike(

        self,

        df,

    ):

        rng = (

            df["High"]

            -

            df["Low"]

        )

        avg = rng.mean()

        spikes = (

            rng >

            avg * 8

        ).sum()

        if spikes:

            self.warnings.append(

                "Possible Spike"

            )

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

            "engine": "AO Validator",

            "valid": self.valid,

            "score": self.score,

            "reasons": self.reasons,

            "warnings": self.warnings,

        }
{

"engine":"AO Validator",

"valid":True,

"score":95,

"reasons":[],

"warnings":[

"Possible Spike"

]

}
# ==========================================================
# AO ENTERPRISE ENGINE
# SECTION 2
# AO CALCULATION ENGINE
# ==========================================================

import pandas as pd
import numpy as np


class AOCalculator:

    def __init__(self):

        self.reset()

    # ------------------------------------------------------

    def reset(self):

        self.valid = True

        self.reasons = []

        self.df = None
    # ------------------------------------------------------

    def calculate_median_price(

        self,

        df,

    ):

        df["MedianPrice"] = (

            df["High"]

            +

            df["Low"]

        ) / 2

        return df
    # ------------------------------------------------------

    def calculate_fast_ma(

        self,

        df,

    ):

        df["AO_FAST"] = (

            df["MedianPrice"]

            .rolling(

                window=5,

            )

            .mean()

        )

        return df
    # ------------------------------------------------------

    def calculate_slow_ma(

        self,

        df,

    ):

        df["AO_SLOW"] = (

            df["MedianPrice"]

            .rolling(

                window=34,

            )

            .mean()

        )

        return df
    # ------------------------------------------------------

    def calculate_ao(

        self,

        df,

    ):

        df["AO"] = (

            df["AO_FAST"]

            -

            df["AO_SLOW"]

        )

        return df
    # ------------------------------------------------------

    def clean(

        self,

        df,

    ):

        df = df.copy()

        df = df.dropna()

        return df
    # ------------------------------------------------------

    def run(

        self,

        df,

    ):

        df = self.calculate_median_price(df)

        df = self.calculate_fast_ma(df)

        df = self.calculate_slow_ma(df)

        df = self.calculate_ao(df)

        df = self.clean(df)

        self.df = df

        return df
    # ------------------------------------------------------

    def report(self):

        return {

            "engine":

                "AO Calculation",

            "valid":

                self.valid,

            "rows":

                len(self.df),

            "columns":

                list(self.df.columns),

        }
{

"engine":"AO Calculation",

"valid":True,

"rows":1450,

"columns":[

"High",

"Low",

"Close",

"MedianPrice",

"AO_FAST",

"AO_SLOW",

"AO"

]

}
# ==========================================================
# AO ENTERPRISE ENGINE
# SECTION 3
# ZERO LINE ENGINE
# ==========================================================

import numpy as np


class AOZeroLineEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.position = "UNKNOWN"

        self.score = 0

        self.cross = False

        self.reasons = []
    # ------------------------------------------------------

    def detect_position(

        self,

        current,

    ):

        if current > 0:

            self.position = "ABOVE"

            self.direction = "BUY"

        elif current < 0:

            self.position = "BELOW"

            self.direction = "SELL"

        else:

            self.position = "ZERO"

            self.direction = "NEUTRAL"
    # ------------------------------------------------------

    def detect_cross(

        self,

        previous,

        current,

    ):

        if previous < 0 <= current:

            self.cross = True

            self.direction = "BUY"

            self.score += 30

            self.reasons.append(

                "Bull Zero Cross"

            )

        elif previous > 0 >= current:

            self.cross = True

            self.direction = "SELL"

            self.score += 30

            self.reasons.append(

                "Bear Zero Cross"

            )
    # ------------------------------------------------------

    def cross_strength(

        self,

        current,

    ):

        value = abs(current)

        if value >= 2:

            self.score += 25

        elif value >= 1:

            self.score += 15

        elif value >= 0.5:

            self.score += 8

        else:

            self.score += 3
    # ------------------------------------------------------

    def persistence(

        self,

        ao_series,

    ):

        last_sign = np.sign(

            ao_series.iloc[-1]

        )

        count = 0

        for value in reversed(ao_series):

            if np.sign(value) == last_sign:

                count += 1

            else:

                break

        if count >= 10:

            self.score += 20

        elif count >= 6:

            self.score += 15

        elif count >= 3:

            self.score += 8
    # ------------------------------------------------------

    def fake_cross(

        self,

        ao_series,

    ):

        if len(ao_series) < 3:

            return

        last = ao_series.iloc[-1]

        prev = ao_series.iloc[-2]

        prev2 = ao_series.iloc[-3]

        if (

            np.sign(prev2)

            !=

            np.sign(prev)

            and

            np.sign(prev2)

            ==

            np.sign(last)

        ):

            self.score -= 20

            self.reasons.append(

                "Fake Zero Cross"

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

                "AO Zero Line",

            "direction":

                self.direction,

            "position":

                self.position,

            "cross":

                self.cross,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"AO Zero Line",

"direction":"BUY",

"position":"ABOVE",

"cross":True,

"score":86,

"reasons":[

"Bull Zero Cross"

]

}
zero = zero_line_engine.report()

internal_score += zero["score"] * 0.15
# ==========================================================
# AO ENTERPRISE ENGINE
# SECTION 4
# TWIN PEAKS ENGINE
# ==========================================================

import numpy as np

class AOTwinPeaksEngine:

    def __init__(self):

        self.reset()

    # -----------------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.pattern = False

        self.score = 0

        self.reasons = []
    # -----------------------------------------------------

    def detect_peaks(

        self,

        ao,

    ):

        peaks = []

        for i in range(1, len(ao)-1):

            if ao.iloc[i] > ao.iloc[i-1] and ao.iloc[i] > ao.iloc[i+1]:

                peaks.append(i)

        return peaks
    # -----------------------------------------------------

    def detect_bottoms(

        self,

        ao,

    ):

        bottoms = []

        for i in range(1, len(ao)-1):

            if ao.iloc[i] < ao.iloc[i-1] and ao.iloc[i] < ao.iloc[i+1]:

                bottoms.append(i)

        return bottoms
    # -----------------------------------------------------

    def bullish(

        self,

        ao,

        bottoms,

    ):

        if len(bottoms) < 2:

            return

        b1 = bottoms[-2]

        b2 = bottoms[-1]

        if (

            ao.iloc[b1] < 0

            and

            ao.iloc[b2] < 0

            and

            ao.iloc[b2] >

            ao.iloc[b1]

        ):

            self.pattern = True

            self.direction = "BUY"

            self.score += 90

            self.reasons.append(

                "Bullish Twin Peaks"

            )
    # -----------------------------------------------------

    def bearish(

        self,

        ao,

        peaks,

    ):

        if len(peaks) < 2:

            return

        p1 = peaks[-2]

        p2 = peaks[-1]

        if (

            ao.iloc[p1] > 0

            and

            ao.iloc[p2] > 0

            and

            ao.iloc[p2] <

            ao.iloc[p1]

        ):

            self.pattern = True

            self.direction = "SELL"

            self.score += 90

            self.reasons.append(

                "Bearish Twin Peaks"

            )
    # -----------------------------------------------------

    def quality(

        self,

        distance,

    ):

        if distance >= 8:

            self.score += 10

        elif distance >= 5:

            self.score += 5
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

            "engine":"AO Twin Peaks",

            "pattern":self.pattern,

            "direction":self.direction,

            "score":self.score,

            "reasons":self.reasons,

        }
{

"engine":"AO Twin Peaks",

"pattern":True,

"direction":"BUY",

"score":95,

"reasons":[

"Bullish Twin Peaks"

]

}
# ==========================================================
# AO ENTERPRISE ENGINE
# SECTION 5-1
# BULLISH SAUCER
# ==========================================================

class BullishSaucerEngine:

    def __init__(self):

        self.reset()

    # ----------------------------------------------------

    def reset(self):

        self.pattern = False

        self.direction = "NONE"

        self.score = 0

        self.reasons = []
    # ----------------------------------------------------

    def above_zero(

        self,

        ao,

    ):

        return (

            ao.iloc[-4:] > 0

        ).all()
    # ----------------------------------------------------

    def two_red(

        self,

        ao,

    ):

        return (

            ao.iloc[-3]

            <

            ao.iloc[-4]

        ) and (

            ao.iloc[-2]

            <

            ao.iloc[-3]

        )
    # ----------------------------------------------------

    def green_bar(

        self,

        ao,

    ):

        return (

            ao.iloc[-1]

            >

            ao.iloc[-2]

        )
    # ----------------------------------------------------

    def validate_green(

        self,

        ao,

    ):

        return (

            ao.iloc[-1]

            >

            ao.iloc[-2]

        )
    # ----------------------------------------------------

    def detect(

        self,

        ao,

    ):

        if not self.above_zero(ao):

            return

        if not self.two_red(ao):

            return

        if not self.green_bar(ao):

            return

        if not self.validate_green(ao):

            return

        self.pattern = True

        self.direction = "BUY"

        self.score = 85

        self.reasons.append(

            "Bullish Saucer"

        )
    # ----------------------------------------------------

    def bonus(

        self,

        velocity,

    ):

        if velocity > 2:

            self.score += 5

            self.reasons.append(

                "Strong Velocity"

            )
    # ----------------------------------------------------

    def weak_volume(

        self,

        volume_ok,

    ):

        if not volume_ok:

            self.score -= 5

            self.reasons.append(

                "Weak Volume"

            )
    # ----------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),
        )
    # ----------------------------------------------------

    def report(self):

        return {

            "engine":

                "Bullish Saucer",

            "pattern":

                self.pattern,

            "direction":

                self.direction,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"Bullish Saucer",

"pattern":True,

"direction":"BUY",

"score":90,

"reasons":[

"Bullish Saucer",

"Strong Velocity"

]

}
# ==========================================================
# AO ENTERPRISE ENGINE
# SECTION 5-2
# BEARISH SAUCER
# ==========================================================

class BearishSaucerEngine:

    def __init__(self):

        self.reset()

    # ----------------------------------------------------

    def reset(self):

        self.pattern = False

        self.direction = "NONE"

        self.score = 0

        self.reasons = []
    # ----------------------------------------------------

    def below_zero(

        self,

        ao,

    ):

        return (

            ao.iloc[-4:] < 0

        ).all()
    # ----------------------------------------------------

    def two_green(

        self,

        ao,

    ):

        return (

            ao.iloc[-3]

            >

            ao.iloc[-4]

        ) and (

            ao.iloc[-2]

            >

            ao.iloc[-3]

        )
    # ----------------------------------------------------

    def red_bar(

        self,

        ao,

    ):

        return (

            ao.iloc[-1]

            <

            ao.iloc[-2]

        )
    # ----------------------------------------------------

    def validate_red(

        self,

        ao,

    ):

        return (

            ao.iloc[-1]

            <

            ao.iloc[-2]

        )
    # ----------------------------------------------------

    def detect(

        self,

        ao,

    ):

        if not self.below_zero(ao):

            return

        if not self.two_green(ao):

            return

        if not self.red_bar(ao):

            return

        if not self.validate_red(ao):

            return

        self.pattern = True

        self.direction = "SELL"

        self.score = 85

        self.reasons.append(

            "Bearish Saucer"

        )
    # ----------------------------------------------------

    def bonus(

        self,

        velocity,

    ):

        if velocity < -2:

            self.score += 5

            self.reasons.append(

                "Strong Down Velocity"

            )
    # ----------------------------------------------------

    def weak_volume(

        self,

        volume_ok,

    ):

        if not volume_ok:

            self.score -= 5

            self.reasons.append(

                "Weak Volume"

            )
    # ----------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # ----------------------------------------------------

    def report(self):

        return {

            "engine":

                "Bearish Saucer",

            "pattern":

                self.pattern,

            "direction":

                self.direction,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"Bearish Saucer",

"pattern":True,

"direction":"SELL",

"score":90,

"reasons":[

"Bearish Saucer",

"Strong Down Velocity"

]

}
# ==========================================================
# AO ENTERPRISE ENGINE
# SECTION 5-3
# REGULAR BULLISH DIVERGENCE
# ==========================================================

class AORegularBullishDivergence:

    def __init__(self):

        self.reset()

    # --------------------------------------------------

    def reset(self):

        self.pattern = False

        self.direction = "NONE"

        self.score = 0

        self.reasons = []
    # --------------------------------------------------

    def price_condition(

        self,

        price1,

        price2,

    ):

        return (

            price2 < price1

        )
    # --------------------------------------------------

    def ao_condition(

        self,

        ao1,

        ao2,

    ):

        return (

            ao2 > ao1

        )
    # --------------------------------------------------

    def detect(

        self,

        price1,

        price2,

        ao1,

        ao2,

    ):

        if not self.price_condition(

            price1,

            price2,

        ):

            return

        if not self.ao_condition(

            ao1,

            ao2,

        ):

            return

        self.pattern = True

        self.direction = "BUY"

        self.score = 90

        self.reasons.append(

            "Regular Bullish Divergence"

        )
    # --------------------------------------------------

    def strength(

        self,

        ao1,

        ao2,

    ):

        diff = abs(

            ao2 - ao1

        )

        if diff >= 2:

            self.score += 5

        elif diff >= 1:

            self.score += 3
    # --------------------------------------------------

    def candle_distance(

        self,

        distance,

    ):

        if 8 <= distance <= 30:

            self.score += 5

        elif distance < 4:

            self.score -= 5

            self.reasons.append(

                "Short Distance"

            )
    # --------------------------------------------------

    def pivot_quality(

        self,

        pivot_score,

    ):

        if pivot_score < 60:

            self.score -= 10

            self.reasons.append(

                "Weak Pivot"

            )
    # --------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # --------------------------------------------------

    def report(self):

        return {

            "engine":

                "AO Regular Bullish Divergence",

            "pattern":

                self.pattern,

            "direction":

                self.direction,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"AO Regular Bullish Divergence",

"pattern":True,

"direction":"BUY",

"score":97,

"reasons":[

"Regular Bullish Divergence"

]

}
# ==========================================================
# AO ENTERPRISE ENGINE
# SECTION 5-4
# REGULAR BEARISH DIVERGENCE
# ==========================================================

class AORegularBearishDivergence:

    def __init__(self):

        self.reset()

    # --------------------------------------------------

    def reset(self):

        self.pattern = False

        self.direction = "NONE"

        self.score = 0

        self.reasons = []
    # --------------------------------------------------

    def price_condition(

        self,

        price1,

        price2,

    ):

        return (

            price2 >

            price1

        )
    # --------------------------------------------------

    def ao_condition(

        self,

        ao1,

        ao2,

    ):

        return (

            ao2 <

            ao1

        )
    # --------------------------------------------------

    def detect(

        self,

        price1,

        price2,

        ao1,

        ao2,

    ):

        if not self.price_condition(

            price1,

            price2,

        ):

            return

        if not self.ao_condition(

            ao1,

            ao2,

        ):

            return

        self.pattern = True

        self.direction = "SELL"

        self.score = 90

        self.reasons.append(

            "Regular Bearish Divergence"

        )
    # --------------------------------------------------

    def strength(

        self,

        ao1,

        ao2,

    ):

        diff = abs(

            ao1 -

            ao2

        )

        if diff >= 2:

            self.score += 5

        elif diff >= 1:

            self.score += 3
    # --------------------------------------------------

    def candle_distance(

        self,

        distance,

    ):

        if 8 <= distance <= 30:

            self.score += 5

        elif distance < 4:

            self.score -= 5

            self.reasons.append(

                "Short Distance"

            )
    # --------------------------------------------------

    def pivot_quality(

        self,

        pivot_score,

    ):

        if pivot_score < 60:

            self.score -= 10

            self.reasons.append(

                "Weak Pivot"

            )
    # --------------------------------------------------

    def weak_divergence(

        self,

        ao1,

        ao2,

    ):

        if abs(

            ao1 -

            ao2

        ) < 0.30:

            self.score -= 10

            self.reasons.append(

                "Weak Divergence"

            )
    # --------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),
        )
    # --------------------------------------------------

    def report(self):

        return {

            "engine":

                "AO Regular Bearish Divergence",

            "pattern":

                self.pattern,

            "direction":

                self.direction,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"AO Regular Bearish Divergence",

"pattern":True,

"direction":"SELL",

"score":95,

"reasons":[

"Regular Bearish Divergence"

]

}
# ==========================================================
# AO ENTERPRISE ENGINE
# SECTION 5-5
# HIDDEN BULLISH DIVERGENCE
# ==========================================================

class AOHiddenBullishDivergence:

    def __init__(self):

        self.reset()

    # --------------------------------------------------

    def reset(self):

        self.pattern = False

        self.direction = "NONE"

        self.score = 0

        self.reasons = []
    # --------------------------------------------------

    def trend_filter(

        self,

        trend,

    ):

        return (

            trend == "UP"

        )
    # --------------------------------------------------

    def price_condition(

        self,

        price1,

        price2,

    ):

        return (

            price2 >

            price1

        )
    # --------------------------------------------------

    def ao_condition(

        self,

        ao1,

        ao2,

    ):

        return (

            ao2 <

            ao1

        )
    # --------------------------------------------------

    def detect(

        self,

        trend,

        price1,

        price2,

        ao1,

        ao2,

    ):

        if not self.trend_filter(

            trend,

        ):

            return

        if not self.price_condition(

            price1,

            price2,

        ):

            return

        if not self.ao_condition(

            ao1,

            ao2,

        ):

            return

        self.pattern = True

        self.direction = "BUY"

        self.score = 88

        self.reasons.append(

            "Hidden Bullish Divergence"

        )
    # --------------------------------------------------

    def quality(

        self,

        diff,

    ):

        if diff >= 2:

            self.score += 5

        elif diff >= 1:

            self.score += 3
    # --------------------------------------------------

    def candle_distance(

        self,

        distance,

    ):

        if 8 <= distance <= 30:

            self.score += 5

        elif distance < 4:

            self.score -= 5

            self.reasons.append(

                "Short Distance"

            )
    # --------------------------------------------------

    def pivot_quality(

        self,

        pivot_score,

    ):

        if pivot_score < 60:

            self.score -= 10

            self.reasons.append(

                "Weak Pivot"

            )
    # --------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # --------------------------------------------------

    def report(self):

        return {

            "engine":

                "AO Hidden Bullish Divergence",

            "pattern":

                self.pattern,

            "direction":

                self.direction,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"AO Hidden Bullish Divergence",

"pattern":True,

"direction":"BUY",

"score":93,

"reasons":[

"Hidden Bullish Divergence"

]

}
# ==========================================================
# AO ENTERPRISE ENGINE
# SECTION 5-6
# HIDDEN BEARISH DIVERGENCE
# ==========================================================

class AOHiddenBearishDivergence:

    def __init__(self):

        self.reset()

    # ----------------------------------------------------

    def reset(self):

        self.pattern = False

        self.direction = "NONE"

        self.score = 0

        self.reasons = []
    # ----------------------------------------------------

    def trend_filter(

        self,

        trend,

    ):

        return (

            trend == "DOWN"

        )
    # ----------------------------------------------------

    def price_condition(

        self,

        price1,

        price2,

    ):

        return (

            price2 <

            price1

        )
    # ----------------------------------------------------

    def ao_condition(

        self,

        ao1,

        ao2,

    ):

        return (

            ao2 >

            ao1

        )
    # ----------------------------------------------------

    def detect(

        self,

        trend,

        price1,

        price2,

        ao1,

        ao2,

    ):

        if not self.trend_filter(

            trend,

        ):

            return

        if not self.price_condition(

            price1,

            price2,

        ):

            return

        if not self.ao_condition(

            ao1,

            ao2,

        ):

            return

        self.pattern = True

        self.direction = "SELL"

        self.score = 88

        self.reasons.append(

            "Hidden Bearish Divergence"

        )
    # ----------------------------------------------------

    def quality(

        self,

        diff,

    ):

        if diff >= 2:

            self.score += 5

        elif diff >= 1:

            self.score += 3
    # ----------------------------------------------------

    def candle_distance(

        self,

        distance,

    ):

        if 8 <= distance <= 30:

            self.score += 5

        elif distance < 4:

            self.score -= 5

            self.reasons.append(

                "Short Distance"

            )
    # ----------------------------------------------------

    def pivot_quality(

        self,

        pivot_score,

    ):

        if pivot_score < 60:

            self.score -= 10

            self.reasons.append(

                "Weak Pivot"

            )
    # ----------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # ----------------------------------------------------

    def report(self):

        return {

            "engine":

                "AO Hidden Bearish Divergence",

            "pattern":

                self.pattern,

            "direction":

                self.direction,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"AO Hidden Bearish Divergence",

"pattern":True,

"direction":"SELL",

"score":94,

"reasons":[

"Hidden Bearish Divergence"

]

}
# ==========================================================
# AO ENTERPRISE ENGINE
# SECTION 5-7
# DIVERGENCE STRENGTH ENGINE
# ==========================================================

class AODivergenceStrength:

    def __init__(self):

        self.reset()

    # ----------------------------------------------------

    def reset(self):

        self.score = 0

        self.reasons = []
    # ----------------------------------------------------

    def ao_difference(

        self,

        ao1,

        ao2,

    ):

        diff = abs(

            ao2 -

            ao1

        )

        if diff >= 3:

            self.score += 30

        elif diff >= 2:

            self.score += 25

        elif diff >= 1:

            self.score += 18

        elif diff >= 0.5:

            self.score += 10

        else:

            self.score += 3
    # ----------------------------------------------------

    def price_difference(

        self,

        p1,

        p2,

    ):

        diff = abs(

            p2 -

            p1

        )

        if diff >= 5:

            self.score += 25

        elif diff >= 3:

            self.score += 18

        elif diff >= 1:

            self.score += 10
    # ----------------------------------------------------

    def angle(

        self,

        angle,

    ):

        if angle >= 45:

            self.score += 20

        elif angle >= 30:

            self.score += 15

        elif angle >= 15:

            self.score += 8
    # ----------------------------------------------------

    def candle_distance(

        self,

        candles,

    ):

        if 8 <= candles <= 25:

            self.score += 15

        elif 5 <= candles <= 40:

            self.score += 10

        else:

            self.score += 5
    # ----------------------------------------------------

    def pivot_quality(

        self,

        pivot_score,

    ):

        self.score += (

            pivot_score *

            0.10

        )
    # ----------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                round(

                    self.score,

                    2,

                ),

            ),

        )
    # ----------------------------------------------------

    def report(self):

        return {

            "engine":

                "AO Divergence Strength",

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"AO Divergence Strength",

"score":92

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 5-8
# DIVERGENCE QUALITY ENGINE
# =====================================================

class AODivergenceQuality:

    def __init__(self):

        self.reset()

    # ------------------------------------------------

    def reset(self):

        self.score = 100

        self.reasons = []

        self.warning = []
    # ------------------------------------------------

    def pivot_quality(

        self,

        pivot_score,

    ):

        if pivot_score >= 90:

            return

        elif pivot_score >= 80:

            self.score -= 3

        elif pivot_score >= 70:

            self.score -= 8

        elif pivot_score >= 60:

            self.score -= 15

        else:

            self.score -= 30

            self.warning.append(

                "Weak Pivot"

            )
    # ------------------------------------------------

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

            return

        elif diff <= 5:

            self.score -= 5

        elif diff <= 8:

            self.score -= 10

        else:

            self.score -= 20

            self.warning.append(

                "Asymmetry"

            )
    # ------------------------------------------------

    def candle_distance(

        self,

        candles,

    ):

        if candles < 5:

            self.score -= 10

        elif candles > 40:

            self.score -= 10
    # ------------------------------------------------

    def noise(

        self,

        noise_score,

    ):

        if noise_score > 80:

            self.score -= 15

            self.warning.append(

                "High Noise"

            )
    # ------------------------------------------------

    def structure(

        self,

        confirmed,

    ):

        if confirmed:

            self.score += 5

        else:

            self.score -= 5
    # ------------------------------------------------

    def ao_strength(

        self,

        strength,

    ):

        if strength < 30:

            self.score -= 10

        elif strength > 80:

            self.score += 5
    # ------------------------------------------------

    def trend(

        self,

        trend_ok,

    ):

        if trend_ok:

            self.score += 5

        else:

            self.score -= 10
    # ------------------------------------------------

    def normalize(

        self,

    ):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # ------------------------------------------------

    def report(

        self,

    ):

        return {

            "engine":

                "AO Divergence Quality",

            "score":

                self.score,

            "warning":

                self.warning,

            "reasons":

                self.reasons,

        }
{

"engine":"AO Divergence Quality",

"score":91,

"warning":[

"Asymmetry"

]

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 5-9
# DIVERGENCE CONFLICT ENGINE
# =====================================================

class AODivergenceConflict:

    def __init__(self):

        self.reset()

    # -----------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.score = 0

        self.conflict = False

        self.reasons = []
    # -----------------------------------------------

    def agreement(

        self,

        regular,

        hidden,

    ):

        if regular == hidden:

            self.direction = regular

            self.score = 100

            self.reasons.append(

                "Agreement"

            )
    # -----------------------------------------------

    def disagreement(

        self,

        regular,

        hidden,

    ):

        if regular != hidden:

            self.conflict = True

            self.direction = "NONE"

            self.score = 40

            self.reasons.append(

                "Conflict"

            )
    # -----------------------------------------------

    def no_signal(

        self,

        regular,

        hidden,

    ):

        if (

            regular == "NONE"

            and

            hidden == "NONE"

        ):

            self.direction = "NONE"

            self.score = 0
    # -----------------------------------------------

    def quality(

        self,

        quality_score,

    ):

        self.score *= (

            quality_score

            /

            100

        )
    # -----------------------------------------------

    def normalize(

        self,

    ):

        self.score = max(

            0,

            min(

                100,

                round(

                    self.score,

                    2,

                ),

            ),

        )
    # -----------------------------------------------

    def report(

        self,

    ):

        return {

            "engine":

                "AO Divergence Conflict",

            "direction":

                self.direction,

            "conflict":

                self.conflict,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"AO Divergence Conflict",

"direction":"BUY",

"conflict":False,

"score":94,

"reasons":[

"Agreement"

]

}
{

"engine":"AO Divergence Conflict",

"direction":"NONE",

"conflict":True,

"score":40,

"reasons":[

"Conflict"

]

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 6
# MOMENTUM ENGINE
# =====================================================

class AOMomentumEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.score = 0

        self.reasons = []
    # ------------------------------------------------

    def slope(

        self,

        ao,

    ):

        return (

            ao.iloc[-1]

            -

            ao.iloc[-2]

        )
    # ------------------------------------------------

    def momentum(

        self,

        ao,

    ):

        value = abs(

            ao.iloc[-1]

        )

        if value >= 4:

            self.score += 40

        elif value >= 3:

            self.score += 32

        elif value >= 2:

            self.score += 24

        elif value >= 1:

            self.score += 16

        else:

            self.score += 8
    # ------------------------------------------------

    def acceleration(

        self,

        ao,

    ):

        acc = (

            ao.iloc[-1]

            -

            ao.iloc[-2]

        ) - (

            ao.iloc[-2]

            -

            ao.iloc[-3]

        )

        if abs(acc) >= 1:

            self.score += 20
    # ------------------------------------------------

    def direction_check(

        self,

        ao,

    ):

        if ao.iloc[-1] > ao.iloc[-2]:

            self.direction = "BUY"

        elif ao.iloc[-1] < ao.iloc[-2]:

            self.direction = "SELL"
    # ------------------------------------------------

    def weakening(

        self,

        ao,

    ):

        if (

            abs(ao.iloc[-1])

            <

            abs(ao.iloc[-2])

        ):

            self.score -= 10

            self.reasons.append(

                "Weak Momentum"

            )
    # ------------------------------------------------

    def strengthening(

        self,

        ao,

    ):

        if (

            abs(ao.iloc[-1])

            >

            abs(ao.iloc[-2])

        ):

            self.score += 10

            self.reasons.append(

                "Strong Momentum"

            )
    # ------------------------------------------------

    def normalize(

        self,

    ):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # ------------------------------------------------

    def report(

        self,

    ):

        return {

            "engine":

                "AO Momentum",

            "direction":

                self.direction,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"AO Momentum",

"direction":"BUY",

"score":91,

"reasons":[

"Strong Momentum"

]

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 7
# MOMENTUM PERSISTENCE
# =====================================================

class AOMomentumPersistence:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.direction="NONE"

        self.persistence=0

        self.score=0

        self.reasons=[]
    # --------------------------------------------

    def count(

        self,

        ao,

    ):

        direction=None

        count=1

        if ao.iloc[-1]>ao.iloc[-2]:

            direction="BUY"

        elif ao.iloc[-1]<ao.iloc[-2]:

            direction="SELL"

        for i in range(

            len(ao)-2,

            1,

            -1,

        ):

            if direction=="BUY":

                if ao.iloc[i]>ao.iloc[i-1]:

                    count+=1

                else:

                    break

            else:

                if ao.iloc[i]<ao.iloc[i-1]:

                    count+=1

                else:

                    break

        self.direction=direction

        self.persistence=count
    # --------------------------------------------

    def scoring(

        self,

    ):

        if self.persistence>=12:

            self.score=100

        elif self.persistence>=10:

            self.score=90

        elif self.persistence>=8:

            self.score=80

        elif self.persistence>=6:

            self.score=70

        elif self.persistence>=4:

            self.score=55

        elif self.persistence>=2:

            self.score=35

        else:

            self.score=15
    # --------------------------------------------

    def exhaustion(

        self,

    ):

        if self.persistence>=18:

            self.score-=15

            self.reasons.append(

                "Momentum Exhaustion"

            )
    # --------------------------------------------

    def weak(

        self,

    ):

        if self.persistence<=2:

            self.score-=10

            self.reasons.append(

                "Weak Persistence"

            )
    # --------------------------------------------

    def normalize(

        self,

    ):

        self.score=max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # --------------------------------------------

    def report(

        self,

    ):

        return{

            "engine":

                "AO Momentum Persistence",

            "direction":

                self.direction,

            "bars":

                self.persistence,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"AO Momentum Persistence",

"direction":"BUY",

"bars":9,

"score":83,

"reasons":[]

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 8
# VELOCITY ENGINE
# =====================================================

class AOVelocityEngine:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.direction="NONE"

        self.velocity=0

        self.score=0

        self.reasons=[]
    # --------------------------------------------

    def calculate(

        self,

        ao,

    ):

        self.velocity=(

            ao.iloc[-1]

            -

            ao.iloc[-2]

        )
    # --------------------------------------------

    def direction_check(

        self,

    ):

        if self.velocity>0:

            self.direction="BUY"

        elif self.velocity<0:

            self.direction="SELL"

        else:

            self.direction="NONE"
    # --------------------------------------------

    def scoring(

        self,

    ):

        value=abs(

            self.velocity

        )

        if value>=3:

            self.score=100

        elif value>=2:

            self.score=85

        elif value>=1:

            self.score=70

        elif value>=0.50:

            self.score=55

        elif value>=0.20:

            self.score=35

        else:

            self.score=15
    # --------------------------------------------

    def explosion(

        self,

    ):

        if abs(

            self.velocity

        )>=3:

            self.score+=5

            self.reasons.append(

                "Velocity Explosion"

            )
    # --------------------------------------------

    def slowdown(

        self,

        prev_velocity,

    ):

        if abs(

            self.velocity

        )<abs(

            prev_velocity

        ):

            self.score-=5

            self.reasons.append(

                "Velocity Slowdown"

            )
    # --------------------------------------------

    def reversal(

        self,

        prev_velocity,

    ):

        if (

            self.velocity

            *

            prev_velocity

        )<0:

            self.score-=10

            self.reasons.append(

                "Velocity Reversal"

            )
    # --------------------------------------------

    def normalize(

        self,

    ):

        self.score=max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # --------------------------------------------

    def report(

        self,

    ):

        return{

            "engine":

                "AO Velocity",

            "direction":

                self.direction,

            "velocity":

                round(

                    self.velocity,

                    4,

                ),

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"AO Velocity",

"direction":"BUY",

"velocity":2.41,

"score":90,

"reasons":[

"Velocity Explosion"

]

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 9
# VELOCITY PERSISTENCE ENGINE
# =====================================================

class AOVelocityPersistenceEngine:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.persistence = 0

        self.score = 0

        self.reasons = []
    # --------------------------------------------

    def count(

        self,

        velocity_series,

    ):

        if len(velocity_series) < 2:

            return

        direction = None

        if velocity_series.iloc[-1] > 0:

            direction = "BUY"

        elif velocity_series.iloc[-1] < 0:

            direction = "SELL"

        count = 1

        for i in range(

            len(velocity_series)-2,

            -1,

            -1,

        ):

            if direction == "BUY":

                if velocity_series.iloc[i] > 0:

                    count += 1

                else:

                    break

            elif direction == "SELL":

                if velocity_series.iloc[i] < 0:

                    count += 1

                else:

                    break

        self.direction = direction

        self.persistence = count
    # --------------------------------------------

    def scoring(

        self,

    ):

        if self.persistence >= 10:

            self.score = 100

        elif self.persistence >= 8:

            self.score = 90

        elif self.persistence >= 6:

            self.score = 80

        elif self.persistence >= 4:

            self.score = 65

        elif self.persistence >= 2:

            self.score = 45

        else:

            self.score = 20
    # --------------------------------------------

    def exhaustion(

        self,

    ):

        if self.persistence >= 15:

            self.score -= 10

            self.reasons.append(

                "Velocity Exhaustion"

            )
    # --------------------------------------------

    def unstable(

        self,

        velocity_series,

    ):

        if len(velocity_series) < 5:

            return

        flips = 0

        for i in range(

            len(velocity_series)-4,

            len(velocity_series),

        ):

            if (

                velocity_series.iloc[i]

                *

                velocity_series.iloc[i-1]

            ) < 0:

                flips += 1

        if flips >= 2:

            self.score -= 15

            self.reasons.append(

                "Unstable Velocity"

            )
    # --------------------------------------------

    def normalize(

        self,

    ):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # --------------------------------------------

    def report(

        self,

    ):

        return {

            "engine":

                "AO Velocity Persistence",

            "direction":

                self.direction,

            "bars":

                self.persistence,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"AO Velocity Persistence",

"direction":"BUY",

"bars":7,

"score":82,

"reasons":[]

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 10
# ZERO LINE CONTEXT ENGINE
# =====================================================

class AOZeroContextEngine:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.score = 0

        self.zone = "NONE"

        self.reasons = []
    # --------------------------------------------

    def zone_check(

        self,

        ao,

    ):

        if ao.iloc[-1] > 0:

            self.zone = "ABOVE"

            self.direction = "BUY"

        elif ao.iloc[-1] < 0:

            self.zone = "BELOW"

            self.direction = "SELL"

        else:

            self.zone = "ZERO"
    # --------------------------------------------

    def distance(

        self,

        ao,

    ):

        value = abs(

            ao.iloc[-1]

        )

        if value >= 5:

            self.score += 40

        elif value >= 3:

            self.score += 30

        elif value >= 2:

            self.score += 20

        elif value >= 1:

            self.score += 10

        else:

            self.score += 3
    # --------------------------------------------

    def persistence(

        self,

        ao,

    ):

        bars = 0

        current = ao.iloc[-1] > 0

        for i in range(

            len(ao)-1,

            -1,

            -1,

        ):

            if (ao.iloc[i] > 0) == current:

                bars += 1

            else:

                break

        if bars >= 10:

            self.score += 30

        elif bars >= 6:

            self.score += 20

        elif bars >= 3:

            self.score += 10
    # --------------------------------------------

    def near_zero(

        self,

        ao,

    ):

        if abs(

            ao.iloc[-1]

        ) < 0.50:

            self.score -= 15

            self.reasons.append(

                "Near Zero"

            )
    # --------------------------------------------

    def zero_noise(

        self,

        ao,

    ):

        flips = 0

        for i in range(

            len(ao)-5,

            len(ao),

        ):

            if (

                ao.iloc[i]

                *

                ao.iloc[i-1]

            ) < 0:

                flips += 1

        if flips >= 2:

            self.score -= 20

            self.reasons.append(

                "Zero Noise"

            )
    # --------------------------------------------

    def normalize(

        self,

    ):

        self.score = max(

            0,

            min(

                100,

                self.score,

            ),

        )
    # --------------------------------------------

    def report(

        self,

    ):

        return {

            "engine":

                "AO Zero Context",

            "direction":

                self.direction,

            "zone":

                self.zone,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
{

"engine":"AO Zero Context",

"direction":"BUY",

"zone":"ABOVE",

"score":86,

"reasons":[]

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 11
# RELIABILITY ENGINE
# =====================================================

class AOReliabilityEngine:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.score = 0

        self.level = "NONE"

        self.reasons = []
    # --------------------------------------------

    def base_score(

        self,

        engines,

    ):

        values = [

            e["score"]

            for e in engines

        ]

        self.score = sum(

            values

        ) / len(values)
    # --------------------------------------------

    def conflict(

        self,

        conflict,

    ):

        if conflict:

            self.score -= 20

            self.reasons.append(

                "Conflict"

            )
    # --------------------------------------------

    def quality(

        self,

        quality,

    ):

        self.score *= (

            quality

            /

            100

        )
    # --------------------------------------------

    def noise(

        self,

        noise,

    ):

        self.score -= (

            noise

            * 0.20

        )
    # --------------------------------------------

    def classify(

        self,

    ):

        if self.score >= 90:

            self.level = "VERY HIGH"

        elif self.score >= 80:

            self.level = "HIGH"

        elif self.score >= 65:

            self.level = "MEDIUM"

        elif self.score >= 50:

            self.level = "LOW"

        else:

            self.level = "VERY LOW"
    # --------------------------------------------

    def normalize(

        self,

    ):

        self.score = max(

            0,

            min(

                100,

                round(

                    self.score,

                    2,

                ),

            ),

        )
    # --------------------------------------------

    def report(

        self,

    ):

        return {

            "engine":

                "AO Reliability",

            "score":

                self.score,

            "level":

                self.level,

            "reasons":

                self.reasons,

        }
{

"engine":"AO Reliability",

"score":91.7,

"level":"VERY HIGH",

"reasons":[]

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 12-1
# DYNAMIC THRESHOLD ENGINE
# =====================================================

class AODynamicThresholdEngine:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.threshold = {}

        self.reasons = []
    # --------------------------------------------

    def average_ao(

        self,

        ao,

        period=100,

    ):

        return (

            ao.tail(period)

            .abs()

            .mean()

        )
    # --------------------------------------------

    def std_ao(

        self,

        ao,

        period=100,

    ):

        return (

            ao.tail(period)

            .std()

        )
    # --------------------------------------------

    def base_threshold(

        self,

        avg,

        std,

    ):

        return (

            avg

            +

            0.50 *

            std

        )
    # --------------------------------------------

    def strong_threshold(

        self,

        avg,

        std,

    ):

        return (

            avg

            +

            1.20 *

            std

        )
    # --------------------------------------------

    def explosion_threshold(

        self,

        avg,

        std,

    ):

        return (

            avg

            +

            2 *

            std

        )
    # --------------------------------------------

    def build(

        self,

        ao,

    ):

        avg = self.average_ao(ao)

        std = self.std_ao(ao)

        self.threshold = {

            "base":

                self.base_threshold(

                    avg,

                    std,

                ),

            "strong":

                self.strong_threshold(

                    avg,

                    std,

                ),

            "explosion":

                self.explosion_threshold(

                    avg,

                    std,

                ),

        }

        return self.threshold
{

"base":1.25,

"strong":2.10,

"explosion":3.95

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 12-2
# DYNAMIC EXHAUSTION ENGINE
# =====================================================

class AODynamicExhaustion:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.limit = 0

        self.reasons = []
Persistence

Timeframe

Market Type
    # --------------------------------------------

    def base_limit(

        self,

        market,

    ):

        table = {

            "crypto":20,

            "forex":15,

            "stock":18

        }

        self.limit = table.get(

            market,

            18,

        )
    # --------------------------------------------

    def timeframe_adjust(

        self,

        timeframe,

    ):

        if timeframe in [

            "M1",

            "M5",

            "M15"

        ]:

            self.limit -= 3

        elif timeframe in [

            "H4",

            "H8",

            "D1"

        ]:

            self.limit += 3
    # --------------------------------------------

    def report(

        self,

    ):

        return {

            "engine":

                "AO Dynamic Exhaustion",

            "limit":

                self.limit

        }
{

"engine":"AO Dynamic Exhaustion",

"limit":21

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 12-3
# DYNAMIC VELOCITY ENGINE
# =====================================================

class AODynamicVelocity:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.threshold={}
    # --------------------------------------------

    def average_velocity(

        self,

        velocity,

        period=100,

    ):

        return (

            velocity

            .tail(period)

            .abs()

            .mean()

        )
    # --------------------------------------------

    def std_velocity(

        self,

        velocity,

        period=100,

    ):

        return (

            velocity

            .tail(period)

            .std()

        )
    # --------------------------------------------

    def base(

        self,

        avg,

        std,

    ):

        return (

            avg

            +

            0.50 *

            std

        )
    # --------------------------------------------

    def strong(

        self,

        avg,

        std,

    ):

        return (

            avg

            +

            1.20 *

            std

        )
    # --------------------------------------------

    def explosion(

        self,

        avg,

        std,

    ):

        return (

            avg

            +

            2 *

            std

        )
    # --------------------------------------------

    def build(

        self,

        velocity,

    ):

        avg=self.average_velocity(

            velocity

        )

        std=self.std_velocity(

            velocity

        )

        self.threshold={

            "base":

                self.base(

                    avg,

                    std,

                ),

            "strong":

                self.strong(

                    avg,

                    std,

                ),

            "explosion":

                self.explosion(

                    avg,

                    std,

                ),

        }

        return self.threshold
{

"base":0.82,

"strong":1.46,

"explosion":2.31

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 12-4
# DYNAMIC MOMENTUM ENGINE
# =====================================================

class AODynamicMomentum:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.threshold = {}
    # --------------------------------------------

    def average(

        self,

        momentum,

        period=100,

    ):

        return (

            momentum

            .tail(period)

            .abs()

            .mean()

        )
    # --------------------------------------------

    def deviation(

        self,

        momentum,

        period=100,

    ):

        return (

            momentum

            .tail(period)

            .std()

        )
    # --------------------------------------------

    def base(

        self,

        avg,

        std,

    ):

        return (

            avg

            +

            0.50 *

            std

        )
    # --------------------------------------------

    def strong(

        self,

        avg,

        std,

    ):

        return (

            avg

            +

            1.20 *

            std

        )
    # --------------------------------------------

    def explosion(

        self,

        avg,

        std,

    ):

        return (

            avg

            +

            2.00 *

            std

        )
    # --------------------------------------------

    def build(

        self,

        momentum,

    ):

        avg = self.average(

            momentum

        )

        std = self.deviation(

            momentum

        )

        self.threshold = {

            "base":

                self.base(

                    avg,

                    std,

                ),

            "strong":

                self.strong(

                    avg,

                    std,

                ),

            "explosion":

                self.explosion(

                    avg,

                    std,

                ),

        }

        return self.threshold
{

"base":1.18,

"strong":2.07,

"explosion":3.81

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 12-5
# DYNAMIC ZERO DISTANCE ENGINE
# =====================================================

class AOZeroDistanceEngine:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.threshold = {}
    # --------------------------------------------

    def distance_series(

        self,

        ao,

    ):

        return ao.abs()
    # --------------------------------------------

    def average(

        self,

        distance,

        period=100,

    ):

        return (

            distance

            .tail(period)

            .mean()

        )
    # --------------------------------------------

    def deviation(

        self,

        distance,

        period=100,

    ):

        return (

            distance

            .tail(period)

            .std()

        )
    # --------------------------------------------

    def base(

        self,

        avg,

        std,

    ):

        return (

            avg

            +

            0.50 *

            std

        )
    # --------------------------------------------

    def strong(

        self,

        avg,

        std,

    ):

        return (

            avg

            +

            1.20 *

            std

        )
    # --------------------------------------------

    def extreme(

        self,

        avg,

        std,

    ):

        return (

            avg

            +

            2.00 *

            std

        )
    # --------------------------------------------

    def build(

        self,

        ao,

    ):

        dist = self.distance_series(

            ao

        )

        avg = self.average(

            dist

        )

        std = self.deviation(

            dist

        )

        self.threshold = {

            "base":

                self.base(

                    avg,

                    std,

                ),

            "strong":

                self.strong(

                    avg,

                    std,

                ),

            "extreme":

                self.extreme(

                    avg,

                    std,

                ),

        }

        return self.threshold
{

"base":1.34,

"strong":2.21,

"extreme":4.02

}
# --------------------------------------------

def distance_velocity(

    self,

    ao,

):

    current = abs(ao.iloc[-1])

    previous = abs(ao.iloc[-2])

    return current - previous
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 12-6
# DYNAMIC DIVERGENCE THRESHOLD
# =====================================================

class AODynamicDivergenceThreshold:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.threshold = 0
    # --------------------------------------------

    def atr_based(

        self,

        atr,

        multiplier=0.25,

    ):

        self.threshold = atr * multiplier
    # --------------------------------------------

    def tick_based(

        self,

        tick,

        multiplier=10,

    ):

        return tick * multiplier
    # --------------------------------------------

    def build(

        self,

        atr,

        tick,

    ):

        atr_value = atr * 0.25

        tick_value = tick * 10

        self.threshold = max(

            atr_value,

            tick_value,

        )

        return self.threshold
{

"divergence_threshold":48.25

}
# ============================================================
# AO ENTERPRISE ENGINE
# SECTION 12-7
# SMART DIVERGENCE / CONVERGENCE CONFLICT ENGINE
# ============================================================

class AOSmartConflictEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.score = 0

        self.conflict = False

        self.reasons = []

    # ------------------------------------------------
    # ضرایب اهمیت
    # ------------------------------------------------

    WEIGHTS = {

        "regular_divergence": 1.00,

        "regular_convergence": 1.00,

        "hidden_divergence": 0.85,

        "hidden_convergence": 0.85,

    }

    # ------------------------------------------------

    def effective_score(

        self,

        raw_score,

        signal_type,

    ):

        weight = self.WEIGHTS.get(

            signal_type,

            1.0,

        )

        return raw_score * weight

    # ------------------------------------------------

    def compare(

        self,

        bullish_signals,

        bearish_signals,

    ):

        bull = 0

        bear = 0

        bull_reason = None

        bear_reason = None

        # --------------------

        for signal in bullish_signals:

            score = self.effective_score(

                signal["score"],

                signal["type"],

            )

            if score > bull:

                bull = score

                bull_reason = signal["type"]

        # --------------------

        for signal in bearish_signals:

            score = self.effective_score(

                signal["score"],

                signal["type"],

            )

            if score > bear:

                bear = score

                bear_reason = signal["type"]

        # --------------------

        diff = abs(

            bull - bear

        )

        # --------------------

        if diff <= 10:

            self.conflict = True

            self.score = 40

            self.direction = "NONE"

            self.reasons.append(

                "Strong Conflict"

            )

        elif diff <= 25:

            self.conflict = True

            self.score = 60

            self.direction = (

                "BUY"

                if bull > bear

                else "SELL"

            )

            self.reasons.append(

                "Medium Conflict"

            )

        else:

            self.conflict = False

            self.score = max(

                bull,

                bear,

            )

            self.direction = (

                "BUY"

                if bull > bear

                else "SELL"

            )

        # --------------------

        self.reasons.append(

            f"Bull={bull_reason}"

        )

        self.reasons.append(

            f"Bear={bear_reason}"

        )

    # ------------------------------------------------

    def normalize(self):

        self.score = max(

            0,

            min(

                100,

                round(

                    self.score,

                    2,

                ),

            ),

        )

    # ------------------------------------------------

    def report(self):

        return {

            "engine":

                "AO Smart Conflict",

            "direction":

                self.direction,

            "conflict":

                self.conflict,

            "score":

                self.score,

            "reasons":

                self.reasons,

        }
bullish_signals = [

    {

        "type":"regular_divergence",

        "score":92

    },

    {

        "type":"hidden_convergence",

        "score":81

    }

]

bearish_signals = [

    {

        "type":"hidden_divergence",

        "score":90

    }

]
{

"engine":"AO Smart Conflict",

"direction":"BUY",

"conflict":False,

"score":92,

"reasons":[

"Bull=regular_divergence",

"Bear=hidden_divergence"

]

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 12-8
# WEIGHTED RELIABILITY ENGINE
# =====================================================

class AOWeightedReliabilityEngine:

    def __init__(self):

        self.reset()
    # --------------------------------------------

    def reset(self):

        self.score = 0

        self.level = "NONE"

        self.active = 0

        self.total = 0

        self.reasons = []
    # --------------------------------------------

    ENGINE_WEIGHTS = {

        "regular_divergence":1.20,

        "regular_convergence":1.20,

        "hidden_divergence":1.10,

        "hidden_convergence":1.10,

        "momentum":1.10,

        "momentum_persistence":1.10,

        "velocity":1.00,

        "velocity_persistence":1.00,

        "zero_context":0.90,

        "zero_cross":0.90,

        "twin_peaks":0.90,

        "saucer":0.90

    }
    # --------------------------------------------

    def calculate(

        self,

        engines,

    ):

        self.total = len(

            engines

        )

        weighted_sum = 0

        weight_total = 0

        active = 0

        for engine in engines:

            if not engine.get(

                "active",

                True,

            ):

                continue

            active += 1

            weight = self.ENGINE_WEIGHTS.get(

                engine["engine"],

                1.0,

            )

            weighted_sum += (

                engine["score"]

                *

                weight

            )

            weight_total += weight

        self.active = active

        if weight_total == 0:

            self.score = 0

        else:

            self.score = (

                weighted_sum

                /

                weight_total

            )
    # --------------------------------------------

    def normalize(

        self,

    ):

        self.score = max(

            0,

            min(

                100,

                round(

                    self.score,

                    2,

                )

            )

        )
    # --------------------------------------------

    def classify(

        self,

    ):

        if self.score >= 90:

            self.level = "VERY HIGH"

        elif self.score >= 80:

            self.level = "HIGH"

        elif self.score >= 65:

            self.level = "MEDIUM"

        elif self.score >= 50:

            self.level = "LOW"

        else:

            self.level = "VERY LOW"
    # --------------------------------------------

    def report(

        self,

    ):

        return {

            "engine":

                "AO Reliability",

            "score":

                self.score,

            "level":

                self.level,

            "active_engines":

                self.active,

            "total_engines":

                self.total,

            "reasons":

                self.reasons,

        }
{

"engine":"AO Reliability",

"score":92.31,

"level":"VERY HIGH",

"active_engines":9,

"total_engines":12,

"reasons":[]

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 12-9
# AO CONFIDENCE REPORT ENGINE
# =====================================================

class AOConfidenceReport:

    def __init__(self):

        self.report_data = {}
    # --------------------------------------------

    def build(

        self,

        direction,

        raw_score,

        reliability,

        quality,

        conflict,

        noise,

        active,

        total,

        momentum,

        velocity,

        zone,

    ):

        self.report_data = {

            "direction": direction,

            "raw_score": raw_score,

            "reliability": reliability,

            "quality": quality,

            "conflict": conflict,

            "noise": noise,

            "active_engines": active,

            "total_engines": total,

            "momentum": momentum,

            "velocity": velocity,

            "zone": zone,

        }

        return self.report_data
    # --------------------------------------------

    def confidence_level(

        self,

        score,

    ):

        if score >= 90:

            return "VERY HIGH"

        elif score >= 80:

            return "HIGH"

        elif score >= 65:

            return "MEDIUM"

        elif score >= 50:

            return "LOW"

        else:

            return "VERY LOW"
    # --------------------------------------------

    def summary(

        self,

    ):

        return {

            "AO REPORT":{

                "Direction":

                    self.report_data["direction"],

                "Raw Score":

                    self.report_data["raw_score"],

                "Reliability":

                    self.report_data["reliability"],

                "Confidence":

                    self.confidence_level(

                        self.report_data["reliability"]

                    ),

                "Quality":

                    self.report_data["quality"],

                "Conflict":

                    self.report_data["conflict"],

                "Noise":

                    self.report_data["noise"],

                "Active Engines":

                    f'{self.report_data["active_engines"]}/{self.report_data["total_engines"]}',

                "Momentum":

                    self.report_data["momentum"],

                "Velocity":

                    self.report_data["velocity"],

                "Zone":

                    self.report_data["zone"],

            }

        }
{

"AO REPORT":{

"Direction":"BUY",

"Raw Score":86,

"Reliability":93,

"Confidence":"VERY HIGH",

"Quality":94,

"Conflict":False,

"Noise":"LOW",

"Active Engines":"10/12",

"Momentum":"STRONG",

"Velocity":"STRONG",

"Zone":"ABOVE"

}

}
AO REPORT

Direction : BUY

Raw Score : 86

Reliability : 93

Confidence : VERY HIGH

Quality : 94

Conflict : NO

Noise : LOW

Momentum : STRONG

Velocity : STRONG

Zone : ABOVE ZERO

Active Engines : 10 / 12
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 12-10
# AO FINAL OUTPUT ENGINE
# =====================================================

class AOFinalOutputEngine:

    SYSTEM_NAME = "AO Enterprise"

    SYSTEM_VERSION = "1.0.0"

    BUILD = "2026.07.30.001"

    def __init__(self):

        self.output = {}
    # ------------------------------------------------

    def build(

        self,

        direction,

        raw_score,

        reliability,

        confidence,

        quality,

        conflict,

        noise,

        momentum,

        velocity,

        zone,

        contributors,

        reasons,

    ):

        self.output = {

            "engine":

                "AO",

            "system":

                self.SYSTEM_NAME,

            "version":

                self.SYSTEM_VERSION,

            "build":

                self.BUILD,

            "direction":

                direction,

            "raw_score":

                raw_score,

            "reliability":

                reliability,

            "confidence":

                confidence,

            "quality":

                quality,

            "conflict":

                conflict,

            "noise":

                noise,

            "momentum":

                momentum,

            "velocity":

                velocity,

            "zone":

                zone,

            "contributors":

                contributors,

            "reasons":

                reasons,

        }

        return self.output
{

"engine":"AO",

"system":"AO Enterprise",

"version":"1.0.0",

"build":"2026.07.30.001",

"direction":"BUY",

"raw_score":86,

"reliability":93,

"confidence":"VERY HIGH",

"quality":94,

"conflict":False,

"noise":"LOW",

"momentum":"STRONG",

"velocity":"STRONG",

"zone":"ABOVE",

"contributors":[

"Regular Bullish Divergence",

"Momentum",

"Velocity"

],

"reasons":[

"Strong Bullish Divergence",

"Momentum Rising",

"Velocity Increasing"

]

}
{

"time":"...",

"symbol":"BTCUSDT",

"engine":"AO",

"system":"AO Enterprise",

"version":"1.0.0",

"build":"2026.07.30.001",

"direction":"BUY",

"raw_score":86,

"reliability":93,

"confidence":"VERY HIGH",

"quality":94,

"conflict":False,

"noise":"LOW",

"momentum":"STRONG",

"velocity":"STRONG",

"zone":"ABOVE"

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 13-1
# TIMEFRAME SYNCHRONIZATION ENGINE
# =====================================================

class AOTimeframeSynchronization:

    def __init__(self):

        self.reset()
    # --------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.score = 0

        self.alignment = False

        self.reasons = []
{

"M15":"BUY",

"M30":"BUY",

"H1":"BUY",

"H4":"BUY",

"D1":"BUY"

}
    # --------------------------------------------

    def calculate(

        self,

        directions,

    ):

        buy = list(

            directions.values()

        ).count(

            "BUY"

        )

        sell = list(

            directions.values()

        ).count(

            "SELL"

        )

        if buy > sell:

            self.direction = "BUY"

            self.score = (

                buy

                /

                len(directions)

            ) * 100

        elif sell > buy:

            self.direction = "SELL"

            self.score = (

                sell

                /

                len(directions)

            ) * 100

        else:

            self.direction = "NONE"

            self.score = 0
    # --------------------------------------------

    def alignment_check(

        self,

    ):

        self.alignment = (

            self.score >= 80

        )
    # --------------------------------------------

    def report(

        self,

    ):

        return {

            "engine":

                "AO Timeframe Sync",

            "direction":

                self.direction,

            "alignment":

                self.alignment,

            "score":

                round(

                    self.score,

                    2,

                )

        }
{

"engine":"AO Timeframe Sync",

"direction":"BUY",

"alignment":True,

"score":100

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 13-2
# HIGHER TIMEFRAME CONFIRMATION ENGINE
# =====================================================

class AOHigherTimeframeConfirmation:

    def __init__(self):

        self.reset()
    # --------------------------------------------

    def reset(self):

        self.confirmed = False

        self.status = "NONE"

        self.current_direction = "NONE"

        self.aligned = []

        self.rejected = []

        self.reasons = []
    # --------------------------------------------

    def check(

        self,

        current_direction,

        higher_timeframes,

    ):

        self.reset()

        self.current_direction = current_direction

        for tf, direction in higher_timeframes.items():

            if direction == current_direction:

                self.aligned.append(tf)

            else:

                self.rejected.append(tf)
    # --------------------------------------------

        aligned_count = len(

            self.aligned

        )

        if aligned_count == len(

            higher_timeframes

        ):

            self.confirmed = True

            self.status = "STRONG"

        elif aligned_count >= 2:

            self.confirmed = True

            self.status = "PARTIAL"

        elif aligned_count >= 1:

            self.confirmed = True

            self.status = "WEAK"

        else:

            self.confirmed = False

            self.status = "REJECTED"
    # --------------------------------------------

        self.reasons.append(

            f"Aligned : {self.aligned}"

        )

        self.reasons.append(

            f"Rejected : {self.rejected}"

        )
    # --------------------------------------------

    def report(

        self,

    ):

        return {

            "engine":

                "Higher TF Confirmation",

            "direction":

                self.current_direction,

            "confirmed":

                self.confirmed,

            "status":

                self.status,

            "aligned_timeframes":

                self.aligned,

            "rejected_timeframes":

                self.rejected,

            "reasons":

                self.reasons,

        }
{

"confirmed":True,

"status":"STRONG",

"aligned_timeframes":[

"M30",

"H1",

"H4"

],

"rejected_timeframes":[]

}
{

"confirmed":True,

"status":"PARTIAL",

"aligned_timeframes":[

"M30",

"H1"

],

"rejected_timeframes":[

"H4"

]

}
{

"confirmed":False,

"status":"REJECTED",

"aligned_timeframes":[],

"rejected_timeframes":[

"M30",

"H1",

"H4"

]

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 13-3
# HIGHER TIMEFRAME TREND REPORT
# =====================================================

class AOHigherTimeframeTrendReport:

    def __init__(self):

        self.reset()
    # --------------------------------------------

    def reset(self):

        self.status = "UNKNOWN"

        self.h1 = "NONE"

        self.h4 = "NONE"

        self.reasons = []
    # --------------------------------------------

    def evaluate(

        self,

        h1_trend,

        h4_trend,

    ):

        self.reset()

        self.h1 = h1_trend

        self.h4 = h4_trend

        if h1_trend == h4_trend:

            self.status = "CONFIRMED"

        else:

            self.status = "MIXED"
    # --------------------------------------------

        self.reasons.append(

            f"H1 = {h1_trend}"

        )

        self.reasons.append(

            f"H4 = {h4_trend}"

        )
    # --------------------------------------------

    def report(

        self,

    ):

        return {

            "engine":

                "Higher TF Trend",

            "status":

                self.status,

            "H1":

                self.h1,

            "H4":

                self.h4,

            "reasons":

                self.reasons,

        }
{

"status":"CONFIRMED",

"H1":"STRONG BULLISH",

"H4":"STRONG BULLISH"

}
{

"status":"MIXED",

"H1":"WEAK BULLISH",

"H4":"STRONG BEARISH"

}
{

"H1":"STRONG BULLISH",

"H4":"WEAK BULLISH",

"status":"CONFIRMED"

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 13-4
# MULTI TIMEFRAME AGREEMENT REPORT
# =====================================================

class AOMultiTimeframeAgreement:

    def __init__(self):

        self.reset()
    # --------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.percent = 0

        self.total = 0

        self.aligned = 0

        self.timeframes = {}
    # --------------------------------------------

    def evaluate(

        self,

        timeframe_signals,

    ):

        self.reset()

        self.timeframes = timeframe_signals

        self.total = len(

            timeframe_signals

        )

        buy = list(

            timeframe_signals.values()

        ).count(

            "BUY"

        )

        sell = list(

            timeframe_signals.values()

        ).count(

            "SELL"

        )

        if buy >= sell:

            self.direction = "BUY"

            self.aligned = buy

        else:

            self.direction = "SELL"

            self.aligned = sell

        self.percent = round(

            (

                self.aligned

                /

                self.total

            ) * 100,

            2,

        )
    # --------------------------------------------

    def report(

        self,

    ):

        return {

            "engine":

                "Multi TF Agreement",

            "direction":

                self.direction,

            "agreement_percent":

                self.percent,

            "aligned":

                self.aligned,

            "total":

                self.total,

            "timeframes":

                self.timeframes,

        }
{

"M15":"BUY",

"M30":"BUY",

"H1":"BUY",

"H4":"SELL",

"D1":"BUY"

}
{

"direction":"BUY",

"agreement_percent":80,

"aligned":4,

"total":5

}
{

"agreement":80,

"direction":"BUY",

"aligned":4,

"total":5

}
multi_timeframe_snapshot = {

    "M15":"BUY",

    "M30":"BUY",

    "H1":"BUY",

    "H4":"SELL",

    "D1":"BUY"

}
"timeframe_snapshot":{

"M15":"BUY",

"M30":"BUY",

"H1":"BUY",

"H4":"SELL",

"D1":"BUY"

}
timeframe_snapshot = {

    "M15":"BUY",

    "M30":"BUY",

    "H1":"BUY",

    "H4":"SELL",

    "D1":"BUY"

}
{

"time":"...",

"symbol":"BTCUSDT",

"timeframe_snapshot":{

"M15":"BUY",

"M30":"BUY",

"H1":"BUY",

"H4":"SELL",

"D1":"BUY"

}

}
{

"id":...,

"symbol":"BTCUSDT",

"entry_time":"...",

"timeframe_snapshot":{

"M15":"BUY",

"M30":"BUY",

"H1":"BUY",

"H4":"SELL",

"D1":"BUY"

}

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 13-5
# MULTI TIMEFRAME CONFLICT REPORT
# =====================================================

class AOMultiTimeframeConflictReport:

    def __init__(self):

        self.reset()
    # --------------------------------------------

    def reset(self):

        self.status = "NONE"

        self.buy_timeframes = []

        self.sell_timeframes = []

        self.reasons = []
    # --------------------------------------------

    def evaluate(

        self,

        timeframe_snapshot,

    ):

        self.reset()

        for tf, direction in timeframe_snapshot.items():

            if direction == "BUY":

                self.buy_timeframes.append(tf)

            elif direction == "SELL":

                self.sell_timeframes.append(tf)

        if len(self.buy_timeframes) > 0 and len(self.sell_timeframes) > 0:

            self.status = "CONFLICT"

        elif len(self.buy_timeframes) > 0:

            self.status = "BUY"

        elif len(self.sell_timeframes) > 0:

            self.status = "SELL"
    # --------------------------------------------

        self.reasons.append(

            f"BUY TF = {self.buy_timeframes}"

        )

        self.reasons.append(

            f"SELL TF = {self.sell_timeframes}"

        )
    # --------------------------------------------

    def report(self):

        return {

            "engine":

                "Multi TF Conflict",

            "status":

                self.status,

            "buy_timeframes":

                self.buy_timeframes,

            "sell_timeframes":

                self.sell_timeframes,

            "reasons":

                self.reasons,

        }
{

"engine":"Multi TF Conflict",

"status":"CONFLICT",

"buy_timeframes":[

"M15",

"M30"

],

"sell_timeframes":[

"H1",

"H4",

"D1"

]

}
{

"tf_conflict":{

"buy":[

"M15",

"M30"

],

"sell":[

"H1",

"H4",

"D1"

]

}

}
{

"M15":{

"direction":"BUY",

"score":84,

"reliability":91,

"confidence":"HIGH"

},

"M30":{

"direction":"BUY",

"score":87,

"reliability":93,

"confidence":"VERY HIGH"

},

"H1":{

"direction":"BUY",

"score":90,

"reliability":95,

"confidence":"VERY HIGH"

},

"H4":{

"direction":"SELL",

"score":78,

"reliability":88,

"confidence":"HIGH"

}

}
{

"time":"...",

"symbol":"BTCUSDT",

"ao_strength":{

"M15":{

"direction":"BUY",

"score":84,

"reliability":91,

"confidence":"HIGH"

},

"M30":{

"direction":"BUY",

"score":87,

"reliability":93,

"confidence":"VERY HIGH"

},

"H1":{

"direction":"BUY",

"score":90,

"reliability":95,

"confidence":"VERY HIGH"

},

"H4":{

"direction":"SELL",

"score":78,

"reliability":88,

"confidence":"HIGH"

},

"D1":{

"direction":"BUY",

"score":81,

"reliability":90,

"confidence":"HIGH"

}

}

}
{

"consensus":{

"BUY":4,

"SELL":1,

"NONE":0

}

}
{

"last_buy":

"2026-07-31 10:15",

"last_sell":

"2026-07-30 18:40",

"last_regular_divergence":

"2026-07-29",

"last_hidden_divergence":

"2026-07-28",

"last_zero_cross":

"2026-07-31"

}
{

"symbol":"BTCUSDT",

"history":{

"last_buy":"2026-07-31 10:15",

"last_sell":"2026-07-30 18:40",

"last_regular_divergence":"2026-07-29",

"last_hidden_divergence":"2026-07-28",

"last_zero_cross":"2026-07-31",

"last_twin_peaks":"2026-07-27",

"last_saucer":"2026-07-26"

}

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 13-10
# AO MARKET STATE REPORT
# =====================================================

class AOMarketStateReport:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.market_state = "UNKNOWN"

        self.strength = "UNKNOWN"

        self.timestamp = None

    # --------------------------------------------

    def evaluate(

        self,

        ao_trend,

        ao_slope,

        ao_histogram,

        timestamp,

    ):

        self.timestamp = timestamp

        # ===== Trending Bull =====

        if (

            ao_trend == "BULL"

            and ao_slope == "UP"

            and ao_histogram > 0

        ):

            self.market_state = "TRENDING_BULL"

            self.strength = "STRONG"

        # ===== Trending Bear =====

        elif (

            ao_trend == "BEAR"

            and ao_slope == "DOWN"

            and ao_histogram < 0

        ):

            self.market_state = "TRENDING_BEAR"

            self.strength = "STRONG"

        # ===== Pullback =====

        elif (

            ao_trend == "BULL"

            and ao_histogram < 0

        ):

            self.market_state = "PULLBACK"

            self.strength = "MEDIUM"

        elif (

            ao_trend == "BEAR"

            and ao_histogram > 0

        ):

            self.market_state = "PULLBACK"

            self.strength = "MEDIUM"

        # ===== Range =====

        elif abs(ao_histogram) < 0.05:

            self.market_state = "RANGING"

            self.strength = "WEAK"

        # ===== Reversal =====

        elif ao_slope == "REVERSING":

            self.market_state = "REVERSAL"

            self.strength = "MEDIUM"

        else:

            self.market_state = "UNKNOWN"

            self.strength = "UNKNOWN"

    # --------------------------------------------

    def report(self):

        return {

            "engine":

                "AO Market State",

            "market_state":

                self.market_state,

            "strength":

                self.strength,

            "timestamp":

                self.timestamp,

        }
{

"time":"...",

"symbol":"BTCUSDT",

"market_state":{

"state":"TRENDING_BULL",

"strength":"STRONG"

}

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 13-11
# AO SIGNAL QUALITY REPORT
# =====================================================

class AOSignalQualityReport:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.quality = "UNKNOWN"

        self.score = 0

        self.timestamp = None

    # --------------------------------------------

    def evaluate(

        self,

        final_score,

        timestamp,

    ):

        self.timestamp = timestamp

        self.score = final_score

        if final_score >= 90:

            self.quality = "EXCELLENT"

        elif final_score >= 80:

            self.quality = "VERY_GOOD"

        elif final_score >= 70:

            self.quality = "GOOD"

        elif final_score >= 60:

            self.quality = "AVERAGE"

        else:

            self.quality = "WEAK"

    # --------------------------------------------

    def report(self):

        return {

            "engine":

                "AO Signal Quality",

            "quality":

                self.quality,

            "score":

                self.score,

            "timestamp":

                self.timestamp,

        }
{

"quality":"VERY_GOOD",

"score":84,

"timestamp":"..."

}
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 13-12
# AO SIGNAL EXPLANATION REPORT
# =====================================================

class AOSignalExplanationReport:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.reasons = []

        self.timestamp = None

    # --------------------------------------------

    def evaluate(

        self,

        direction,

        reason_list,

        timestamp,

    ):

        self.direction = direction

        self.timestamp = timestamp

        self.reasons = reason_list.copy()

    # --------------------------------------------

    def report(self):

        return {

            "engine":

                "AO Signal Explanation",

            "direction":

                self.direction,

            "timestamp":

                self.timestamp,

            "reasons":

                self.reasons,

        }
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 13-13
# AO SIGNAL SUMMARY REPORT
# =====================================================

class AOSignalSummaryReport:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.symbol = None

        self.direction = "NONE"

        self.entry = None

        self.stop_loss = None

        self.take_profit = []

        self.score = 0

        self.quality = "UNKNOWN"

        self.timestamp = None

    # --------------------------------------------

    def build(

        self,

        symbol,

        direction,

        entry,

        stop_loss,

        take_profit,

        score,

        quality,

        timestamp,

    ):

        self.symbol = symbol

        self.direction = direction

        self.entry = entry

        self.stop_loss = stop_loss

        self.take_profit = take_profit

        self.score = score

        self.quality = quality

        self.timestamp = timestamp

    # --------------------------------------------

    def report(self):

        return {

            "engine":

                "AO Signal Summary",

            "symbol":

                self.symbol,

            "direction":

                self.direction,

            "entry":

                self.entry,

            "stop_loss":

                self.stop_loss,

            "take_profit":

                self.take_profit,

            "score":

                self.score,

            "quality":

                self.quality,

            "timestamp":

                self.timestamp,

        }
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 13-14
# AO DIAGNOSTIC REPORT
# =====================================================

class AODiagnosticReport:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.engine_status = {}

        self.warning_list = []

        self.error_list = []

        self.timestamp = None

    # --------------------------------------------

    def evaluate(

        self,

        engine_status,

        warnings,

        errors,

        timestamp,

    ):

        self.engine_status = engine_status.copy()

        self.warning_list = warnings.copy()

        self.error_list = errors.copy()

        self.timestamp = timestamp

    # --------------------------------------------

    def report(self):

        return {

            "engine":

                "AO Diagnostic",

            "timestamp":

                self.timestamp,

            "engine_status":

                self.engine_status,

            "warnings":

                self.warning_list,

            "errors":

                self.error_list,

        }
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 13-15
# AO ENGINE PERFORMANCE REPORT
# =====================================================

class AOEnginePerformanceReport:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.execution_time = {}

        self.total_execution_time = 0.0

        self.slowest_engine = None

        self.fastest_engine = None

        self.timestamp = None

    # --------------------------------------------

    def evaluate(

        self,

        execution_time,

        timestamp,

    ):

        self.execution_time = execution_time.copy()

        self.timestamp = timestamp

        self.total_execution_time = sum(

            execution_time.values()

        )

        self.slowest_engine = max(

            execution_time,

            key=execution_time.get

        )

        self.fastest_engine = min(

            execution_time,

            key=execution_time.get

        )

    # --------------------------------------------

    def report(self):

        return {

            "engine":

                "AO Engine Performance",

            "execution_time":

                self.execution_time,

            "total_execution_time":

                round(

                    self.total_execution_time,

                    4

                ),

            "slowest_engine":

                self.slowest_engine,

            "fastest_engine":

                self.fastest_engine,

            "timestamp":

                self.timestamp,

        }
# =====================================================
# AO ENTERPRISE ENGINE
# SECTION 13-16
# AO REPORT MANAGER
# =====================================================

class AOReportManager:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.market_state = None

        self.signal_quality = None

        self.signal_explanation = None

        self.signal_summary = None

        self.diagnostic = None

        self.performance = None

        self.timestamp = None

    # --------------------------------------------

    def update(

        self,

        market_state=None,

        signal_quality=None,

        signal_explanation=None,

        signal_summary=None,

        diagnostic=None,

        performance=None,

        timestamp=None,

    ):

        self.market_state = market_state

        self.signal_quality = signal_quality

        self.signal_explanation = signal_explanation

        self.signal_summary = signal_summary

        self.diagnostic = diagnostic

        self.performance = performance

        self.timestamp = timestamp

    # --------------------------------------------

    def report(self):

        return {

            "engine":

                "AO Report Manager",

            "timestamp":

                self.timestamp,

            "market_state":

                self.market_state,

            "signal_quality":

                self.signal_quality,

            "signal_explanation":

                self.signal_explanation,

            "signal_summary":

                self.signal_summary,

            "diagnostic":

                self.diagnostic,

            "performance":

                self.performance,

        }
# =====================================================
# ENTERPRISE TRADING BOT
# SECTION 14
# SIGNAL ENGINE
# =====================================================

class SignalEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------

    def reset(self):

        self.direction = "NONE"

        self.score = 0

        self.confidence = "UNKNOWN"

        self.entry = None

        self.stop_loss = None

        self.take_profit = []

        self.reasons = []

        self.status = "NO SIGNAL"

    # ------------------------------------------------

    def evaluate(

        self,

        ao_result,

        rsi_result,

        ichimoku_result,

        pivot_result,

        candle_result,

        ao_score,

        rsi_score,

        ichimoku_score,

        pivot_score,

        candle_score,

    ):

        self.reset()

        total_score = (

            ao_score

            + rsi_score

            + ichimoku_score

            + pivot_score

            + candle_score

        )

        self.score = round(

            total_score,

            2

        )
# =====================================================
# ENTERPRISE TRADING BOT
# SECTION 14-1
# SIGNAL VALIDATION ENGINE
# =====================================================

class SignalValidationEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------

    def reset(self):

        self.valid = False

        self.reasons = []

        self.failed_conditions = []

    # ------------------------------------------------

    def validate(

        self,

        ao_signal,

        rsi_signal,

        ichimoku_signal,

        pivot_signal,

        candle_signal,

    ):

        self.reset()

        signals = [

            ao_signal,

            rsi_signal,

            ichimoku_signal,

            pivot_signal,

            candle_signal,

        ]

        buy_count = signals.count("BUY")

        sell_count = signals.count("SELL")

        if buy_count >= 3:

            self.valid = True

            self.reasons.append(

                "BUY confirmed"

            )

        elif sell_count >= 3:

            self.valid = True

            self.reasons.append(

                "SELL confirmed"

            )

        else:

            self.valid = False

            self.failed_conditions.append(

                "Not enough confirmation"

            )

    # ------------------------------------------------

    def report(self):

        return {

            "engine":

                "Signal Validation",

            "valid":

                self.valid,

            "reasons":

                self.reasons,

            "failed":

                self.failed_conditions,

        }
# =====================================================
# ENTERPRISE TRADING BOT
# SECTION 14-2
# SIGNAL SCORING ENGINE
# =====================================================

class SignalScoringEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------

    def reset(self):

        self.total_score = 0

        self.score_details = {}

        self.confidence = "UNKNOWN"

    # ------------------------------------------------

    def calculate(

        self,

        ao_score,

        rsi_score,

        ichimoku_score,

        pivot_score,

        candle_score,

    ):

        self.reset()

        self.score_details = {

            "AO": ao_score,

            "RSI": rsi_score,

            "ICHIMOKU": ichimoku_score,

            "PIVOT": pivot_score,

            "CANDLE": candle_score,

        }

        self.total_score = round(

            sum(

                self.score_details.values()

            ),

            2,

        )

        if self.total_score >= 90:

            self.confidence = "VERY HIGH"

        elif self.total_score >= 80:

            self.confidence = "HIGH"

        elif self.total_score >= 70:

            self.confidence = "MEDIUM"

        elif self.total_score >= 60:

            self.confidence = "LOW"

        else:

            self.confidence = "VERY LOW"

    # ------------------------------------------------

    def report(self):

        return {

            "engine":

                "Signal Scoring",

            "score":

                self.total_score,

            "confidence":

                self.confidence,

            "details":

                self.score_details,

        }
# =====================================================
# ENTERPRISE TRADING BOT
# SECTION 14-3
# TRADE EXECUTION FILTER ENGINE
# =====================================================

class TradeExecutionFilterEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------

    def reset(self):

        self.allow_trade = False

        self.reason = []

        self.failed = []

    # ------------------------------------------------

    def evaluate(

        self,

        signal_valid,

        signal_score,

        confidence,

        risk_reward,

        market_status,

    ):

        self.reset()

        # ===== Signal Validation =====

        if not signal_valid:

            self.failed.append(

                "Signal Validation Failed"

            )

        # ===== Minimum Score =====

        if signal_score < 70:

            self.failed.append(

                "Score below minimum"

            )

        # ===== Confidence =====

        if confidence not in [

            "HIGH",

            "VERY HIGH"

        ]:

            self.failed.append(

                "Confidence too low"

            )

        # ===== Risk Reward =====

        if risk_reward < 1:

            self.failed.append(

                "Risk Reward below 1"

            )

        # ===== Market Status =====

        if market_status == "UNKNOWN":

            self.failed.append(

                "Unknown Market State"

            )

        # ===== Final Decision =====

        if len(self.failed) == 0:

            self.allow_trade = True

            self.reason.append(

                "Trade Approved"

            )

        else:

            self.allow_trade = False
# =====================================================
# ENTERPRISE TRADING BOT
# SECTION 14-4
# ENTRY PRICE VALIDATION ENGINE
# =====================================================

class EntryPriceValidationEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------

    def reset(self):

        self.valid = False

        self.entry_price = None

        self.reasons = []

        self.failed = []

    # ------------------------------------------------

    def evaluate(

        self,

        current_price,

        proposed_entry,

        direction,

        spread,

        slippage,

    ):

        self.reset()

        self.entry_price = proposed_entry

        # ===== Spread Check =====

        if spread > 0.30:

            self.failed.append(

                "Spread too high"

            )

        # ===== Slippage Check =====

        if slippage > 0.20:

            self.failed.append(

                "Slippage too high"

            )

        # ===== Entry Distance =====

        distance = abs(

            current_price -

            proposed_entry

        )

        if distance > (

            current_price * 0.005

        ):

            self.failed.append(

                "Entry too far"

            )

        # ===== Final Decision =====

        if len(self.failed) == 0:

            self.valid = True

            self.reasons.append(

                "Entry Confirmed"

            )
# =====================================================
# ENTERPRISE TRADING BOT
# SECTION 14-5
# STOP LOSS VALIDATION ENGINE
# =====================================================

class StopLossValidationEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------

    def reset(self):

        self.valid = False

        self.stop_loss = None

        self.distance = 0

        self.failed = []

    # ------------------------------------------------

    def evaluate(

        self,

        entry,

        stop_loss,

        direction,

    ):

        self.reset()

        self.stop_loss = stop_loss

        self.distance = abs(

            entry -

            stop_loss

        )

        # ===== BUY =====

        if direction == "BUY":

            if stop_loss >= entry:

                self.failed.append(

                    "Invalid BUY Stop Loss"

                )

        # ===== SELL =====

        elif direction == "SELL":

            if stop_loss <= entry:

                self.failed.append(

                    "Invalid SELL Stop Loss"

                )

        # ===== Distance =====

        if self.distance <= 0:

            self.failed.append(

                "Zero Stop Distance"

            )

        # ===== Final =====

        if len(self.failed) == 0:

            self.valid = True
# =====================================================
# ENTERPRISE TRADING BOT
# SECTION 14-6
# TAKE PROFIT VALIDATION ENGINE
# =====================================================

class TakeProfitValidationEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------

    def reset(self):

        self.valid = False

        self.tp1 = None

        self.tp2 = None

        self.tp3 = None

        self.failed = []

    # ------------------------------------------------

    def evaluate(

        self,

        entry,

        tp1,

        tp2,

        tp3,

        direction,

    ):

        self.reset()

        self.tp1 = tp1

        self.tp2 = tp2

        self.tp3 = tp3

        # ===== BUY =====

        if direction == "BUY":

            if not (

                tp1 > entry and

                tp2 > tp1 and

                tp3 > tp2

            ):

                self.failed.append(

                    "Invalid BUY Take Profit"

                )

        # ===== SELL =====

        elif direction == "SELL":

            if not (

                tp1 < entry and

                tp2 < tp1 and

                tp3 < tp2

            ):

                self.failed.append(

                    "Invalid SELL Take Profit"

                )

        # ===== Final =====

        if len(self.failed) == 0:

            self.valid = True
# =====================================================
# ENTERPRISE TRADING BOT
# SECTION 14-7
# RISK REWARD VALIDATION ENGINE
# =====================================================

class RiskRewardValidationEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------

    def reset(self):

        self.valid = False

        self.risk = 0

        self.reward = 0

        self.risk_reward = 0

        self.failed = []

    # ------------------------------------------------

    def evaluate(

        self,

        entry,

        stop_loss,

        take_profit,

    ):

        self.reset()

        self.risk = abs(

            entry -

            stop_loss

        )

        self.reward = abs(

            take_profit -

            entry

        )

        if self.risk == 0:

            self.failed.append(

                "Risk equals zero"

            )

            return

        self.risk_reward = round(

            self.reward /

            self.risk,

            2

        )

        # ===== Minimum RR =====

        if self.risk_reward < 1.0:

            self.failed.append(

                "Risk / Reward below minimum"

            )

        else:

            self.valid = True

    # ------------------------------------------------

    def report(self):

        return {

            "engine":

                "Risk Reward Validation",

            "risk":

                self.risk,

            "reward":

                self.reward,

            "risk_reward":

                self.risk_reward,

            "valid":

                self.valid,

            "failed":

                self.failed,

        }
# =====================================================
# ENTERPRISE TRADING BOT
# SECTION 14-8
# FINAL SIGNAL ENGINE
# =====================================================

class FinalSignalEngine:

    def __init__(self):

        self.reset()

    # --------------------------------------------

    def reset(self):

        self.signal = "NO TRADE"

        self.direction = "NONE"

        self.score = 0

    # --------------------------------------------

    def evaluate(

        self,

        validation_ok,

        execution_ok,

        sl_ok,

        tp_ok,

        rr_ok,

        final_score,

        direction,

    ):

        self.reset()

        self.score = final_score

        if (

            validation_ok

            and execution_ok

            and sl_ok

            and tp_ok

            and rr_ok

        ):

            self.signal = "TRADE"

            self.direction = direction

        else:

            self.signal = "NO TRADE"

            self.direction = "NONE"

    # --------------------------------------------

    def report(self):

        return {

            "signal": self.signal,

            "direction": self.direction,

            "score": self.score,

        }
# =====================================================
# ENTERPRISE TRADING BOT
# SECTION 15
# TRADE MANAGEMENT ENGINE
# =====================================================

class TradeManagementEngine:

    def __init__(self):

        self.reset()

    # ------------------------------------------------

    def reset(self):

        self.trade_status = "CLOSED"

        self.position_size = 0

        self.entry_price = None

        self.stop_loss = None

        self.take_profit = []

        self.current_profit = 0

        self.current_loss = 0

    # ------------------------------------------------

    def open_trade(

        self,

        position_size,

        entry_price,

        stop_loss,

        take_profit,

    ):

        self.trade_status = "OPEN"

        self.position_size = position_size

        self.entry_price = entry_price

        self.stop_loss = stop_loss

        self.take_profit = take_profit

    # ------------------------------------------------

    def close_trade(self):

        self.trade_status = "CLOSED"

    # ------------------------------------------------

    def report(self):

        return {

            "status":

                self.trade_status,

            "entry":

                self.entry_price,

            "stop_loss":

                self.stop_loss,

            "take_profit":

                self.take_profit,

            "position_size":

                self.position_size,

            "profit":

                self.current_profit,

            "loss":

                self.current_loss,

        }