"""
=========================================================
AI Signal Engine
Logger
Version : 1.0
=========================================================
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class Logger:

    def __init__(
        self,
        log_folder: str = "logs",
        log_file: str = "ai_signal_engine.log",
        level: int = logging.INFO,
    ):

        Path(log_folder).mkdir(
            parents=True,
            exist_ok=True
        )

        self.logger = logging.getLogger("AI_Signal_Engine")

        self.logger.setLevel(level)

        if self.logger.handlers:
            return

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        file_handler = RotatingFileHandler(
            filename=Path(log_folder) / log_file,
            maxBytes=10 * 1024 * 1024,   # 10 MB
            backupCount=5,
            encoding="utf-8"
        )

        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()

        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

        self.logger.addHandler(console_handler)

    # --------------------------------------------------

    def get_logger(self):

        return self.logger