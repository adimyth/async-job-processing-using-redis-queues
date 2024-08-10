import json
import traceback

from loguru import logger
from redis import Redis
from rq import Queue, Retry, get_current_job
from sqlalchemy import func
from sqlalchemy.sql import select, update

from src.db.session import get_db
from src.models.model import Jobs
from src.schemas.common import JobStatus
from src.schemas.response import JobStatusResponse
from src.settings import settings


class BaseJob:
    # Use a class-level Redis connection
    redis = Redis.from_url(settings.REDIS_URL)

    def __init__(self, **kwargs):
        self.job = get_current_job()
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def update_job(cls, job_id, increment_retry_count=False, **kwargs):
        with get_db() as session:
            if increment_retry_count:
                # Use SQL expression to increment retry_count
                kwargs["retry_count"] = func.coalesce(Jobs.retry_count, 0) + 1
            stmt = update(Jobs).where(Jobs.id == job_id).values(**kwargs)
            session.execute(stmt)

    @classmethod
    def perform(cls, *args, **kwargs):
        # Fetch current job
        job = get_current_job()

        if job:
            logger.info(f"Executing job {job.id}, attempt {job.meta.get('attempt', 1)}")
            # Job Started: update the status
            cls.update_job(job.id, status=JobStatus.started)
        else:
            logger.warning("No current job context found")

        instance = cls(*args, **kwargs)
        try:
            # Run the job
            result = instance.handle()
            # Job completed: update status
            cls.update_job(job.id, status=JobStatus.completed, result=str(result))
            return result
        except Exception as e:
            tb = traceback.format_exc()
            # Job failed: update status, error & traceback
            # TODO: Set next_retry_count
            cls.update_job(
                job.id,
                increment_retry_count=True,
                status=JobStatus.failed,
                error=str(e),
                traceback=tb,
            )
            raise

    def handle(self):
        raise NotImplementedError("Subclasses must implement this method")

    @classmethod
    def dispatch(cls, **kwargs):
        # Get the queue name from the kwargs or use the default
        queue_name = kwargs.get("queue", settings.JOB_DEFAULT_QUEUE)
        queue = Queue(queue_name, connection=cls.redis)

        # set job timeout & retry with exponential backoff
        retry = Retry(
            max=settings.JOB_MAX_RETRIES, interval=settings.JOB_RETRY_INTERVAL
        )

        # add job to queue
        job = queue.enqueue(
            cls.perform,
            kwargs=kwargs,
            timeout=settings.JOB_TIMEOUT,
            retry=retry,
        )

        # Job Queued: store status & payload
        with get_db() as session:
            new_job = Jobs(
                id=job.id, status=JobStatus.queued, payload=json.dumps(kwargs)
            )
            session.add(new_job)
        return job

    @classmethod
    def get_job_status(cls, job_id):
        with get_db() as session:
            stmt = select(Jobs).where(Jobs.id == job_id)
            job = session.execute(stmt).scalar_one_or_none()

            if not job:
                return None

            return JobStatusResponse(**job)
