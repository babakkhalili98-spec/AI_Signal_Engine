"""
====================================================
AI Signal Engine
Database Base
====================================================
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all database models.
    Every SQLAlchemy model must inherit from this class.
    """
    pass