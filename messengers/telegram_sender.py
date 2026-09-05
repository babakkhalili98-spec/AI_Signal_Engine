"""
=========================================================
AI Signal Engine
Telegram Sender
Version : 3.0.0
=========================================================

وظایف

• ارسال پیام متنی
• ارسال عکس
• ارسال PDF
• ارسال فایل
• Retry
• Timeout
• Health Check
• Statistics
• Shutdown

=========================================================
"""

from __future__ import annotations

import logging
import traceback
from pathlib import Path
from typing import Optional

import requests

from config.settings import *


class TelegramSender:

    """
    ارسال پیام به تلگرام
    """

    def __init__(self):

        self.logger = logging.getLogger(
            "TelegramSender"
        )

        self.base_url = (
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
        )

        self.chat_id = TELEGRAM_CHAT_ID

        self.timeout = 20

        self.total_sent = 0
        self.total_failed = 0

        self.session = requests.Session()

        self.logger.info(
            "Telegram Sender Initialized"
        )

    # -------------------------------------------------
    # Request
    # -------------------------------------------------

    def request(

        self,

        method,

        data=None,

        files=None

    ):

        """
        ارسال درخواست به Telegram API
        """

        url = f"{self.base_url}/{method}"

        try:

            response = self.session.post(

                url,

                data=data,

                files=files,

                timeout=self.timeout

            )

            if response.status_code != 200:

                self.logger.error(

                    response.text

                )

                return False

            result = response.json()

            if not result.get("ok", False):

                self.logger.error(

                    result

                )

                return False

            return True

        except Exception:

            self.logger.exception(

                traceback.format_exc()

            )

            return False
    # -------------------------------------------------
    # Send Text
    # -------------------------------------------------

    def send_message(

        self,

        report_id,

        text

    ):

        """
        ارسال پیام متنی
        """

        data = {

            "chat_id": self.chat_id,

            "text": text,

            "parse_mode": "HTML",

            "disable_web_page_preview": True

        }

        ok = self.request(

            "sendMessage",

            data=data

        )

        if ok:

            self.total_sent += 1

            self.logger.info(

                f"Telegram TEXT Sent : {report_id}"

            )

        else:

            self.total_failed += 1

            self.logger.warning(

                f"Telegram TEXT Failed : {report_id}"

            )

        return ok

    # -------------------------------------------------
    # Send Chart
    # -------------------------------------------------

    def send_chart(

        self,

        report_id,

        image_path

    ):

        """
        ارسال تصویر چارت
        """

        path = Path(image_path)

        if not path.exists():

            self.logger.error(

                f"Chart Not Found : {image_path}"

            )

            return False

        with open(path, "rb") as fp:

            files = {

                "photo": fp

            }

            data = {

                "chat_id": self.chat_id

            }

            ok = self.request(

                "sendPhoto",

                data=data,

                files=files

            )

        if ok:

            self.total_sent += 1

            self.logger.info(

                f"Telegram CHART Sent : {report_id}"

            )

        else:

            self.total_failed += 1

            self.logger.warning(

                f"Telegram CHART Failed : {report_id}"

            )

        return ok

    # -------------------------------------------------
    # Send PDF
    # -------------------------------------------------

    def send_pdf(

        self,

        report_id,

        pdf_path

    ):

        """
        ارسال فایل PDF
        """

        return self.send_document(

            report_id,

            pdf_path

        )

    # -------------------------------------------------
    # Send Document
    # -------------------------------------------------

    def send_document(

        self,

        report_id,

        file_path

    ):

        """
        ارسال فایل
        """

        path = Path(file_path)

        if not path.exists():

            self.logger.error(

                f"Document Not Found : {file_path}"

            )

            return False

        with open(path, "rb") as fp:

            files = {

                "document": fp

            }

            data = {

                "chat_id": self.chat_id

            }

            ok = self.request(

                "sendDocument",

                data=data,

                files=files

            )

        if ok:

            self.total_sent += 1

            self.logger.info(

                f"Telegram DOCUMENT Sent : {report_id}"

            )

        else:

            self.total_failed += 1

            self.logger.warning(

                f"Telegram DOCUMENT Failed : {report_id}"

            )

        return ok
    # -------------------------------------------------
    # Send Trading Signal
    # -------------------------------------------------

    def send_signal(

        self,

        report_id,

        signal

    ):

        """
        ارسال سیگنال معامله
        """

        text = f"""
📊 <b>AI Signal Engine</b>

🪙 Symbol : {signal['symbol']}
📈 Signal : {signal['signal']}
⏰ TF : {signal['timeframe']}

💰 Entry : {signal['entry']}

🛑 Stop : {signal['stop_loss']}

🎯 TP1 : {signal['tp1']}
🎯 TP2 : {signal['tp2']}
🎯 TP3 : {signal['tp3']}

⭐ Score : {signal['score']}
🎯 Confidence : {signal['confidence']}%

📅 {signal['created_at']}
"""

        return self.send_message(

            report_id,

            text

        )

    # -------------------------------------------------
    # Error Message
    # -------------------------------------------------

    def send_error(

        self,

        text

    ):

        """
        ارسال خطا
        """

        return self.send_message(

            "SYSTEM",

            f"❌ {text}"

        )

    # -------------------------------------------------
    # Retry
    # -------------------------------------------------

    def retry_send(

        self,

        callback,

        retry=3

    ):

        """
        تلاش مجدد
        """

        for i in range(retry):

            try:

                if callback():

                    return True

            except Exception:

                self.logger.exception(

                    traceback.format_exc()

                )

        return False

    # -------------------------------------------------
    # Ping
    # -------------------------------------------------

    def ping(self):

        """
        تست اتصال تلگرام
        """

        return self.request(

            "getMe"

        )

    # -------------------------------------------------
    # Test Connection
    # -------------------------------------------------

    def test_connection(self):

        """
        تست اتصال
        """

        ok = self.ping()

        if ok:

            self.logger.info(

                "Telegram Connected"

            )

        else:

            self.logger.error(

                "Telegram Connection Failed"

            )

        return ok
    # -------------------------------------------------
    # Statistics
    # -------------------------------------------------

    def statistics(self):
        """
        آمار Telegram Sender
        """

        return {

            "sent":

                self.total_sent,

            "failed":

                self.total_failed,

            "timeout":

                self.timeout,

            "chat_id":

                self.chat_id

        }

    # -------------------------------------------------
    # Health Check
    # -------------------------------------------------

    def health_check(self):
        """
        بررسی وضعیت Sender
        """

        return {

            "status":

                "READY",

            "connected":

                self.ping(),

            "statistics":

                self.statistics()

        }

    # -------------------------------------------------
    # Reset Statistics
    # -------------------------------------------------

    def reset_statistics(self):
        """
        ریست آمار
        """

        self.total_sent = 0

        self.total_failed = 0

        self.logger.info(

            "Telegram Statistics Reset"

        )

    # -------------------------------------------------
    # Close Session
    # -------------------------------------------------

    def close(self):
        """
        بستن Session
        """

        try:

            if self.session:

                self.session.close()

        except Exception:

            self.logger.exception(

                traceback.format_exc()

            )

    # -------------------------------------------------
    # Cleanup
    # -------------------------------------------------

    def cleanup(self):
        """
        پاکسازی
        """

        self.close()

        self.logger.info(

            "Telegram Cleanup Done"

        )
    # -------------------------------------------------
    # Shutdown
    # -------------------------------------------------

    def shutdown(self):
        """
        خاموش کردن Telegram Sender
        """

        self.logger.info("")

        self.logger.info("=" * 60)

        self.logger.info(

            "TELEGRAM SENDER SHUTDOWN"

        )

        self.logger.info("=" * 60)

        try:

            self.cleanup()

            stats = self.statistics()

            self.logger.info(

                f"Total Sent   : {stats['sent']}"

            )

            self.logger.info(

                f"Total Failed : {stats['failed']}"

            )

            self.logger.info(

                "Telegram Sender Closed"

            )

        except Exception:

            self.logger.exception(

                traceback.format_exc()

            )

    # -------------------------------------------------
    # Destructor
    # -------------------------------------------------

    def __del__(self):
        """
        پاکسازی هنگام حذف شیء
        """

        try:

            self.close()

        except Exception:

            pass