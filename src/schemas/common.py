from enum import Enum


class JobStatus(Enum):
    queued = "queued"
    started = "started"
    completed = "completed"
    failed = "failed"
