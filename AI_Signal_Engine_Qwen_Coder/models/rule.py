"""
====================================================
AI Signal Engine
Rule Model
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
    Text,
    Enum as SqlEnum,
    Index
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from database.base import Base


class RuleStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    TEST = "TEST"


class Rule(Base):

    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    rule_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    module: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        default=""
    )

    score: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    weight: Mapped[float] = mapped_column(
        Float,
        default=1.0
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    success_rate: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    sample_size: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    market_type: Mapped[str] = mapped_column(
        String(30),
        default="ALL"
    )

    timeframe: Mapped[str] = mapped_column(
        String(20),
        default="ALL"
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    need_admin_review: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    status: Mapped[RuleStatus] = mapped_column(
        SqlEnum(RuleStatus),
        default=RuleStatus.ACTIVE
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    __table_args__ = (
        Index("idx_rule_module", "module"),
        Index("idx_rule_category", "category"),
        Index("idx_rule_enabled", "enabled"),
    )

    def __repr__(self):
        return (
            f"<Rule("
            f"{self.rule_id}, "
            f"{self.score}"
            f")>"
        )