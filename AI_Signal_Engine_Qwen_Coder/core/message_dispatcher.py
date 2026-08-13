"""
=========================================================
AI SIGNAL ENGINE
Message Dispatcher
Version : 4.0
=========================================================

وظایف

✓ خواندن MessageQueue
✓ ارسال Telegram
✓ ارسال Bale
✓ Retry
✓ Flush Queue
✓ جلوگیری از ارسال تکراری
✓ Statistics
✓ Health Check

=========================================================
"""

from __future__ import annotations

import logging
import threading
import traceback
import time

from typing import Optional

from config.settings import *

from core.database_manager import DatabaseManager

from messengers.message_queue import MessageQueue
from messengers.telegram_sender import TelegramSender
from messengers.bale_sender import BaleSender


# =========================================================
# Dispatcher
# =========================================================

class MessageDispatcher:

    def __init__(self):

        self.logger = logging.getLogger(
            "MessageDispatcher"
        )

        # ------------------------------
        # Database
        # ------------------------------

        self.database = DatabaseManager()

        # ------------------------------
        # Queue
        # ------------------------------

        self.queue = MessageQueue(

            logger=self.logger,

            database=self.database

        )

        # ------------------------------
        # Messengers
        # ------------------------------

        self.telegram = TelegramSender()
        
        self.bale = BaleSender()

        # ------------------------------
        # Worker
        # ------------------------------

        self.running = False

        self.worker: Optional[threading.Thread] = None

        # ------------------------------
        # Statistics
        # ------------------------------

        self.total_sent = 0

        self.total_failed = 0

        self.total_retry = 0

        self.total_duplicate = 0

        self.logger.info(

            "MessageDispatcher Initialized"

        )
    # =====================================================
    # Start
    # =====================================================

    def start(self):
        """
        شروع Dispatcher
        """

        if self.running:
            return

        self.running = True

        self.worker = threading.Thread(

            target=self.run,

            daemon=True,

            name="MessageDispatcher"

        )

        self.worker.start()

        self.logger.info(

            "Message Dispatcher Started"

        )

    # =====================================================
    # Stop
    # =====================================================

    def stop(self):
        """
        توقف Dispatcher
        """

        self.running = False

        self.logger.info(

            "Stopping Dispatcher..."

        )

    # =====================================================
    # Main Loop
    # =====================================================

    def run(self):
        """
        حلقه اصلی Dispatcher
        """

        self.logger.info(

            "Dispatcher Loop Started"

        )

        while self.running:

            try:

                self.run_once()

            except Exception:

                self.logger.exception(

                    traceback.format_exc()

                )

            time.sleep(

                SCAN_DELAY_SECONDS

            )

        self.logger.info(

            "Dispatcher Loop Finished"

        )

    # =====================================================
    # Run Once
    # =====================================================

    def run_once(self):
        """
        پردازش فقط یک پیام
        """

        message = self.get_next_message()

        if message is None:

            return

        self.process_message(

            message

        )

    # =====================================================
    # Get Next Message
    # =====================================================

    def get_next_message(self):
        """
        دریافت پیام بعدی از صف
        """

        try:

            if self.queue.is_empty():

                return None

            return self.queue.get_next()

        except Exception:

            self.logger.exception(

                traceback.format_exc()

            )

            return None
    # =====================================================
    # Process Message
    # =====================================================

    def process_message(
        self,
        message
    ):
        """
        پردازش یک پیام
        """

        report_id = message.get("report_id")

        try:

            if self.database.message_sent(report_id):

                self.total_duplicate += 1

                self.logger.info(
                    f"Duplicate Message : {report_id}"
                )

                return

        except Exception:

            pass

        success = self.send_message(message)

        if success:

            self.total_sent += 1

            try:

                self.database.mark_message_sent(
                    report_id
                )

            except Exception:

                self.logger.exception(
                    traceback.format_exc()
                )

        else:

            self.retry(message)

    # =====================================================
    # Telegram
    # =====================================================

    def send_telegram(
        self,
        message
    ):

        message_type = message.get("message_type")

        report_id = message.get("report_id")

        payload = message.get("payload")

        try:

            if message_type == "text":

                return self.telegram.send_message(
                    report_id,
                    payload
                )

            elif message_type == "chart":

                return self.telegram.send_chart(
                    report_id,
                    payload
                )

            elif message_type == "pdf":

                return self.telegram.send_pdf(
                    report_id,
                    payload
                )

            elif message_type == "document":

                return self.telegram.send_document(
                    report_id,
                    payload
                )

            elif message_type == "signal":

                return self.telegram.send_signal(
                    report_id,
                    payload
                )

            else:

                self.logger.warning(
                    f"Unknown Telegram Message Type : {message_type}"
                )

                return False

        except Exception:

            self.logger.exception(
                traceback.format_exc()
            )

            return False

    # =====================================================
    # Bale
    # =====================================================

    def send_bale(
        self,
        message
    ):

        message_type = message.get("message_type")

        report_id = message.get("report_id")

        payload = message.get("payload")

        try:

            if message_type == "text":

                return self.bale.send_message(
                    report_id,
                    payload
                )

            elif message_type == "chart":

                return self.bale.send_chart(
                    report_id,
                    payload
                )

            elif message_type == "pdf":

                return self.bale.send_pdf(
                    report_id,
                    payload
                )

            elif message_type == "document":

                return self.bale.send_document(
                    report_id,
                    payload
                )

            elif message_type == "signal":

                return self.bale.send_signal(
                    report_id,
                    payload
                )

            else:

                self.logger.warning(
                    f"Unknown Bale Message Type : {message_type}"
                )

                return False

        except Exception:

            self.logger.exception(
                traceback.format_exc()
            )

            return False

    # =====================================================
    # Send Message
    # =====================================================

    def send_message(
        self,
        message
    ):

        telegram_ok = False
        bale_ok = False
 
        if TELEGRAM_ENABLED:
            telegram_ok = self.send_telegram(message)

        if BALE_ENABLED:
            bale_ok = self.send_bale(message)

        # اگر هیچ پیام‌رسانی فعال نبود
        if not TELEGRAM_ENABLED and not BALE_ENABLED:
            return False

        # اگر حداقل یکی موفق بود
        return telegram_ok or bale_ok

    # =====================================================
    # Retry
    # =====================================================

    def retry(
        self,
        message
    ):
        """
        ارسال مجدد پیام
        """

        retry = message.get("retry", 0)

        if retry >= API_RETRY:

            self.total_failed += 1

            self.logger.warning(

                f"Retry Failed : {message.get('report_id')}"

            )

            return
 
        message["retry"] = retry + 1

        self.total_retry += 1

        self.queue.add(

            messenger=message.get("messenger", "telegram"),

            report_id=message.get("report_id"),

            message_type=message.get("message_type"),

            payload=message.get("payload"),

            retry=message.get("retry", 0)

        )

        self.logger.info(
 
            f"Retry {message['retry']} : {message.get('report_id')}"

        )

    # =====================================================
    # Flush Queue
    # =====================================================

    def flush_queue(self):
        """
        ارسال تمام پیام‌های باقی‌مانده
        """

        self.logger.info(

            "Flushing Queue..."

        )

        while not self.queue.is_empty():

            try:

                self.run_once()

            except Exception:

                self.logger.exception(

                    traceback.format_exc()

                )

                break

    # =====================================================
    # Queue Size
    # =====================================================

    def queue_size(self):

        try:

            return self.queue.size()

        except Exception:

            return 0
            
            retry=message.get("retry")

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self):

        return {

            "sent": self.total_sent,

            "failed": self.total_failed,

            "retry": self.total_retry,

            "duplicate": self.total_duplicate,

            "queue": self.queue_size()

        }

    # =====================================================
    # Send Signal
    # =====================================================

    def send_signal(self, signal):

        message = {

            "messenger": "telegram",

            "report_id": f"{signal['symbol']}_{signal['timeframe']}",

            "message_type": "signal",

            "payload": signal,

        }

        return self.send_message(message)

    # =====================================================
    # Health Check
    # =====================================================

    def health_check(self):

        return {

            "running": self.running,

            "database": self.database is not None,

            "queue": self.queue is not None,

            "telegram": self.telegram is not None,

            "bale": self.bale is not None,

            "statistics": self.statistics()

        }

    # =====================================================
    # Print Statistics
    # =====================================================

    def print_statistics(self):

        stats = self.statistics()

        self.logger.info("")

        self.logger.info("=" * 60)

        self.logger.info("MESSAGE DISPATCHER")

        self.logger.info("=" * 60)

        self.logger.info(

            f"Sent       : {stats['sent']}"

        )

        self.logger.info(

            f"Retry      : {stats['retry']}"

        )

        self.logger.info(

            f"Duplicate  : {stats['duplicate']}"

        )

        self.logger.info(

            f"Failed     : {stats['failed']}"

        )

        self.logger.info(

            f"Queue      : {stats['queue']}"

        )

        self.logger.info("=" * 60)
    # =====================================================
    # Shutdown
    # =====================================================

    def shutdown(self):
        """
        خاموش کردن Dispatcher
        """

        self.logger.info("")

        self.logger.info("=" * 60)

        self.logger.info(

            "MESSAGE DISPATCHER SHUTDOWN"

        )

        self.logger.info("=" * 60)

        try:

            # توقف Worker
            self.stop()
            
            self.running=False

            # ارسال پیام‌های باقی‌مانده
            self.flush_queue()

            # منتظر پایان Thread
            if self.worker is not None:

                self.worker.join(timeout=5)

            # بستن Session های Messenger
            try:

                self.telegram.shutdown()

            except Exception:

                self.logger.exception(
                    traceback.format_exc()
                )

            try:

                self.bale.shutdown()

            except Exception:

                self.logger.exception(
                    traceback.format_exc()
                )

            # بستن Database
            try:

                if hasattr(self.database, "close"):

                    self.database.close()

            except Exception:

                self.logger.exception(
                    traceback.format_exc()
                )

            # چاپ آمار
            self.print_statistics()

            self.logger.info(

                "Message Dispatcher Closed"

            )

        except Exception:

            self.logger.exception(

                traceback.format_exc()

            )

    # =====================================================
    # Context Manager
    # =====================================================

    def __enter__(self):

        self.start()

        return self

    # =====================================================
    # Context Exit
    # =====================================================

    def __exit__(

        self,

        exc_type,

        exc_val,

        exc_tb

    ):

        self.shutdown()

    # =====================================================
    # Destructor
    # =====================================================

    def __del__(self):

        try:
            if self.running:
                self.shutdown()

        except Exception:
            pass