from sqlalchemy.orm import Session
from src.jobs.base import BaseJob


class TruncateTable(BaseJob):
    def __init__(
        self, schema: str = "public", table_name: str = None, session: Session = None
    ):
        super().__init__()
        self.schema = schema
        self.table = table_name
        self.session = session

    def perform(self):
        self.before_start()
        try:
            self.session.execute(f"TRUNCATE TABLE {self.schema}.{self.table} CASCADE")
            self.session.commit()
            self.after_success(
                f"Table {self.schema}.{self.table} truncated successfully"
            )
        except Exception as e:
            self.on_failure(type(e), e, e.__traceback__)
            raise
