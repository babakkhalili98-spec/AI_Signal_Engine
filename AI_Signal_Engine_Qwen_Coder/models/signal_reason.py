"""
====================================================
AI Signal Engine
Signal Reason Model
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
    Text,
    Index
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from database.base import Base


class SignalReason(Base):

    __tablename__ = "signal_reasons"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    signal_id: Mapped[int] = mapped_column(
        ForeignKey(
            "signals.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    module: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    rule_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    score: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    positive: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    signal = relationship(
        "Signal",
        backref="reasons"
    )

    __table_args__ = (
        Index(
            "idx_reason_signal",
            "signal_id"
        ),
        Index(
            "idx_reason_rule",
            "rule_id"
        ),
    )

    def __repr__(self):

        return (
            f"<SignalReason("
            f"{self.rule_id}, "
            f"{self.score}"
            f")>"
        )