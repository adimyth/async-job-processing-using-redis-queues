from loguru import logger
from sqlalchemy import text

from src.db.session import get_db
from src.jobs.base import BaseJob


class SlowQuery(BaseJob):
    def __init__(self, duration: int, **kwargs):
        super().__init__(**kwargs)
        self.duration = duration

    def handle(self):
        logger.info(f"Executing sleep query for {self.duration} seconds")

        with get_db() as session:
            session.execute(text(f"SELECT pg_sleep({self.duration})"))

        return f"Slow query completed after {self.duration} seconds"
