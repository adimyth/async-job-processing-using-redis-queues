from redis import Redis
from rq import Queue, get_current_job
from src.db.session import Session
from src.models.model import JobStatus
from sqlalchemy.orm import Session


class BaseJob:
    def __init__(self, session: Session):
        self.job = get_current_job()
        self.redis = Redis()
        self.session = session

    def _update_status(self, status):
        if self.job:
            job_status = self.session.query(JobStatus).get(self.job.id)
            if not job_status:
                job_status = JobStatus(id=self.job.id)
            job_status.status = status
            job_status.retry_count += 1
            self.session.add(job_status)
            self.session.commit()

    def before_start(self):
        self._update_status("started")

    def after_success(self, result=None):
        job_status = self.session.query(JobStatus).get(self.job.id)
        job_status.status = "completed"
        job_status.result = str(result)
        self.session.commit()

    def on_failure(self, exc_type, exc_value, traceback):
        job_status = self.session.query(JobStatus).get(self.job.id)
        job_status.status = "failed"
        job_status.error = str(exc_value)
        self.session.commit()

    def perform(self):
        raise NotImplementedError("Subclasses must implement this method")

    @classmethod
    def dispatch(cls, *args, **kwargs):
        queue_name = kwargs.pop("queue", "default")
        redis_conn = Redis()
        queue = Queue(queue_name, connection=redis_conn)
        job = queue.enqueue(
            cls.perform,
            args=args,
            kwargs=kwargs,
            # Set timeout to 5 minutes
            timeout=300,
            # Retry 3 times
            retry=3,
            # Exponential backoff: 1 minute, 5 minutes, 15 minutes
            retry_intervals=[60, 300, 900],
        )

        session = Session()
        job_status = JobStatus(id=job.id, status="queued")
        session.add(job_status)
        session.commit()
        session.close()

        return job

    @classmethod
    def get_job_status(cls, job_id):
        session = Session()
        job_status: JobStatus = session.query(JobStatus).get(job_id)
        status_dict = {
            "id": job_status.id,
            "status": job_status.status,
            "created_at": job_status.created_at,
            "updated_at": job_status.updated_at,
            "result": job_status.result,
            "error": job_status.error,
            "retry_count": job_status.retry_count,
        }
        session.close()
        return status_dict
