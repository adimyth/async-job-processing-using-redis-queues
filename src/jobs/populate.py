from loguru import logger
from sqlalchemy import text

from src.db.session import get_db
from src.jobs.base import BaseJob


class PopulateRecords(BaseJob):
    def __init__(self, sql_path: str, **kwargs):
        super().__init__(**kwargs)
        self.sql_path = sql_path

    def handle(self):
        logger.info(f"Populating table")

        # Read SQL file content
        with open(self.sql_path, "r") as sql_file:
            sql_commands = sql_file.read()

        with get_db() as session:
            session.execute(text(sql_commands))

        logger.info(f"Table populated successfully")
