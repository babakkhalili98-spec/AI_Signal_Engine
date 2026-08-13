"""
=========================================================
AI Signal Engine
Database Manager
Version : 4.1
=========================================================
"""

from __future__ import annotations

import sqlite3
import threading
import logging

from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

from config.settings import DATABASE_PATH
from config.settings import DATABASE_BACKUP


class DatabaseManager:

    def __init__(self):

        self.logger = logging.getLogger("DatabaseManager")

        self.lock = threading.RLock()

        self.db_path = Path(DATABASE_PATH)

        self.connection = None

        self.cursor = None

        self.connected = False

    # =====================================================
    # Initialize
    # =====================================================

    def initialize(self):

        if self.connected:
            return

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.connection = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False
        )

        self.connection.row_factory = sqlite3.Row

        self.cursor = self.connection.cursor()

        self.connected = True

        self.logger.info(
            f"Database Connected : {self.db_path}"
        )

        self.create_tables()

        self.create_indexes()

    # =====================================================
    # Compatibility
    # =====================================================

    def connect(self):

        self.initialize()

        return True

    def reconnect(self):

        self.close()

        self.initialize()

        return True

    def ensure_connection(self):

        if (
            not self.connected
            or self.connection is None
            or self.cursor is None
        ):
            self.initialize()

    def is_connected(self):

        return (
            self.connected
            and self.connection is not None
            and self.cursor is not None
        )
    # =====================================================
    # Transaction
    # =====================================================

    @contextmanager
    def transaction(self):

        self.ensure_connection()

        with self.lock:

            try:

                yield

                self.connection.commit()

            except Exception:

                if self.connection is not None:

                    self.connection.rollback()

                raise

    # =====================================================
    # Execute
    # =====================================================

    def execute(
        self,
        query,
        values=()
    ):

        self.ensure_connection()

        with self.transaction():

            self.cursor.execute(
                query,
                values
            )

            return self.cursor

    # =====================================================
    # Fetch One
    # =====================================================

    def fetchone(
        self,
        query,
        values=()
    ):

        self.ensure_connection()

        self.cursor.execute(
            query,
            values
        )

        row = self.cursor.fetchone()

        return row

    # =====================================================
    # Fetch All
    # =====================================================

    def fetchall(
        self,
        query,
        values=()
    ):

        self.ensure_connection()

        self.cursor.execute(
            query,
            values
        )

        rows = self.cursor.fetchall()

        return rows

    # =====================================================
    # Execute Many
    # =====================================================

    def executemany(
        self,
        query,
        values
    ):

        self.ensure_connection()

        with self.transaction():

            self.cursor.executemany(
                query,
                values
            )

    # =====================================================
    # Scalar
    # =====================================================

    def scalar(
        self,
        query,
        values=()
    ):

        row = self.fetchone(
            query,
            values
        )

        if row is None:

            return None

        return row[0]
    # =====================================================
    # Create Tables
    # =====================================================

    def create_tables(self):

        self.execute("""

        CREATE TABLE IF NOT EXISTS signals(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            report_id TEXT UNIQUE,

            symbol TEXT,

            timeframe TEXT,

            signal_type TEXT,

            score REAL,

            confidence REAL,

            entry REAL,

            stop_loss REAL,

            tp1 REAL,

            tp2 REAL,

            tp3 REAL,

            created_at TEXT

        )

        """)

        self.execute("""

        CREATE TABLE IF NOT EXISTS trades(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            report_id TEXT UNIQUE,

            symbol TEXT,

            timeframe TEXT,

            signal_type TEXT,

            entry REAL,

            current_price REAL,

            stop_loss REAL,

            tp1 REAL,

            tp2 REAL,

            tp3 REAL,

            status TEXT,

            profit_percent REAL DEFAULT 0,

            break_even INTEGER DEFAULT 0,

            trailing_stop REAL DEFAULT 0,

            opened_at TEXT,

            updated_at TEXT,

            closed_at TEXT

        )

        """)

        self.execute("""

        CREATE TABLE IF NOT EXISTS recovery(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            report_id TEXT UNIQUE,

            symbol TEXT,

            timeframe TEXT,

            state TEXT,

            created_at TEXT,

            updated_at TEXT

        )

        """)

        self.execute("""

        CREATE TABLE IF NOT EXISTS journal(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            report_id TEXT,

            symbol TEXT,

            timeframe TEXT,

            entry REAL,

            exit REAL,

            result TEXT,

            profit REAL,

            note TEXT,

            created_at TEXT

        )

        """)

        self.execute("""

        CREATE TABLE IF NOT EXISTS learning(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            report_id TEXT,

            symbol TEXT,

            timeframe TEXT,

            score REAL,

            confidence REAL,

            result TEXT,

            created_at TEXT

        )

        """)

        self.execute("""

        CREATE TABLE IF NOT EXISTS message_log(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            report_id TEXT,

            message_type TEXT,

            sent INTEGER DEFAULT 0,

            retry INTEGER DEFAULT 0,

            sent_at TEXT

        )

        """)

        self.connection.commit()
    # =====================================================
    # Create Indexes
    # =====================================================

    def create_indexes(self):

        indexes = [

            """
            CREATE INDEX IF NOT EXISTS idx_signal_symbol
            ON signals(symbol)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_trade_symbol
            ON trades(symbol)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_trade_status
            ON trades(status)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_recovery_report
            ON recovery(report_id)
            """,

            """
            CREATE INDEX IF NOT EXISTS idx_message_report
            ON message_log(report_id)
            """

        ]

        for query in indexes:

            self.execute(query)

    # =====================================================
    # Save Signal
    # =====================================================

    def save_signal(self, signal, report):

        self.execute(

            """
            INSERT OR REPLACE INTO signals(

                report_id,
                symbol,
                timeframe,
                signal_type,
                score,
                confidence,
                entry,
                stop_loss,
                tp1,
                tp2,
                tp3,
                created_at

            )

            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            """,

            (

                report.report_id,

                signal.symbol,

                signal.timeframe,

                signal.signal_type,

                signal.score,

                signal.confidence,

                signal.entry,

                signal.sl,

                signal.tp1,

                signal.tp2,

                signal.tp3,

                datetime.utcnow().isoformat()

            )

        )

    # =====================================================
    # Save Trade
    # =====================================================

    def save_trade(self, signal, report):

        self.execute(

            """
            INSERT OR REPLACE INTO trades(

                report_id,
                symbol,
                timeframe,
                signal_type,
                entry,
                current_price,
                stop_loss,
                tp1,
                tp2,
                tp3,
                status,
                opened_at,
                updated_at

            )

            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,

            (

                report.report_id,

                signal.symbol,

                signal.timeframe,

                signal.signal_type,

                signal.entry,

                signal.entry,

                signal.sl,

                signal.tp1,

                signal.tp2,

                signal.tp3,

                "OPEN",

                datetime.utcnow().isoformat(),

                datetime.utcnow().isoformat()

            )

        )

    # =====================================================
    # Get Open Trades
    # =====================================================

    def get_open_trades(self):

        return self.fetchall(

            """
            SELECT *
            FROM trades
            WHERE status!='CLOSED'
            """

        )

    # =====================================================
    # Get Active Signals
    # =====================================================

    def get_active_signals(self):

        return self.fetchall(

            """
            SELECT *
            FROM recovery
            WHERE state='ACTIVE'
            """

        )

    # =====================================================
    # Update Trade Status
    # =====================================================

    def update_trade_status(

        self,

        report_id,

        status,

        current_price,

        hit_time

    ):

        self.execute(

            """
            UPDATE trades

            SET

                status=?,

                current_price=?,

                updated_at=?

            WHERE report_id=?

            """,

            (

                status,

                current_price,

                hit_time.isoformat(),

                report_id

            )

        )
    # =====================================================
    # Close Trade
    # =====================================================

    def close_trade(

        self,

        report_id,

        exit_price,

        profit_percent

    ):

        self.execute(

            """
            UPDATE trades

            SET

                status='CLOSED',

                current_price=?,

                profit_percent=?,

                closed_at=?,

                updated_at=?

            WHERE report_id=?

            """,

            (

                exit_price,

                profit_percent,

                datetime.utcnow().isoformat(),

                datetime.utcnow().isoformat(),

                report_id

            )

        )

    # =====================================================
    # Recovery
    # =====================================================

    def update_recovery_state(

        self,

        report_id,

        state

    ):

        self.execute(

            """

            UPDATE recovery

            SET

                state=?,

                updated_at=?

            WHERE report_id=?

            """,

            (

                state,

                datetime.utcnow().isoformat(),

                report_id

            )

        )

    def remove_recovery(

        self,

        report_id

    ):

        self.execute(

            """

            DELETE FROM recovery

            WHERE report_id=?

            """,

            (

                report_id,

            )

        )

    # =====================================================
    # Message Log
    # =====================================================

    def message_sent(

        self,

        report_id

    ):

        row = self.fetchone(

            """

            SELECT sent

            FROM message_log

            WHERE report_id=?

            LIMIT 1

            """,

            (

                report_id,

            )

        )

        if row is None:

            return False

        return bool(row["sent"])

    def mark_message_sent(

        self,

        report_id

    ):

        self.execute(

            """

            INSERT OR REPLACE INTO message_log(

                report_id,

                message_type,

                sent,

                retry,

                sent_at

            )

            VALUES(?,?,?,?,?)

            """,

            (

                report_id,

                "SIGNAL",

                1,

                0,

                datetime.utcnow().isoformat()

            )

        )

    def save_message(

        self,

        report_id,

        message_type,

        retry

    ):

        self.execute(

            """

            INSERT INTO message_log(

                report_id,

                message_type,

                sent,

                retry,

                sent_at

            )

            VALUES(?,?,?,?,?)

            """,

            (

                report_id,

                message_type,

                0,

                retry,

                datetime.utcnow().isoformat()

            )

        )

    # =====================================================
    # Backup
    # =====================================================

    def backup(self):

        from shutil import copy2

        backup_folder = Path(BACKUP_FOLDER)

        backup_folder.mkdir(

            parents=True,

            exist_ok=True

        )

        backup_name = (

            f"backup_"

            f"{datetime.utcnow():%Y%m%d_%H%M%S}.db"

        )

        copy2(

            self.db_path,

            backup_folder / backup_name

        )

    # =====================================================
    # Optimize
    # =====================================================

    def optimize(self):

        self.ensure_connection()

        self.cursor.execute("VACUUM")

        self.cursor.execute("ANALYZE")

        self.connection.commit()

    # =====================================================
    # Save Signal V2
    # =====================================================

    def save_signal_v2(self, signal):

        self.execute(
            """
            INSERT INTO signals(

                report_id,
                symbol,
                timeframe,
                signal_type,
                score,
                confidence,
                entry,
                stop_loss,
                tp1,
                tp2,
                tp3,
                created_at

            )

            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            """,

            (

                signal["report_id"],

                signal["symbol"],

                signal["timeframe"],

                signal["signal"],

                signal["final_score"],

                signal["confidence"],

                signal["metadata"]["entry"],

                signal["metadata"]["stop_loss"],

                signal["metadata"]["tp1"],

                signal["metadata"]["tp2"],

                signal["metadata"]["tp3"],

                datetime.utcnow().isoformat(),

            )

        )

    # =====================================================
    # Health Check
    # =====================================================

    def health_check(self):

        return {

            "connected": self.connected,

            "database": str(self.db_path),

            "exists": self.db_path.exists()

        }

    # =====================================================
    # Close
    # =====================================================

    def close(self):

        if self.cursor:

            try:

                self.cursor.close()

            except Exception:

                pass

            self.cursor = None

        if self.connection:

            try:

                self.connection.close()

            except Exception:

                pass

            self.connection = None

        self.connected = False

    # =====================================================
    # Shutdown
    # =====================================================

    def shutdown(self):

        try:

            self.optimize()

        except Exception:

            pass

        try:

            self.backup()

        except Exception:

            pass

        self.close()