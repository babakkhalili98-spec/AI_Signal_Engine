"""
=========================================================
AI Signal Engine
Bale Sender
Version : 1.0
=========================================================
"""

from __future__ import annotations

import logging
from pathlib import Path

import requests

from senders.base_sender import BaseSender


class BaleSender(BaseSender):

    def __init__(

        self,

        token: str,

        chat_id: str

    ):

        self.logger = logging.getLogger("BaleSender")

        self.token = token

        self.chat_id = chat_id

        self.base_url = f"https://tapi.bale.ai/bot{token}"

    # ------------------------------------------------

    def send_message(self, text: str) -> bool:

        try:

            url = self.base_url + "/sendMessage"

            response = requests.post(

                url,

                json={

                    "chat_id": self.chat_id,

                    "text": text

                },

                timeout=20

            )

            response.raise_for_status()

            return True

        except Exception as e:

            self.logger.exception(e)

            return False

    # ------------------------------------------------

    def send_photo(

        self,

        image_path,

        caption=""

    ):

        try:

            image = Path(image_path)

            if not image.exists():

                return False

            url = self.base_url + "/sendPhoto"

            with image.open("rb") as photo:

                response = requests.post(

                    url,

                    data={

                        "chat_id": self.chat_id,

                        "caption": caption

                    },

                    files={

                        "photo": photo

                    },

                    timeout=60

                )

            response.raise_for_status()

            return True

        except Exception as e:

            self.logger.exception(e)

            return False

    # ------------------------------------------------

    def test_connection(self):

        return self.send_message(
            "✅ AI Signal Engine Connected"
        )