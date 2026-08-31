"""
=========================================================
AI Signal Engine
Signal Recovery Engine
Version : 3.0.0
=========================================================

وظایف

• مانیتور معاملات باز
• بررسی TP1 TP2 TP3
• بررسی StopLoss
• Recovery بعد از ری استارت
• Trailing Stop
• BreakEven
• Journal
• Learning

=========================================================
"""

from __future__ import annotations

import logging
import threading
import time

from datetime import datetime
from typing import Dict
from typing import Optional

from core.database_manager import DatabaseManager
from core.market_data import MarketData


# ==========================================================
# Signal Recovery Engine
# ==========================================================

class SignalRecoveryEngine:

    """
    این موتور تمام معاملات باز را مانیتور می‌کند.
    """

    def __init__(self):

        self.logger = logging.getLogger(

            "SignalRecovery"

        )

        self.database = DatabaseManager()

        self.market = MarketData()

        self.running = False

        self.worker: Optional[
            threading.Thread
        ] = None

        self.open_trades: Dict = {}

        self.check_interval = 5

        self.logger.info(

            "Signal Recovery Engine Initialized"

        )

    # -------------------------------------------------

    def initialize(self):

        """
        آماده‌سازی Engine
        """

        self.database.initialize()

        self.market.initialize()

        self.load_open_trades()

    # -------------------------------------------------

    def load_open_trades(self):

        """
        بازیابی معاملات باز از دیتابیس
        """

        trades = self.database.get_open_trades()

        self.open_trades.clear()

        for trade in trades:

            self.open_trades[
                trade["report_id"]
            ] = dict(trade)

        self.logger.info(

            f"{len(self.open_trades)} "

            f"Open Trades Loaded"

        )

    # -------------------------------------------------

    def start(self):

        """
        شروع مانیتورینگ
        """

        if self.running:

            return

        self.running = True

        self.worker = threading.Thread(

            target=self.run,

            daemon=True

        )

        self.worker.start()

        self.logger.info(

            "Signal Recovery Started"

        )
    # -------------------------------------------------
    # Main Loop
    # -------------------------------------------------

    def run(self):
        """
        حلقه اصلی مانیتورینگ
        """

        self.logger.info(

            "Recovery Loop Started"

        )

        while self.running:

            try:

                self.run_once()

            except Exception as ex:

                self.logger.exception(ex)

            time.sleep(

                self.check_interval

            )

        self.logger.info(

            "Recovery Loop Stopped"

        )

    # -------------------------------------------------
    # Run Once
    # -------------------------------------------------

    def run_once(self):
        """
        بررسی یک دور کامل معاملات باز
        """

        if not self.running:

            return

        if len(self.open_trades) == 0:

            return

        for report_id in list(

            self.open_trades.keys()

        ):

            trade = self.open_trades.get(

                report_id

            )

            if trade is None:

                continue

            self.check_trade(

                trade

            )

    # -------------------------------------------------
    # Check Trade
    # -------------------------------------------------

    def check_trade(

        self,

        trade

    ):

        """
        بررسی وضعیت یک معامله
        """

        symbol = trade["symbol"]

        price = self.market.last_price(

            symbol

        )

        if price is None:

            return

        trade["current_price"] = price

        self.database.update_trade_status(

            report_id=trade["report_id"],

            status=trade["status"],

            current_price=price,

            hit_time=datetime.utcnow()

        )

        self.check_take_profit(

            trade,

            price

        )

        self.check_stop_loss(

            trade,

            price

        )

    # -------------------------------------------------
    # Remove Closed Trade
    # -------------------------------------------------

    def remove_trade(

        self,

        report_id

    ):

        """
        حذف معامله از حافظه
        """

        if report_id in self.open_trades:

            del self.open_trades[

                report_id

            ]

    # -------------------------------------------------
    # Reload
    # -------------------------------------------------

    def reload_open_trades(self):
        """
        بارگذاری مجدد معاملات باز
        """

        self.load_open_trades()
    # -------------------------------------------------
    # Take Profit
    # -------------------------------------------------

    def check_take_profit(

        self,

        trade,

        price

    ):

        """
        بررسی TP1 / TP2 / TP3
        """

        report_id = trade["report_id"]

        status = trade["status"]

        # ---------------- TP1 ----------------

        if status == "OPEN":

            if price >= trade["tp1"]:

                trade["status"] = "TP1"

                self.database.update_trade_status(

                    report_id,

                    "TP1",

                    price,

                    datetime.utcnow()

                )

                self.on_tp_hit(

                    trade,

                    "TP1",

                    price

                )

                return

        # ---------------- TP2 ----------------

        if status == "TP1":

            if price >= trade["tp2"]:

                trade["status"] = "TP2"

                self.database.update_trade_status(

                    report_id,

                    "TP2",

                    price,

                    datetime.utcnow()

                )

                self.on_tp_hit(

                    trade,

                    "TP2",

                    price

                )

                return

        # ---------------- TP3 ----------------

        if status == "TP2":

            if price >= trade["tp3"]:

                trade["status"] = "TP3"

                self.database.update_trade_status(

                    report_id,

                    "TP3",

                    price,

                    datetime.utcnow()

                )

                self.close_trade(

                    trade,

                    price,

                    "TP3"

                )

    # -------------------------------------------------
    # Stop Loss
    # -------------------------------------------------

    def check_stop_loss(

        self,

        trade,

        price

    ):

        """
        بررسی Stop Loss
        """

        if price > trade["stop_loss"]:

            return

        self.close_trade(

            trade,

            price,

            "SL"

        )

    # -------------------------------------------------
    # TP Event
    # -------------------------------------------------

    def on_tp_hit(

        self,

        trade,

        level,

        price

    ):

        """
        رخداد برخورد TP
        """

        self.logger.info(

            f"{trade['symbol']} "

            f"{level} HIT"

        )

        # بعداً

        # ارسال تلگرام

        # ثبت ژورنال

        # ثبت Learning

    # -------------------------------------------------
    # Close Trade
    # -------------------------------------------------

    def close_trade(

        self,

        trade,

        exit_price,

        result

    ):

        """
        بستن معامله
        """

        entry = trade["entry"]

        profit = (

            (exit_price - entry)

            / entry

        ) * 100

        self.database.close_trade(

            trade["report_id"],

            exit_price,

            profit

        )

        self.logger.info(

            f"{trade['symbol']} "

            f"{result} "

            f"{profit:.2f}%"

        )

        self.remove_trade(

            trade["report_id"]

        )

        self.database.remove_recovery(

            trade["report_id"]

        )

        # در بخش بعد

        # Journal

        # Learning

        # Telegram

        # Report
    # -------------------------------------------------
    # Break Even
    # -------------------------------------------------

    def update_break_even(

        self,

        trade

    ):

        """
        انتقال StopLoss به نقطه ورود
        """

        if trade.get("break_even"):

            return

        trade["stop_loss"] = trade["entry"]

        trade["break_even"] = True

        self.database.update_trade_status(

            report_id=trade["report_id"],

            status="BREAK_EVEN",

            current_price=trade["current_price"],

            hit_time=datetime.utcnow()

        )

        self.logger.info(

            f"{trade['symbol']} "

            f"Break Even Activated"

        )

    # -------------------------------------------------
    # Trailing Stop
    # -------------------------------------------------

    def update_trailing_stop(

        self,

        trade,

        price

    ):

        """
        Trailing Stop
        """

        trailing_percent = 1.0

        new_stop = price * (

            1 - trailing_percent / 100

        )

        if new_stop > trade["stop_loss"]:

            trade["stop_loss"] = new_stop

            self.database.update_trade_status(

                report_id=trade["report_id"],

                status="TRAILING",

                current_price=price,

                hit_time=datetime.utcnow()

            )

            self.logger.info(

                f"{trade['symbol']} "

                f"Trailing Stop Updated"

            )

    # -------------------------------------------------
    # Partial Close
    # -------------------------------------------------

    def partial_close(

        self,

        trade,

        percent,

        level

    ):

        """
        بستن بخشی از معامله
        """

        self.logger.info(

            f"{trade['symbol']} "

            f"Partial Close "

            f"{percent}% "

            f"{level}"

        )

    # -------------------------------------------------
    # BUY / SELL Logic
    # -------------------------------------------------

    def price_hit_tp(

        self,

        trade,

        tp,

        price

    ):

        """
        بررسی رسیدن به TP
        """

        if trade["signal_type"] == "BUY":

            return price >= tp

        return price <= tp

    # -------------------------------------------------

    def price_hit_sl(

        self,

        trade,

        price

    ):

        """
        بررسی رسیدن به SL
        """

        if trade["signal_type"] == "BUY":

            return price <= trade["stop_loss"]

        return price >= trade["stop_loss"]

    # -------------------------------------------------
    # Manage Trade
    # -------------------------------------------------

    def manage_trade(

        self,

        trade,

        price

    ):

        """
        مدیریت کامل معامله
        """

        if trade["status"] == "OPEN":

            if self.price_hit_tp(

                trade,

                trade["tp1"],

                price

            ):

                self.partial_close(

                    trade,

                    25,

                    "TP1"

                )

                self.update_break_even(

                    trade

                )

        elif trade["status"] == "TP1":

            self.update_trailing_stop(

                trade,

                price

            )

            if self.price_hit_tp(

                trade,

                trade["tp2"],

                price

            ):

                self.partial_close(

                    trade,

                    35,

                    "TP2"

                )

        elif trade["status"] == "TP2":

            self.update_trailing_stop(

                trade,

                price

            )

            if self.price_hit_tp(

                trade,

                trade["tp3"],

                price

            ):

                self.partial_close(

                    trade,

                    40,

                    "TP3"

                )

                self.close_trade(

                    trade,

                    price,

                    "TP3"

                )

        if self.price_hit_sl(

            trade,

            price

        ):

            self.close_trade(

                trade,

                price,

                "SL"

            )
    # -------------------------------------------------
    # Journal
    # -------------------------------------------------

    def save_journal(

        self,

        trade,

        result,

        exit_price,

        profit

    ):

        """
        ثبت ژورنال معامله
        """

        try:

            self.database.execute(

                """

                INSERT INTO journal(

                    report_id,

                    symbol,

                    timeframe,

                    entry,

                    exit,

                    result,

                    profit,

                    note,

                    created_at

                )

                VALUES(

                    ?,?,?,?,?,?,?,?,?

                )

                """,

                (

                    trade["report_id"],

                    trade["symbol"],

                    trade["timeframe"],

                    trade["entry"],

                    exit_price,

                    result,

                    profit,

                    "",

                    datetime.utcnow().isoformat()

                )

            )

        except Exception as ex:

            self.logger.exception(ex)

    # -------------------------------------------------
    # Learning
    # -------------------------------------------------

    def save_learning(

        self,

        trade,

        result

    ):

        """
        ثبت نتیجه برای موتور یادگیری
        """

        try:

            self.database.execute(

                """

                INSERT INTO learning(

                    report_id,

                    symbol,

                    timeframe,

                    score,

                    confidence,

                    result,

                    created_at

                )

                VALUES(

                    ?,?,?,?,?,?,?

                )

                """,

                (

                    trade["report_id"],

                    trade["symbol"],

                    trade["timeframe"],

                    trade.get("score", 0),

                    trade.get("confidence", 0),

                    result,

                    datetime.utcnow().isoformat()

                )

            )

        except Exception as ex:

            self.logger.exception(ex)

    # -------------------------------------------------
    # Statistics
    # -------------------------------------------------

    def statistics(self):

        """
        آمار Recovery
        """

        return {

            "open_trades":

                len(self.open_trades),

            "running":

                self.running,

            "check_interval":

                self.check_interval

        }

    # -------------------------------------------------
    # Health Check
    # -------------------------------------------------

    def health_check(self):

        """
        وضعیت Recovery Engine
        """

        return {

            "running":

                self.running,

            "database":

                self.database.health_check(),

            "market":

                self.market.health_check(),

            "open_trades":

                len(self.open_trades)

        }
    # -------------------------------------------------
    # Recover Open Signals
    # -------------------------------------------------

    def recover_open_signals(self):
        """
        بازیابی معاملات باز بعد از ری‌استارت
        """

        self.logger.info(
            "Recovering Open Signals..."
        )

        # اگر دیتابیس هنوز وصل نشده باشد
        if not self.database.connected:

            self.database.initialize()

        self.load_open_trades()

        self.logger.info(
  
            f"{len(self.open_trades)} Open Signals Recovered"

        )

        return True

    # -------------------------------------------------
    # Shutdown
    # -------------------------------------------------

    def shutdown(self):

        """
        خاموش کردن Recovery Engine
        """

        self.logger.info("")

        self.logger.info("=" * 60)

        self.logger.info(

            "SIGNAL RECOVERY SHUTDOWN"

        )

        self.logger.info("=" * 60)

        self.running = False

        if self.worker is not None:

            self.worker.join(

                timeout=5

            )

        self.market.close()

        self.database.close()

        self.logger.info(

            "Recovery Engine Closed"

        )