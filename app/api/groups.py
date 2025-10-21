from __future__ import annotations

from fastapi import APIRouter

from ..schemas import GroupSearchRequest, GroupSearchResponse
from ..services.group_search import group_search_service
from ..services.files import file_service

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("/search", response_model=GroupSearchResponse)
def search_groups(payload: GroupSearchRequest) -> GroupSearchResponse:
    filename = payload.file_name or file_service.timestamped_filename("group_search", ext="txt")
    job_id, file_path = group_search_service.start_search(
        keywords=payload.keywords,
        limit_per_keyword=payload.limit_per_keyword,
        file_name=filename,
        min_members=payload.min_members,
    )
    return GroupSearchResponse(job_id=job_id, file_path=file_path)
