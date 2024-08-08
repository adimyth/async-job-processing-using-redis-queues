from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from src.jobs.truncate import TruncateTable
from sqlalchemy.orm import Session
from src.db.session import get_db, engine
from src.db.base_class import Base


app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)


@app.post("/truncate-table/")
async def truncate_table(session: Session = Depends(get_db)):
    job = TruncateTable.dispatch(
        schema="public",
        table_name="temp_table",
        session=session,
        queue="low",
    )

    return {"job_id": job.id, "status": "enqueued"}


@app.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    return TruncateTable.get_job_status(job_id)
