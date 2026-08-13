"""
=========================================================
AI Signal Engine
Bale Sender
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

import requests

from config.settings import *


class BaleSender:
    """
    ارسال پیام به پیام‌رسان بله
    """

    def __init__(self):

        self.logger = logging.getLogger(
            "BaleSender"
        )

        self.base_url = (
            f"https://tapi.bale.ai/bot{BALE_BOT_TOKEN}"
        )

        self.chat_id = BALE_CHAT_ID

        self.timeout = 20

        self.total_sent = 0
        self.total_failed = 0

        self.session = requests.Session()

        self.logger.info(
            "Bale Sender Initialized"
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
        ارسال درخواست به API بله
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

            if not result.get("ok", True):

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

            "text": text

        }

        ok = self.request(

            "sendMessage",

            data=data

        )

        if ok:

            self.total_sent += 1

            self.logger.info(

                f"Bale TEXT Sent : {report_id}"

            )

        else:

            self.total_failed += 1

            self.logger.warning(

                f"Bale TEXT Failed : {report_id}"

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
        ارسال تصویر
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

                f"Bale CHART Sent : {report_id}"

            )

        else:

            self.total_failed += 1

            self.logger.warning(

                f"Bale CHART Failed : {report_id}"

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
        ارسال PDF
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

                f"Bale DOCUMENT Sent : {report_id}"

            )

        else:

            self.total_failed += 1

            self.logger.warning(

                f"Bale DOCUMENT Failed : {report_id}"

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

        meta = signal["metadata"]

        text = f"""
    📊 AI Signal Engine

    🪙 Symbol : {signal['symbol']}
    📈 Signal : {signal['signal']}
    ⏰ TF : {signal['timeframe']}

    💰 Entry : {meta['entry']}

    🛑 Stop : {meta['stop_loss']}

    🎯 TP1 : {meta['tp1']}
    🎯 TP2 : {meta['tp2']}
    🎯 TP3 : {meta['tp3']}

    ⭐ Score : {signal['final_score']}

    🔗 Confluence : {signal.get('confluence',0)}%

    📅 {signal['created_at']}
    """

        return self.send_message(

            report_id,

            text

        )

    # -------------------------------------------------
    # Send Error
    # -------------------------------------------------

    def send_error(

        self,

        text

    ):

        """
        ارسال پیام خطا
        """

        return self.send_message(

            "SYSTEM",

            f"❌ {text}"

        )

    # -------------------------------------------------
    # Retry Send
    # -------------------------------------------------

    def retry_send(

        self,

        callback,

        retry=3

    ):

        """
        تلاش مجدد
        """

        for attempt in range(retry):

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
        تست ارتباط با بله
        """

        return self.request(

            "getMe"

        )

    # -------------------------------------------------
    # Test Connection
    # -------------------------------------------------

    def test_connection(self):

        """
        بررسی اتصال
        """

        ok = self.ping()

        if ok:

            self.logger.info(

                "Bale Connected"

            )

        else:

            self.logger.error(

                "Bale Connection Failed"

            )

        return ok
    # -------------------------------------------------
    # Statistics
    # -------------------------------------------------

    def statistics(self):
        """
        آمار Bale Sender
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

            "Bale Statistics Reset"

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

            "Bale Cleanup Done"

        )
    # -------------------------------------------------
    # Shutdown
    # -------------------------------------------------

    def shutdown(self):
        """
        خاموش کردن Bale Sender
        """

        self.logger.info("")

        self.logger.info("=" * 60)

        self.logger.info(

            "BALE SENDER SHUTDOWN"

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

                "Bale Sender Closed"

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