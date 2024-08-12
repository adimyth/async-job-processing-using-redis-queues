import sqlalchemy as sa

from src.db.base_class import Base
from src.schemas.common import JobStatus


class Jobs(Base):
    id = sa.Column(sa.String, primary_key=True)
    job_class = sa.Column(sa.String)
    payload = sa.Column(sa.JSON)
    status = sa.Column(sa.Enum(JobStatus), default=JobStatus.queued, nullable=False)
    result = sa.Column(sa.String)
    error = sa.Column(sa.Text)
    traceback = sa.Column(sa.Text)
    retry_count = sa.Column(sa.Integer, default=0)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime, onupdate=sa.func.now())
