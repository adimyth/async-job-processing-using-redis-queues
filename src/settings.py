from functools import lru_cache
from typing import List

from dotenv import load_dotenv
from loguru import logger
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # Redis settings
    REDIS_URL: str

    # Database settings (postgres)
    DATABASE_URL: str

    # Job settings
    JOB_DEFAULT_QUEUE: str = "default"
    JOB_TIMEOUT: int = 300  # 5 minutes
    JOB_MAX_RETRIES: int = 3
    JOB_RETRY_INTERVAL: List[int] = [60, 300, 900]  # 1 minute, 5 minutes, 15 minutes


settings = Settings()


@lru_cache()
def get_settings() -> BaseSettings:
    logger.info("Loading config settings from the environment...")
    return Settings()
