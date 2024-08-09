from typing import Optional

from pydantic import BaseModel

from src.schemas.common import JobStatus


class JobStatusResponse(BaseModel):
    id: str
    status: JobStatus
    result: Optional[str] = None
    error: Optional[str] = None
    traceback: Optional[str] = None
    retry_count: int
    next_retry_time: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
