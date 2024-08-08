from typing import Generator
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlmodel import Session
from src.settings import settings

# Encode the password
encoded_password = quote_plus(settings.POSTGRES_DB_PASSWORD.get_secret_value())


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=0,
)


def get_db(autocommit=False) -> Generator[Session, None, None]:
    session = Session(engine, expire_on_commit=False, autocommit=autocommit)
    try:
        yield session
    finally:
        session.close()


def get_session(autocommit=False) -> Session:
    return next(get_db(autocommit))
