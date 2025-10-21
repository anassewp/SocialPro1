from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select

from ..database import session_scope
from ..models import Job, JobStatus, JobType


class JobService:
    def create_job(self, job_type: JobType, payload: dict[str, Any], owner: str | None = None) -> Job:
        with session_scope() as session:
            job = Job(type=job_type, payload=payload, owner=owner)
            session.add(job)
            session.flush()
            session.refresh(job)
            return job

    def update_status(
        self,
        job_id: int,
        *,
        status: JobStatus | None = None,
        progress: float | None = None,
        last_error: str | None = None,
        finished: bool = False,
    ) -> Job | None:
        with session_scope() as session:
            job = session.get(Job, job_id)
            if not job:
                return None
            if status:
                job.status = status
                if status == JobStatus.running:
                    job.started_at = job.started_at or datetime.utcnow()
            if progress is not None:
                job.progress = progress
            if last_error:
                job.last_error = last_error
            if finished:
                job.finished_at = datetime.utcnow()
            session.add(job)
            session.flush()
            session.refresh(job)
            return job

    def list_jobs(self) -> list[Job]:
        with session_scope() as session:
            return list(session.scalars(select(Job).order_by(Job.created_at.desc())))

    def get_job(self, job_id: int) -> Job | None:
        with session_scope() as session:
            return session.get(Job, job_id)


job_service = JobService()

__all__ = ["JobService", "job_service"]
