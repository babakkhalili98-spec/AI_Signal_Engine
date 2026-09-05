"""
====================================================
AI Signal Engine
Database Session
====================================================
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import (
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_NAME,
    DATABASE_USER,
    DATABASE_PASSWORD,
)

DATABASE_URL = (
    f"postgresql+psycopg://"
    f"{DATABASE_USER}:{DATABASE_PASSWORD}"
    f"@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=30,
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """
    ایجاد Session جدید
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()