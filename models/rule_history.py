"""
====================================================
AI Signal Engine
Rule History Model
====================================================
"""

from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Float,
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


class RuleHistory(Base):

    __tablename__ = "rule_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    rule_id: Mapped[int] = mapped_column(
        ForeignKey(
            "rules.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    old_score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    new_score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    old_weight: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    new_weight: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    # ADMIN
    # RESEARCH
    # IMPORT
    # SYSTEM

    approved_by: Mapped[str] = mapped_column(
        String(100),
        default=""
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    rule = relationship("Rule")

    __table_args__ = (
        Index(
            "idx_rule_history",
            "rule_id",
            "created_at"
        ),
    )

    def __repr__(self):

        return (
            f"<RuleHistory("
            f"{self.rule_id}, "
            f"{self.old_score} -> {self.new_score}"
            f")>"
        )