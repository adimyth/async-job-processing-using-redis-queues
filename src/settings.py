from functools import lru_cache

from dotenv import load_dotenv
from loguru import logger
from pydantic import AnyUrl, SecretStr
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # Redis settings
    REDIS_URL: AnyUrl

    # Database settings (postgres)
    DATABASE_URL: str


settings = Settings()


@lru_cache()
def get_settings() -> BaseSettings:
    logger.info("Loading config settings from the environment...")
    return Settings()
