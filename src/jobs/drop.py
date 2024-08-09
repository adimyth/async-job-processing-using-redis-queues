from loguru import logger
from sqlalchemy import text

from src.db.session import get_db
from src.jobs.base import BaseJob


class DropTable(BaseJob):
    def __init__(self, table: str, **kwargs):
        super().__init__(**kwargs)
        self.table = table

    def handle(self):
        logger.info(f"Dropping table {self.table}")

        with get_db() as session:
            session.execute(text(f"DROP TABLE IF EXISTS {self.table};"))

        logger.info(f"Table {self.table} dropped successfully")
