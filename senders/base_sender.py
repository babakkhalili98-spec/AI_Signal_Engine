"""
اینترفیس‌های پایه برای ارسال‌کننده‌های پیام.
این ماژول لایه انتزاع را برای ارسال پیام به کانال‌های مختلف تعریف می‌کند.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from models.message import Message, MessageResult


class IMessageSender(ABC):
    """
    اینترفیس پایه برای تمام ارسال‌کننده‌های پیام.
    
    هر Sender (Telegram, Bale, Email, SMS, etc.)
    باید این اینترفیس را پیاده‌سازی کند.
    """
    
    @abstractmethod
    def send(self, message: Message) -> MessageResult:
        """
        ارسال یک پیام جدید.
        
        Args:
            message: شیء پیام
            
        Returns:
            MessageResult: نتیجه ارسال
        """
        pass
    
    @abstractmethod
    def edit(self, message_id: str, new_content: str) -> MessageResult:
        """
        ویرایش یک پیام ارسالی قبلی.
        
        Args:
            message_id: شناسه پیام اصلی
            new_content: محتوای جدید
            
        Returns:
            MessageResult: نتیجه ویرایش
        """
        pass
    
    @abstractmethod
    def reply(self, message_id: str, content: str) -> MessageResult:
        """
        پاسخ به یک پیام ارسالی قبلی.
        
        Args:
            message_id: شناسه پیام اصلی
            content: محتوای پاسخ
            
        Returns:
            MessageResult: نتیجه پاسخ
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        بررسی در دسترس بودن Sender.
        
        Returns:
            bool: True اگر Sender در دسترس باشد
        """
        pass
    
    @abstractmethod
    def get_channel_name(self) -> str:
        """
        دریافت نام کانال ارسال‌کننده.
        
        Returns:
            str: نام کانال
        """
        pass


class SenderManager:
    """
    مدیریت ارسال‌کننده‌های مختلف پیام.
    
    این کلاس امکان ثبت چندین Sender و ارسال پیام به کانال‌های مختلف را فراهم می‌کند.
    """
    
    _senders: dict[str, IMessageSender] = {}
    
    @classmethod
    def register(cls, name: str, sender: IMessageSender):
        """
        ثبت یک Sender جدید.
        
        Args:
            name: نام منحصر به فرد Sender
            sender: شیء Sender
        """
        cls._senders[name] = sender
    
    @classmethod
    def get(cls, name: str) -> Optional[IMessageSender]:
        """
        دریافت یک Sender بر اساس نام.
        
        Args:
            name: نام Sender
            
        Returns:
            Optional[IMessageSender]: شیء Sender یا None
        """
        return cls._senders.get(name)
    
    @classmethod
    def send_to_all(cls, message: Message) -> List[MessageResult]:
        """
        ارسال پیام به تمام کانال‌های ثبت‌شده.
        
        Args:
            message: شیء پیام
            
        Returns:
            List[MessageResult]: لیست نتایج ارسال
        """
        results = []
        for sender in cls._senders.values():
            if sender.is_available():
                result = sender.send(message)
                results.append(result)
        return results
    
    @classmethod
    def list_senders(cls) -> List[str]:
        """
       返回列表所有已注册的发送者名称。
        
        Returns:
            List[str]: لیست نام Senderهای ثبت‌شده
        """
        return list(cls._senders.keys())
