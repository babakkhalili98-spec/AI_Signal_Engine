"""
=========================================================
AI Signal Engine
Telegram Sender
Version : 2.0
=========================================================
"""

import requests
from time import sleep


class TelegramSender:

    def __init__(

        self,

        config,

        logger,

        database

    ):

        self.config = config

        self.logger = logger

        self.database = database

        self.token = config.TELEGRAM_BOT_TOKEN

        self.chat_id = config.TELEGRAM_CHAT_ID

        self.base_url = (

            f"https://api.telegram.org/bot{self.token}"

        )

    # =====================================================
    # SEND TEXT
    # =====================================================

    def send_message(

        self,

        report_id,

        message

    ):

        endpoint = (

            self.base_url +

            "/sendMessage"

        )

        payload = {

            "chat_id": self.chat_id,

            "text": message,

            "parse_mode": "HTML",

            "disable_web_page_preview": True

        }

        return self._request(

            endpoint,

            payload,

            report_id,

            "TEXT"

        )
    # =====================================================
    # SEND CHART
    # =====================================================

    def send_chart(

        self,

        report_id,

        chart_path,

        caption=""

    ):

        endpoint = (

            self.base_url +

            "/sendPhoto"

        )

        with open(

            chart_path,

            "rb"

        ) as photo:

            files = {

                "photo": photo

            }

            data = {

                "chat_id": self.chat_id,

                "caption": caption,

                "parse_mode": "HTML"

            }

            return self._request_file(

                endpoint,

                data,

                files,

                report_id,

                "CHART"

            )
    # =====================================================
    # SEND PDF
    # =====================================================

    def send_pdf(

        self,

        report_id,

        pdf_path,

        caption=""

    ):

        endpoint = (

            self.base_url +

            "/sendDocument"

        )

        with open(

            pdf_path,

            "rb"

        ) as pdf:

            files = {

                "document": pdf

            }

            data = {

                "chat_id": self.chat_id,

                "caption": caption,

                "parse_mode": "HTML"

            }

            return self._request_file(

                endpoint,

                data,

                files,

                report_id,

                "PDF"

            )
    # =====================================================
    # REQUEST
    # =====================================================

    def _request(

        self,

        endpoint,

        payload,

        report_id,

        message_type

    ):

        retry = self.config.MAX_SEND_RETRY

        for attempt in range(

            1,

            retry + 1

        ):

            try:

                response = requests.post(

                    endpoint,

                    json=payload,

                    timeout=self.config.REQUEST_TIMEOUT

                )

                if response.status_code == 200:

                    self.database.save_message_status(

                        report_id=report_id,

                        messenger="TELEGRAM",

                        message_type=message_type,

                        status="SENT",

                        retry=attempt

                    )

                    return True

            except Exception as error:

                self.logger.error(str(error))

            sleep(

                self.config.RETRY_DELAY

            )

        self.database.save_message_status(

            report_id=report_id,

            messenger="TELEGRAM",

            message_type=message_type,

            status="FAILED",

            retry=retry

        )

        return False
    # =====================================================
    # REQUEST FILE
    # =====================================================

    def _request_file(

        self,

        endpoint,

        data,

        files,

        report_id,

        message_type

    ):

        retry = self.config.MAX_SEND_RETRY

        for attempt in range(

            1,

            retry + 1

        ):

            try:

                response = requests.post(

                    endpoint,

                    data=data,

                    files=files,

                    timeout=self.config.REQUEST_TIMEOUT

                )

                if response.status_code == 200:

                    self.database.save_message_status(

                        report_id=report_id,

                        messenger="TELEGRAM",

                        message_type=message_type,

                        status="SENT",

                        retry=attempt

                    )

                    return True

            except Exception as error:

                self.logger.error(str(error))

            sleep(

                self.config.RETRY_DELAY

            )

        self.database.save_message_status(

            report_id=report_id,

            messenger="TELEGRAM",

            message_type=message_type,

            status="FAILED",

            retry=retry

        )

        return False