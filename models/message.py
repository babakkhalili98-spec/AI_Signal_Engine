"""
مدل‌های مربوط به پیام و ارسال آن.
این ماژول ساختار پیام‌ها و نتایج ارسال را تعریف می‌کند.
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass


class MessageType(Enum):
    """انواع مختلف پیام‌ها"""
    SIGNAL = "signal"
    UPDATE = "update"
    NEWS_WARNING = "news_warning"
    MARKET_REPORT = "market_report"
    LONDON_OPENING_REPORT = "london_opening_report"
    PERFORMANCE_REPORT = "performance_report"
    R_AND_D_REPORT = "r_and_d_report"
    ALERT = "alert"


class MessagePriority(Enum):
    """اولویت‌های پیام"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Message:
    """
    نماینده یک پیام برای ارسال به کانال‌های مختلف.
    
    Attributes:
        message_id: شناسه یکتای پیام
        message_type: نوع پیام
        priority: اولویت پیام
        content: محتوای متنی پیام
        recipient: شناسه گیرنده (کانال، کاربر، etc.)
        original_message_id: شناسه پیام اصلی (برای آپدیت/ریپلای)
        metadata: متادیتای اضافی
        created_at: زمان ایجاد پیام
    """
    message_id: str = ""
    message_type: MessageType = MessageType.ALERT
    priority: MessagePriority = MessagePriority.NORMAL
    content: str = ""
    recipient: str = ""
    original_message_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if isinstance(self.message_type, str):
            self.message_type = MessageType(self.message_type)
        if isinstance(self.priority, str):
            self.priority = MessagePriority(self.priority)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "content": self.content,
            "recipient": self.recipient,
            "original_message_id": self.original_message_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class MessageResult:
    """
    نتیجه ارسال یک پیام.
    
    Attributes:
        success: آیا ارسال موفق بود
        message_id: شناسه پیام ارسالی (در صورت موفقیت)
        error: پیام خطا (در صورت شکست)
        timestamp: زمان ارسال
        channel: کانال ارسال‌کننده
    """
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = None
    channel: str = ""
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message_id": self.message_id,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
            "channel": self.channel
        }
