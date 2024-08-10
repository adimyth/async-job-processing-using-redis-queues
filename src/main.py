import asyncio

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.db.base_class import Base
from src.db.session import engine
from src.jobs.aggregation import DataAggregation
from src.jobs.drop import DropTable
from src.jobs.exception import FailedJob
from src.jobs.fibonacci import Fibonacci
from src.jobs.populate import PopulateRecords
from src.jobs.slow_query import SlowQuery
from src.jobs.truncate import TruncateTable
from src.models.model import Jobs
from src.schemas.response import JobStatusResponse
from src.utils import recover_jobs

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    # Run create_all in a separate thread to not block the event loop
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, Base.metadata.create_all, engine)

    # Requeue jobs that were queued or started within the last 24 hours
    recover_jobs()


@app.post("/create-jobs/")
async def create_jobs():
    # high priority jobs
    PopulateRecords.dispatch(sql_path="users.sql", queue="high")

    # medium priority jobs
    SlowQuery.dispatch(duration=10, queue="medium")
    DataAggregation.dispatch(
        table="auth.users",
        group_by="department",
        sort_by="total_salary",
        sort_order="desc",
        queue="medium",
    )
    TruncateTable.dispatch(table="auth.users", queue="medium")
    DropTable.dispatch(table="auth.users", queue="low")

    # low priority jobs
    Fibonacci.dispatch(n=10, queue="low")
    FailedJob.dispatch(queue="low")


@app.get("/job-status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    response = TruncateTable.get_job_status(job_id)
    if not response:
        return JSONResponse(status_code=400, content={"msg": "Invalid job ID"})
    return JSONResponse(status_code=200, content=response)
