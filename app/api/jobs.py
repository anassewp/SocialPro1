from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..schemas import JobRead
from ..services.jobs import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobRead])
def list_jobs() -> list[JobRead]:
    jobs = job_service.list_jobs()
    return [JobRead.from_orm(job) for job in jobs]


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: int) -> JobRead:
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobRead.from_orm(job)
