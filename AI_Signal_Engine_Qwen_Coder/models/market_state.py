"""
====================================================
AI Signal Engine
Market State Model
====================================================
"""

from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Float,
    Boolean,
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


class MarketState(Base):
    """
    وضعیت بازار برای هر ارز و تایم‌فریم
    """

    __tablename__ = "market_states"

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

    market_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    # BULL / BEAR / RANGE / VOLATILE / TRANSITION

    trend: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    # UP / DOWN / SIDEWAYS

    trend_strength: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    volatility: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    fake_breakout_risk: Mapped[float] = mapped_column(
        Float,
        default=0.0
    )

    is_tradable: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    coin = relationship("Coin")

    __table_args__ = (
        Index(
            "idx_market_state",
            "coin_id",
            "timeframe",
            "analyzed_at"
        ),
    )

    def __repr__(self):
        return (
            f"<MarketState("
            f"{self.coin_id}, "
            f"{self.timeframe}, "
            f"{self.market_type}"
            f")>"
        )