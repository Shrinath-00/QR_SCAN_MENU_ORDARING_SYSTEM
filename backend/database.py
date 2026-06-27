from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings
import logging

logger = logging.getLogger("hotel_management")

DATABASE_URL = settings.DATABASE_URL
is_sqlite = DATABASE_URL.startswith("sqlite")

try:
    if is_sqlite:
        engine = create_engine(
            DATABASE_URL, connect_args={"check_same_thread": False}
        )
    else:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=10,
            max_overflow=20
        )
    # Verify connection
    with engine.connect() as conn:
        pass
except Exception as e:
    logger.warning(
        f"Failed to connect to primary database ({DATABASE_URL}): {e}. "
        "Falling back to SQLite."
    )
    DATABASE_URL = "sqlite:///./hotel_management_fallback.db"
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
