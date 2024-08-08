import sqlalchemy as sa
from src.db.base_class import Base


class JobStatus(Base):
    __tablename__ = "job_statuses"

    id = sa.Column(sa.String, primary_key=True)
    status = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime, onupdate=sa.func.now())
    result = sa.Column(sa.String)
    error = sa.Column(sa.String)
    retry_count = sa.Column(sa.Integer, default=0)