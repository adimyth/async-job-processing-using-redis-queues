from loguru import logger
from sqlalchemy import text

from src.db.session import get_db
from src.jobs.base import BaseJob


class DataAggregation(BaseJob):
    def __init__(self, table: str, group_by: str, **kwargs):
        super().__init__(**kwargs)
        self.table = table
        self.group_by = group_by
        self.kwargs = kwargs

    def handle(self):
        logger.info(f"Aggregating {self.table} grouped by {self.group_by}")
        with get_db() as session:
            result = session.execute(
                text(
                    f"""
                SELECT {self.group_by}, SUM(salary) as total_salary
                FROM {self.table}
                GROUP BY {self.group_by}
                ORDER BY {self.kwargs.get("sort_by")} {self.kwargs.get("sort_order")}
                """
                )
            )
            data = result.fetchall()
        return f"Aggregation complete. {len(data)} groups found."
