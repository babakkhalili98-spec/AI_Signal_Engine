"""
=========================================================
AI Signal Engine
Database Manager
Version : 1.0
=========================================================
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class Database:

    def __init__(self, db_path="database/ai_signal.db"):

        Path("database").mkdir(
            parents=True,
            exist_ok=True
        )

        self.connection = sqlite3.connect(
            db_path,
            check_same_thread=False
        )

        self.connection.row_factory = sqlite3.Row

        self.cursor = self.connection.cursor()

    # --------------------------------------------------

    def initialize(self):

        self.create_tables()

    # --------------------------------------------------

    def execute(self, sql, params=()):

        self.cursor.execute(sql, params)

        self.connection.commit()

    # --------------------------------------------------

    def query(self, sql, params=()):

        self.cursor.execute(sql, params)

        return self.cursor.fetchall()

    # --------------------------------------------------

    def insert(self, table, data: dict):

        columns = ",".join(data.keys())

        placeholders = ",".join(["?"] * len(data))

        sql = f"""

        INSERT INTO {table}

        ({columns})

        VALUES

        ({placeholders})

        """

        self.execute(

            sql,

            tuple(data.values())

        )

    # --------------------------------------------------

    def close(self):

        self.connection.close()

    # --------------------------------------------------

    def create_tables(self):

        # ==============================
        # Signals
        # ==============================

        self.execute("""

        CREATE TABLE IF NOT EXISTS signals(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symbol TEXT,

            timeframe TEXT,

            direction TEXT,

            score REAL,

            confidence REAL,

            entry REAL,

            sl REAL,

            tp1 REAL,

            tp2 REAL,

            tp3 REAL,

            created_at TEXT

        )

        """)

        # ==============================
        # Trades
        # ==============================

        self.execute("""

        CREATE TABLE IF NOT EXISTS trades(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            signal_id INTEGER,

            status TEXT,

            entry_price REAL,

            exit_price REAL,

            pnl REAL,

            result TEXT,

            opened_at TEXT,

            closed_at TEXT

        )

        """)

        # ==============================
        # Shadow Mode
        # ==============================

        self.execute("""

        CREATE TABLE IF NOT EXISTS shadow_trades(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symbol TEXT,

            timeframe TEXT,

            direction TEXT,

            score REAL,

            result TEXT,

            created_at TEXT

        )

        """)

        # ==============================
        # Market Memory
        # ==============================

        self.execute("""

        CREATE TABLE IF NOT EXISTS market_memory(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            pattern TEXT,

            symbol TEXT,

            timeframe TEXT,

            win INTEGER,

            loss INTEGER,

            created_at TEXT

        )

        """)

        # ==============================
        # Research
        # ==============================

        self.execute("""

        CREATE TABLE IF NOT EXISTS research(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT,

            description TEXT,

            status TEXT,

            created_at TEXT

        )

        """)

        # ==============================
        # News Memory
        # ==============================

        self.execute("""

        CREATE TABLE IF NOT EXISTS news_memory(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            news_type TEXT,

            symbol TEXT,

            impact REAL,

            created_at TEXT

        )

        """)

        # ==============================
        # Logs
        # ==============================

        self.execute("""

        CREATE TABLE IF NOT EXISTS logs(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            level TEXT,

            message TEXT,

            created_at TEXT

        )

        """)