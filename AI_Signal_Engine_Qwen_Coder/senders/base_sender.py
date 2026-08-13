"""
=========================================================
AI Signal Engine
Base Sender
Version : 1.0
=========================================================
"""

from abc import ABC, abstractmethod


class BaseSender(ABC):
    """
    کلاس پایه تمام ارسال کننده‌ها
    """

    @abstractmethod
    def send_message(self, text: str) -> bool:
        pass

    @abstractmethod
    def send_photo(
        self,
        image_path: str,
        caption: str = ""
    ) -> bool:
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        pass