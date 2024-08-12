import importlib
import json
from typing import List

import click
from redis import Redis
from redis.exceptions import RedisError
from rq import Queue
from rq.registry import FailedJobRegistry
from sqlalchemy.orm import Session
from sqlalchemy.sql import delete, select

from src.db.session import get_db
from src.jobs.base import BaseJob
from src.models.model import Jobs
from src.schemas.common import JobStatus
from src.settings import settings


@click.group()
def cli():
    """CLI for managing jobs."""
    pass


@cli.command()
@click.option("--job-id", help="ID of the specific job to retry")
@click.option("--all", is_flag=True, help="Retry all failed jobs")
def retry_job(job_id, all):
    """
    Retry failed jobs.

    You can either retry a specific job by providing the job ID or retry all failed jobs.

    If you retry a specific job, a new job will be enqueued with a new ID. The old job will disappear from the failed jobs list.
    """
    redis_conn = Redis.from_url(settings.REDIS_URL)

    with get_db() as session:
        try:
            if all:
                retry_all_failed_jobs(session=session, redis_conn=redis_conn)
            elif job_id:
                retry_single_job(job_id, session=session, redis_conn=redis_conn)
            else:
                click.echo(
                    "Please provide either a job ID or use the --all flag. Use --help for more information."
                )
        except RedisError as e:
            click.echo(f"Failed to connect to Redis: {e}")
        except Exception as e:
            click.echo(f"An error occurred: {e}")
        finally:
            redis_conn.close()


def retry_single_job(job_id: str, session: Session, redis_conn: str):
    stmt = select(Jobs).where(Jobs.id == job_id, Jobs.status == JobStatus.failed)
    job = session.execute(stmt).scalar_one_or_none()

    if not job:
        click.echo(f"No failed job found with ID {job_id}")
        return

    try:
        payload = json.loads(job.payload)
        queue_name = payload.get("queue", settings.JOB_DEFAULT_QUEUE)
        queue = Queue(queue_name, connection=redis_conn)

        # Dynamically import the job class
        module_name, class_name = job.job_class.rsplit(".", 1)
        module = importlib.import_module(module_name)
        job_class = getattr(module, class_name)

        # Dispatch a new job with the same payload & log the retry attempt
        new_job = job_class.dispatch(**json.loads(job.payload))
        click.echo(f"Job {job_id} has been requeued with new ID: {new_job.id}")

        # Delete the failed job
        stmt = delete(Jobs).where(Jobs.id == job_id)
        session.execute(stmt)

        # Remove from FailedJobRegistry
        registry = FailedJobRegistry(queue=queue)
        registry.remove(job_id)
    except json.JSONDecodeError:
        click.echo(f"Failed to parse payload for job {job_id}")
    except Exception as e:
        click.echo(f"Failed to retry job {job_id}: {e}")


def retry_all_failed_jobs(session: Session, redis_conn: str):
    stmt = select(Jobs).where(Jobs.status == JobStatus.failed)
    failed_jobs: List[Jobs] = session.execute(stmt).scalars().all()

    retried_count = 0
    for job in failed_jobs:
        try:
            retry_single_job(job_id=job.id, session=session, redis_conn=redis_conn)
            retried_count += 1
        except Exception as e:
            click.echo(f"Failed to retry job {job.id}: {str(e)}")

    click.echo(f"Retried {retried_count} out of {len(failed_jobs)} failed jobs")


@cli.command()
@click.option("--limit", default=10, help="Number of jobs to display")
def list_failed_jobs(limit):
    """
    List failed jobs. By default, it will display the last 10 failed jobs.
    """

    with get_db() as session:
        stmt = select(Jobs).where(Jobs.status == JobStatus.failed).limit(limit)
        failed_jobs = session.execute(stmt).scalars().all()
        if not failed_jobs:
            click.echo("No failed jobs found")
        else:
            for job in failed_jobs:
                click.echo(f"Job ID: {job.id}, Error: {job.error[:300]}...")


if __name__ == "__main__":
    cli()
