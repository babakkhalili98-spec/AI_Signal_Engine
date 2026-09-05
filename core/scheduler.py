"""
=========================================================
AI Signal Engine
Scheduler
Version : 1.0
=========================================================
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, List


@dataclass
class ScheduledJob:
    name: str
    interval_seconds: int
    callback: Callable
    enabled: bool = True
    last_run: datetime | None = None
    next_run: float = 0.0


class Scheduler:
    """
    زمان‌بندی اجرای Job ها

    این کلاس هیچ تحلیل بازار انجام نمی‌دهد.
    فقط Job ها را در زمان مشخص اجرا می‌کند.
    """

    def __init__(self):

        self.logger = logging.getLogger("Scheduler")

        self.jobs: List[ScheduledJob] = []

        self.running = False

        self.thread = None

    # -------------------------------------------------

    def add_job(

        self,

        name: str,

        interval_seconds: int,

        callback: Callable

    ):

        now = time.time()

        self.jobs.append(

            ScheduledJob(

                name=name,

                interval_seconds=interval_seconds,

                callback=callback,

                next_run=now

            )

        )

        self.logger.info(

            f"Job Registered : {name}"
        )

    # -------------------------------------------------

    def every_seconds(

        self,

        seconds: int,

        callback: Callable,

        name: str = "Job"

    ):

        self.add_job(

            name,

            seconds,

            callback

        )

    # -------------------------------------------------

    def every_minutes(

        self,

        minutes: int,

        callback: Callable,

        name: str = "Job"

    ):

        self.add_job(

            name,

            minutes * 60,

            callback

        )

    # -------------------------------------------------

    def every_hours(

        self,

        hours: int,

        callback: Callable,

        name: str = "Job"

    ):

        self.add_job(

            name,

            hours * 3600,

            callback

        )

    # -------------------------------------------------

    def run_pending(self):

        now = time.time()

        for job in self.jobs:

            if not job.enabled:
                continue

            if now >= job.next_run:

                try:

                    self.logger.info(

                        f"Running : {job.name}"
                    )

                    job.callback()

                    job.last_run = datetime.utcnow()

                except Exception as e:

                    self.logger.exception(e)

                finally:

                    job.next_run = (

                        now +

                        job.interval_seconds

                    )

    # -------------------------------------------------

    def _loop(self):

        while self.running:

            self.run_pending()

            time.sleep(1)

    # -------------------------------------------------

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(

            target=self._loop,

            daemon=True

        )

        self.thread.start()

        self.logger.info(

            "Scheduler Started."
        )

    # -------------------------------------------------

    def stop(self):

        self.running = False

        self.logger.info(

            "Scheduler Stopped."
        )