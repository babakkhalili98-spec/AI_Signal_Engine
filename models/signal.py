"""
====================================================
AI Signal Engine
Signal Model
====================================================
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Enum as SqlEnum,
    Index
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from database.base import Base


class SignalType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class SignalStatus(str, Enum):
    WAITING = "WAITING"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELED = "CANCELED"


class SignalResult(str, Enum):
    UNKNOWN = "UNKNOWN"
    WIN = "WIN"
    LOSS = "LOSS"
    BREAKEVEN = "BREAKEVEN"


class Signal(Base):

    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    coin_id: Mapped[int] = mapped_column(
        ForeignKey("coins.id"),
        nullable=False,
        index=True
    )

    timeframe: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    signal_type: Mapped[SignalType] = mapped_column(
        SqlEnum(SignalType),
        nullable=False
    )

    status: Mapped[SignalStatus] = mapped_column(
        SqlEnum(SignalStatus),
        default=SignalStatus.WAITING
    )

    result: Mapped[SignalResult] = mapped_column(
        SqlEnum(SignalResult),
        default=SignalResult.UNKNOWN
    )

    total_score: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    entry_price: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    stop_loss: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    take_profit_1: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    take_profit_2: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    take_profit_3: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    risk_reward: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    market_type: Mapped[str] = mapped_column(
        String(20)
    )

    trend: Mapped[str] = mapped_column(
        String(20)
    )

    description: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    sent_to_bale: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    sent_to_telegram: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    opened_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    coin = relationship("Coin")

    __table_args__ = (
        Index(
            "idx_signal",
            "coin_id",
            "timeframe",
            "created_at"
        ),
    )

    def __repr__(self):
        return (
            f"<Signal("
            f"{self.id}, "
            f"{self.signal_type}, "
            f"{self.total_score}"
            f")>"
        )