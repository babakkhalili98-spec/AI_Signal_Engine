"""
====================================================
AI Signal Engine
Candle Model
====================================================
"""

from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Index
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from database.base import Base


class Candle(Base):
    """
    ذخیره کندل‌های بازار
    """

    __tablename__ = "candles"

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
        nullable=False,
        index=True
    )

    open_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True
    )

    close_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    open: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    high: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    low: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    close: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    volume: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    trades: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    coin = relationship("Coin")

    __table_args__ = (
        Index(
            "idx_coin_tf_time",
            "coin_id",
            "timeframe",
            "open_time"
        ),
    )

    def __repr__(self):
        return (
            f"<Candle("
            f"{self.coin_id}, "
            f"{self.timeframe}, "
            f"{self.open_time}"
            f")>"
        )