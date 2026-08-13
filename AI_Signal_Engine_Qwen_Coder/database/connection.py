"""
=====================================================
Argus AI
Database Connection
Version : 1.0
=====================================================
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

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

# ساخت Engine
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    echo=False,
)

# ساخت Session
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

# کلاس پایه تمام مدل‌های دیتابیس
Base = declarative_base()


def get_db():
    """
    ایجاد Session برای استفاده در برنامه
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


def create_database():
    """
    ساخت تمام جدول‌ها
    """

    Base.metadata.create_all(bind=engine)