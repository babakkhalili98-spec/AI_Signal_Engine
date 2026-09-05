"""
====================================================
AI Signal Engine
Coin Model
====================================================
"""

from sqlalchemy import (
    Boolean,
    Integer,
    String,
    DateTime
)

from sqlalchemy.sql import func
from database.base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Coin(Base):
    """
    اطلاعات هر دارایی قابل معامله
    """

    __tablename__ = "coins"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    symbol: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    market: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    base_asset: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    quote_asset: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self):

        return (
            f"<Coin("
            f"{self.symbol}"
            f")>"
        )