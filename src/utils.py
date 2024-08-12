import importlib
import json
from datetime import datetime, timedelta

from loguru import logger
from redis import Redis
from rq import Queue
from rq.job import Job as RQJob
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import select

from src.db.session import get_db
from src.jobs.base import BaseJob
from src.models.model import Jobs
from src.schemas.common import JobStatus
from src.settings import settings


def recover_jobs():
    try:
        redis_conn = Redis.from_url(settings.REDIS_URL)
        with get_db() as session:
            # Fetch jobs that are queued or started within the last 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            stmt = select(Jobs).where(
                Jobs.status.in_([JobStatus.queued, JobStatus.started]),
                Jobs.created_at > cutoff_time,
            )
            jobs_to_recover = session.execute(stmt).scalars().all()

            recovered_count = 0
            for job in jobs_to_recover:
                try:
                    # Parse the payload to get the queue name
                    payload = json.loads(job.payload)
                    queue_name = payload.get("queue", settings.JOB_DEFAULT_QUEUE)
                    queue = Queue(queue_name, connection=redis_conn)

                    # Check if the job exists in Redis
                    rq_job = RQJob.fetch(job.id, connection=redis_conn)

                    if rq_job is None:
                        # Dynamically import the job class
                        module_name, class_name = job.job_class.rsplit(".", 1)
                        module = importlib.import_module(module_name)
                        job_class = getattr(module, class_name)

                        # Requeue the job using the original job ID.
                        _ = queue.enqueue(job_class.perform, **payload, job_id=job.id)

                        # Set status=queued & updated_at for the existing job in the database
                        job.status = JobStatus.queued
                        job.updated_at = datetime.utcnow()

                        logger.info(f"Recovered job {job.id} by requeueing")
                        recovered_count += 1
                    else:
                        # Job exists in Redis, no action needed
                        logger.info(
                            f"Job {job.id} already exists in Redis. No action taken"
                        )

                except json.JSONDecodeError:
                    logger.error(f"Failed to parse payload for job {job.id}")
                except Exception as e:
                    logger.error(f"Failed to recover job {job.id}: {str(e)}")

            session.commit()
            logger.info(
                f"Recovered {recovered_count} out of {len(jobs_to_recover)} jobs"
            )
    except SQLAlchemyError as e:
        logger.error(f"Database error during job recovery: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during job recovery: {str(e)}")
