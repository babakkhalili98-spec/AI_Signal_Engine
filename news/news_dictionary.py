"""
=========================================================
AI Signal Engine
News Dictionary
Version : 1.0
=========================================================
"""

NEWS_DICTIONARY = {

# =========================================================
# CPI
# =========================================================

"CPI m/m":{

"fa":"شاخص قیمت مصرف کننده آمریکا (ماهانه)",

"country":"USA",

"currency":"USD",

"importance":"HIGH",

"markets":[

"Forex",

"Gold",

"Silver",

"Crypto",

"US Stocks",

"Bonds",

"DXY"

],

"positive":{

"condition":"Actual > Forecast",

"usd":"Bullish",

"gold":"Bearish",

"silver":"Bearish",

"crypto":"Bearish",

"stocks":"Bearish",

"bonds":"Bullish",

"dxy":"Bullish"

},

"negative":{

"condition":"Actual < Forecast",

"usd":"Bearish",

"gold":"Bullish",

"silver":"Bullish",

"crypto":"Bullish",

"stocks":"Bullish",

"bonds":"Bearish",

"dxy":"Bearish"

}

},

# =========================================================
# Core CPI
# =========================================================

"Core CPI m/m":{

"fa":"شاخص قیمت مصرف کننده هسته آمریکا",

"country":"USA",

"currency":"USD",

"importance":"HIGH",

"markets":[

"Forex",

"Gold",

"Crypto",

"DXY",

"Stocks"

],

"positive":{

"condition":"Actual > Forecast",

"usd":"Bullish",

"gold":"Bearish",

"crypto":"Bearish",

"stocks":"Bearish",

"dxy":"Bullish"

},

"negative":{

"condition":"Actual < Forecast",

"usd":"Bearish",

"gold":"Bullish",

"crypto":"Bullish",

"stocks":"Bullish",

"dxy":"Bearish"

}

},

# =========================================================
# PPI
# =========================================================

"PPI m/m":{

"fa":"شاخص قیمت تولیدکننده",

"country":"USA",

"currency":"USD",

"importance":"HIGH",

"markets":[

"Forex",

"Gold",

"Crypto"

],

"positive":{

"condition":"Actual > Forecast",

"usd":"Bullish",

"gold":"Bearish",

"crypto":"Bearish"

},

"negative":{

"condition":"Actual < Forecast",

"usd":"Bearish",

"gold":"Bullish",

"crypto":"Bullish"

}

},

# =========================================================
# NFP
# =========================================================

"Non-Farm Employment Change":{

"fa":"اشتغال بخش غیرکشاورزی",

"country":"USA",

"currency":"USD",

"importance":"HIGH",

"markets":[

"Forex",

"Gold",

"Crypto",

"Stocks"

],

"positive":{

"condition":"Actual > Forecast",

"usd":"Bullish",

"gold":"Bearish",

"crypto":"Bearish",

"stocks":"Mixed"

},

"negative":{

"condition":"Actual < Forecast",

"usd":"Bearish",

"gold":"Bullish",

"crypto":"Bullish",

"stocks":"Mixed"

}

},

# =========================================================
# FED RATE
# =========================================================

"Federal Funds Rate":{

"fa":"نرخ بهره فدرال رزرو",

"country":"USA",

"currency":"USD",

"importance":"VERY_HIGH",

"markets":[

"Forex",

"Gold",

"Crypto",

"Stocks",

"Bonds",

"DXY"

],

"positive":{

"condition":"Rate Higher",

"usd":"Bullish",

"gold":"Bearish",

"crypto":"Bearish",

"stocks":"Bearish",

"dxy":"Bullish"

},

"negative":{

"condition":"Rate Lower",

"usd":"Bearish",

"gold":"Bullish",

"crypto":"Bullish",

"stocks":"Bullish",

"dxy":"Bearish"

}

},

# =========================================================
# FOMC
# =========================================================

"FOMC Statement":{

"fa":"بیانیه کمیته بازار آزاد فدرال",

"country":"USA",

"currency":"USD",

"importance":"VERY_HIGH",

"markets":[

"ALL"

]

},

# =========================================================
# GDP
# =========================================================

"GDP q/q":{

"fa":"تولید ناخالص داخلی",

"country":"USA",

"currency":"USD",

"importance":"HIGH",

"markets":[

"Forex",

"Stocks",

"Crypto"

]

},

# =========================================================
# Retail Sales
# =========================================================

"Retail Sales m/m":{

"fa":"خرده فروشی آمریکا",

"country":"USA",

"currency":"USD",

"importance":"HIGH",

"markets":[

"Forex",

"Stocks",

"Gold"

]

},

# =========================================================
# Unemployment
# =========================================================

"Unemployment Rate":{

"fa":"نرخ بیکاری",

"country":"USA",

"currency":"USD",

"importance":"HIGH",

"markets":[

"Forex",

"Gold",

"Crypto"

]

}

}