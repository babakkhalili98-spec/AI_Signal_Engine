"""
=========================================================
AI SIGNAL ENGINE
Settings V3
Optimized For Nobitex
=========================================================
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# =========================================================
# Load ENV
# =========================================================

load_dotenv()

# =========================================================
# Paths
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_DIR = BASE_DIR / "config"
CORE_DIR = BASE_DIR / "core"
DATABASE_DIR = BASE_DIR / "database"
LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"
CACHE_DIR = BASE_DIR / "cache"
BACKTEST_DIR = BASE_DIR / "backtest"
MODEL_DIR = BASE_DIR / "models"
TEMP_DIR = BASE_DIR / "temp"
EXPORT_DIR = BASE_DIR / "exports"

IMAGE_DIR = REPORT_DIR / "charts"
PDF_DIR = REPORT_DIR / "pdf"

DATABASE_BACKUP = DATABASE_DIR / "backup"
JOURNAL_PATH = REPORT_DIR / "journal"

# =========================================================
# Create Directories
# =========================================================

DIRECTORIES = [

    DATABASE_DIR,
    LOG_DIR,
    REPORT_DIR,
    CACHE_DIR,
    BACKTEST_DIR,
    MODEL_DIR,
    TEMP_DIR,
    EXPORT_DIR,
    IMAGE_DIR,
    PDF_DIR,
    DATABASE_BACKUP,
    JOURNAL_PATH,

]

for directory in DIRECTORIES:

    directory.mkdir(

        parents=True,
        exist_ok=True,

    )

# =========================================================
# Application
# =========================================================

APP_NAME = "AI Signal Engine"

ENGINE_NAME = APP_NAME

ENGINE_VERSION = "3.0"

ENGINE_AUTHOR = "Babak Khalili"

BUILD_DATE = "2026-07-26"

DEBUG = True

TIMEZONE = "Asia/Tehran"

LANGUAGE = "fa"

ENCODING = "utf-8"

# =========================================================
# Database
# =========================================================

DATABASE_PATH = DATABASE_DIR / "ai_signal_engine.db"

DATABASE_TIMEOUT = 30

DATABASE_CACHE_SIZE = 10000

DATABASE_SYNCHRONOUS = "NORMAL"

DATABASE_FOREIGN_KEYS = True

DATABASE_AUTO_VACUUM = True

DATABASE_MAX_CONNECTIONS = 1

# =========================================================
# Logging
# =========================================================

LOG_LEVEL = "INFO"

LOG_FILE = LOG_DIR / "ai_signal_engine.log"

ERROR_LOG = LOG_DIR / "error.log"

MAX_LOG_SIZE = 20 * 1024 * 1024

LOG_BACKUP_COUNT = 10

LOG_FORMAT = (

    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"

)

# =========================================================
# Exchange
# =========================================================

EXCHANGE_NAME = "NOBITEX"

API_TIMEOUT = 20

API_RETRY = 3

API_RETRY_DELAY = 3

VERIFY_SSL = True

REQUESTS_PER_SECOND = 2

MAX_THREADS = 2

WORKER_THREADS = 2

# =========================================================
# Nobitex
# =========================================================

NOBITEX_API_KEY = os.getenv(
    "NOBITEX_API_KEY",
    ""
)

NOBITEX_BASE_URL = "https://apiv2.nobitex.ir"

NOBITEX_TIMEOUT = 20

NOBITEX_MAX_RETRY = 3

NOBITEX_SLEEP = 1.5

# =========================================================
# Telegram
# =========================================================

TELEGRAM_ENABLED = True

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    ""
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    ""
)

TELEGRAM_TIMEOUT = 20

TELEGRAM_RETRY = 3

# =========================================================
# Bale
# =========================================================

BALE_ENABLED = False

BALE_BOT_TOKEN = os.getenv(
    "BALE_BOT_TOKEN",
    ""
)

BALE_CHAT_ID = os.getenv(
    "BALE_CHAT_ID",
    ""
)

BALE_TIMEOUT = 20

BALE_RETRY = 3

# =========================================================
print("=" * 60)
print(f"{ENGINE_NAME} Settings Loaded")
print(f"Version : {ENGINE_VERSION}")
print("=" * 60)
# =========================================================
# Capital & Risk Management
# =========================================================

DEFAULT_CAPITAL = 1000.0

POSITION_SIZE_PERCENT = 5.0

RISK_PER_TRADE = 0.05

DEFAULT_LEVERAGE = 8

MIN_RISK_REWARD = 1.0

MAX_OPEN_POSITIONS = 7

MAX_DAILY_TRADES = 30

ALLOW_MULTI_SYMBOL = True

USE_DYNAMIC_POSITION_SIZE = True

MOVE_SL_TO_BREAK_EVEN = True

TRAILING_STOP = True

TRAILING_STOP_DISTANCE = 0.5

# =========================================================
# Take Profit
# =========================================================

TP1_PERCENT = 0.25

TP2_PERCENT = 0.35

TP3_PERCENT = 0.40

# =========================================================
# Scanner
# =========================================================

SCAN_INTERVAL = 30

SCAN_DELAY_SECONDS = 30

MAX_SYMBOLS_PER_SCAN = 300

MAX_THREADS = 2

WORKER_THREADS = 2

SAVE_SCAN_HISTORY = True

# =========================================================
# TimeFrames Supported By Nobitex API
# =========================================================

TIMEFRAMES = [

    "1m",
    "5m",
    "15m",
    "30m",

    "1h",
    "2h",
    "4h",

    "1d",

]

# =========================================================
# Synthetic TimeFrames
# (ساخته می‌شوند، از API گرفته نمی‌شوند)
# =========================================================

CUSTOM_TIMEFRAMES = {

    "8h":  ("4h", 2),

    "12h": ("4h", 3),

    "3d":  ("1d", 3),

    "1w":  ("1d", 7),

    "1M":  ("1d", 30),

}

# =========================================================
# Main Analysis TimeFrames
# =========================================================

PRIMARY_TIMEFRAMES = [

    "30m",

    "1h",

    "4h",

    "1d",

]

# =========================================================
# Scanner TimeFrames
# =========================================================

SCAN_TIMEFRAMES = [

    "15m",

    "30m",

    "1h",

    "4h",

    "1d",

]

# =========================================================
# Candle Settings
# =========================================================

CANDLE_LIMIT = 300

MIN_REQUIRED_CANDLES = 150

MAX_REQUIRED_CANDLES = 500

# =========================================================
# Symbols
# =========================================================

DEFAULT_SYMBOLS = [

    "BTCUSDT",

    "ETHUSDT",

    "BNBUSDT",

    "SOLUSDT",

    "XRPUSDT",

    "DOGEUSDT",

    "ADAUSDT",

    "AVAXUSDT",

]

AUTO_LOAD_SYMBOLS = True

# =========================================================
# Pivot TimeFrames
# =========================================================

PIVOT_TIMEFRAMES = [

    "1h",

    "4h",

    "1d",

]

# =========================================================
# Score
# =========================================================

MIN_SIGNAL_SCORE = 72

BUY_SCORE_LIMIT = 72

SELL_SCORE_LIMIT = 72

STRONG_SIGNAL_SCORE = 90

WEAK_SIGNAL_SCORE = 50

SIGNAL_GRADE = {

    "C": 72,

    "B": 80,

    "B+": 85,

    "A": 90,

    "A+": 95,

}
# =========================================================
# AI ENGINE
# =========================================================

AI_ENABLED = True

LEARNING_MODE = True

SAVE_MARKET_MEMORY = True

USE_MARKET_DNA = True

USE_SIGNAL_MEMORY = True

USE_PATTERN_MEMORY = True

AI_CONFIDENCE_LIMIT = 70

# =========================================================
# SCORE ENGINE
# =========================================================

MIN_SIGNAL_SCORE = 72

BUY_SCORE_LIMIT = 72

SELL_SCORE_LIMIT = 72

STRONG_SIGNAL_SCORE = 90

WEAK_SIGNAL_SCORE = 50

SIGNAL_GRADE = {

    "C": 72,

    "B": 80,

    "B+": 85,

    "A": 90,

    "A+": 95,

}

# =========================================================
# INDICATORS
# =========================================================

USE_RSI = True

USE_ICHIMOKU = True

USE_PIVOT = True

USE_AO = True

USE_CANDLE_PATTERN = True

USE_HARMONIC = True

USE_FIBONACCI = True

USE_VOLUME = True

USE_ORDERBOOK = True

USE_OPEN_INTEREST = True

USE_FUNDING_RATE = True

USE_CVD = True

# =========================================================
# RSI
# =========================================================

RSI_PERIOD = 14

RSI_OVERBOUGHT = 80

RSI_OVERSOLD = 20

# =========================================================
# ICHIMOKU
# =========================================================

ICHIMOKU_TENKAN = 9

ICHIMOKU_KIJUN = 26

ICHIMOKU_SENKOU = 52

# =========================================================
# FIBONACCI
# =========================================================

FIB_LEVELS = [

    0.236,

    0.382,

    0.500,

    0.618,

    0.786,

    0.886,

    1.000,

    1.272,

    1.382,

    1.618,

]

# =========================================================
# CHART ENGINE
# =========================================================

SAVE_CHARTS = True

CHART_WIDTH = 1600

CHART_HEIGHT = 900

CHART_DPI = 120

SHOW_INDICATORS = True

SHOW_ENTRY_EXIT = True

# =========================================================
# CACHE
# =========================================================

CACHE_ENABLED = True

CACHE_EXPIRE = 300

CACHE_MAX_ITEMS = 1000

# =========================================================
# NEWS ENGINE
# =========================================================

USE_NEWS = True

NEWS_IMPORTANCE = [

    "red",

    "orange",

]

NEWS_LOOKBACK_HOURS = 24

NEWS_UPDATE_INTERVAL = 300

# =========================================================
# MARKET MEMORY
# =========================================================

ENABLE_MARKET_MEMORY = True

MEMORY_MAX_RECORDS = 500000

SAVE_SIGNAL_HISTORY = True

SAVE_TRADE_HISTORY = True

SAVE_NEWS_HISTORY = True

# =========================================================
# RESEARCH ENGINE
# =========================================================

RESEARCH_ENABLED = True

RESEARCH_REPORT_WEEKLY = True

RESEARCH_CREATE_HYPOTHESIS = True

RESEARCH_QUEUE_SIZE = 500

RESEARCH_VALIDATE_INDICATORS = True
# =========================================================
# BACKTEST
# =========================================================

BACKTEST_ENABLED = True

BACKTEST_INITIAL_CAPITAL = 1000

BACKTEST_COMMISSION = 0.001

BACKTEST_SLIPPAGE = 0.0005

BACKTEST_SAVE_TRADES = True

BACKTEST_SAVE_REPORT = True

BACKTEST_SHOW_EQUITY = True

# =========================================================
# PERFORMANCE
# =========================================================

ENABLE_MULTITHREADING = True

WORKER_THREADS = 4

MAX_THREADS = 4

ASYNC_QUEUE_SIZE = 1000

MAX_CPU_USAGE = 90

MAX_RAM_USAGE = 85

# =========================================================
# API
# =========================================================

API_TIMEOUT = 20

API_RETRY = 3

API_RETRY_DELAY = 2

REQUESTS_PER_SECOND = 2

# =========================================================
# SCHEDULER
# =========================================================

ENABLE_SCHEDULER = True

SCAN_DELAY_SECONDS = 30

REPORT_DELAY_SECONDS = 5

DATABASE_SAVE_INTERVAL = 60

# =========================================================
# SECURITY
# =========================================================

VERIFY_SSL = True

ALLOW_ENV_OVERRIDE = True

MASK_API_KEYS = True

# =========================================================
# EXPORT
# =========================================================

EXPORT_CSV = True

EXPORT_JSON = True

EXPORT_PDF = True

EXPORT_EXCEL = False

EXPORT_SIGNAL_HISTORY = True

EXPORT_BACKTEST = True

# =========================================================
# NOTIFICATION
# =========================================================

SEND_SIGNAL_TO_TELEGRAM = True

SEND_SIGNAL_TO_BALE = False

SEND_ERROR_NOTIFICATION = True

SEND_DAILY_REPORT = True

SEND_WEEKLY_REPORT = True

SEND_MONTHLY_REPORT = True

# =========================================================
# DEBUG
# =========================================================

PRINT_SIGNALS = True

PRINT_SCORES = True

PRINT_DATABASE = False

PRINT_API = False

PRINT_NEWS = False

PRINT_INDICATORS = False

PRINT_RISK = False

PRINT_TIMEFRAME = True

# =========================================================
# ENGINE
# =========================================================

ENGINE_NAME = "AI Signal Engine"

ENGINE_VERSION = "2.0"

ENGINE_AUTHOR = "Babak Khalili"

BUILD_DATE = "2026-07-26"

# =========================================================
# STARTUP
# =========================================================

print("=" * 60)
print(f"{ENGINE_NAME} Settings Loaded")
print(f"Version : {ENGINE_VERSION}")
print("=" * 60)