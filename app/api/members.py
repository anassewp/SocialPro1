from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from ..config import MEMBERS_DIR, PREPARED_DIR
from ..schemas import (
    MemberExtractionRequest,
    MemberAddRequest,
    MemberPreparationRequest,
    MemberPreparationResponse,
    MessageSendRequest,
)
from ..services.files import file_service
from ..services.member_extraction import member_extraction_service
from ..services.member_loader import load_members_from_csv
from ..services.member_preparation import member_preparation_service
from ..services.member_addition import member_addition_service
from ..services.message_sending import message_sending_service

router = APIRouter(prefix="/members", tags=["members"])


@router.post("/extract")
def extract_members(payload: MemberExtractionRequest) -> dict:
    filename = payload.file_name or file_service.timestamped_filename("members", ext="csv")
    job_id, file_path = member_extraction_service.start_extraction(
        groups=payload.groups,
        file_name=filename,
        batch_size=payload.batch_size,
    )
    return {"job_id": job_id, "file_path": file_path}


@router.post("/prepare", response_model=MemberPreparationResponse)
def prepare_members(payload: MemberPreparationRequest) -> MemberPreparationResponse:
    source_path = Path(payload.source_file)
    if not source_path.is_file():
        source_path = MEMBERS_DIR / payload.source_file
    if not source_path.is_file():
        raise HTTPException(status_code=404, detail="Source file not found")
    result = member_preparation_service.prepare(
        source_file=source_path,
        blacklist=set(payload.blacklist or []),
        whitelist=set(payload.whitelist or []),
        chunk_size=payload.chunk_size,
    )
    files = [str(path) for path in result.get("files", [])]
    job_id = int(result.get("job_id", 0))
    return MemberPreparationResponse(job_id=job_id, files=files)


@router.post("/add")
def add_members(payload: MemberAddRequest) -> dict:
    if not payload.accounts:
        raise HTTPException(status_code=400, detail="At least one account is required")
    if not payload.member_files:
        raise HTTPException(status_code=400, detail="Member files list cannot be empty")
    all_members = []
    for file_name in payload.member_files:
        path = Path(file_name)
        if not path.is_file():
            path = PREPARED_DIR / file_name
        if not path.is_file():
            raise HTTPException(status_code=404, detail=f"Member file not found: {file_name}")
        all_members.extend(list(load_members_from_csv(path)))
    job_id = member_addition_service.add_members(
        members=all_members,
        group_id=payload.group_id,
        account_labels=payload.accounts,
        adds_per_hour=payload.adds_per_hour,
        max_retry_per_user=payload.max_retry,
    )
    return {"job_id": job_id, "total_members": len(all_members)}


@router.post("/message")
def send_messages(payload: MessageSendRequest) -> dict:
    if not payload.accounts:
        raise HTTPException(status_code=400, detail="At least one account is required")
    if not payload.member_files:
        raise HTTPException(status_code=400, detail="Member files list cannot be empty")
    all_members = []
    for file_name in payload.member_files:
        path = Path(file_name)
        if not path.is_file():
            path = PREPARED_DIR / file_name
        if not path.is_file():
            raise HTTPException(status_code=404, detail=f"Member file not found: {file_name}")
        all_members.extend(list(load_members_from_csv(path)))
    job_id = message_sending_service.send_messages(
        members=all_members,
        accounts=payload.accounts,
        template=payload.template,
        messages_per_minute=payload.messages_per_minute,
    )
    return {"job_id": job_id, "recipients": len(all_members)}
