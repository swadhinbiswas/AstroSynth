from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

# The API serves predictions without Postgres. Keep the connect attempt short
# so a dead database costs milliseconds, not the whole request budget.
_connect_args: dict = {"connect_timeout": 2} if settings.DATABASE_URL.startswith("postgresql") else {}

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    future=True,
    connect_args=_connect_args,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
