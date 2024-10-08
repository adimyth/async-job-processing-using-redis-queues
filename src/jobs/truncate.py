from loguru import logger
from sqlalchemy import text

from src.db.session import get_db
from src.jobs.base import BaseJob


class TruncateTable(BaseJob):
    def __init__(self, table: str, **kwargs):
        super().__init__(**kwargs)
        self.table = table

    def handle(self):
        logger.info(f"Truncating table {self.table}")

        with get_db() as session:
            session.execute(
                text(f"TRUNCATE TABLE {self.table} RESTART IDENTITY CASCADE;")
            )

        logger.info(f"Table {self.table} truncated successfully")
