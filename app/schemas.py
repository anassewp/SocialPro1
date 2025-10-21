from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field

from .models import AccountStatus, JobStatus, JobType


class AccountCreate(BaseModel):
    label: str
    phone: str
    api_id: str
    api_hash: str
    session_path: Optional[str] = None
    limits: dict | None = None


class AccountRead(BaseModel):
    id: int
    label: str
    phone: str
    status: AccountStatus
    created_at: datetime
    last_activity: Optional[datetime]

    class Config:
        orm_mode = True


class GroupSearchRequest(BaseModel):
    keywords: List[str] = Field(..., min_items=1)
    limit_per_keyword: int = Field(5, ge=1, le=100)
    file_name: Optional[str] = None
    min_members: int = Field(0, ge=0)


class GroupSearchResponse(BaseModel):
    job_id: int
    file_path: Optional[str]


class MemberExtractionRequest(BaseModel):
    groups: List[str]
    file_name: Optional[str] = None
    batch_size: int = Field(200, ge=1, le=1000)


class MemberPreparationRequest(BaseModel):
    source_file: str
    blacklist: List[str] | None = None
    whitelist: List[str] | None = None
    chunk_size: int = Field(1000, ge=10, le=10000)


class MemberPreparationResponse(BaseModel):
    job_id: int
    files: List[str]


class MessageSendRequest(BaseModel):
    member_files: List[str]
    accounts: List[str]
    template: str
    messages_per_minute: int = Field(15, ge=1, le=120)


class MemberAddRequest(BaseModel):
    group_id: str
    member_files: List[str]
    accounts: List[str]
    adds_per_hour: int = Field(20, ge=1, le=200)
    max_retry: int = Field(2, ge=0, le=5)


class JobRead(BaseModel):
    id: int
    type: JobType
    status: JobStatus
    progress: float
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    last_error: Optional[str]

    class Config:
        orm_mode = True
