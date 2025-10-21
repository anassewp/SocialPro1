from __future__ import annotations

import enum
from datetime import datetime
from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class AccountStatus(str, enum.Enum):
    online = "ONLINE"
    offline = "OFFLINE"
    banned = "BANNED"
    cooldown = "COOLDOWN"


class GroupStatus(str, enum.Enum):
    new = "NEW"
    extracted = "EXTRACTED"
    blacklisted = "BLACKLISTED"


class JobStatus(str, enum.Enum):
    pending = "PENDING"
    running = "RUNNING"
    success = "SUCCESS"
    failed = "FAILED"
    paused = "PAUSED"


class JobType(str, enum.Enum):
    group_search = "GROUP_SEARCH"
    member_extraction = "MEMBER_EXTRACTION"
    member_preparation = "MEMBER_PREPARATION"
    member_addition = "MEMBER_ADDITION"
    message_sending = "MESSAGE_SENDING"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String(100), nullable=False)
    phone = Column(String(32), nullable=False, unique=True)
    api_id_encrypted = Column(String(512), nullable=False)
    api_hash_encrypted = Column(String(512), nullable=False)
    session_path = Column(String(512), nullable=True)
    status = Column(Enum(AccountStatus), default=AccountStatus.offline, nullable=False)
    limits = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    jobs = relationship("Job", back_populates="account")


class GroupRecord(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    group_id = Column(String(128), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    invite_link = Column(String(255), nullable=True)
    members_count = Column(Integer, nullable=True)
    found_keyword = Column(String(100), nullable=True)
    source_file = Column(String(255), nullable=True)
    status = Column(Enum(GroupStatus), default=GroupStatus.new, nullable=False)
    members_hidden = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MemberRecord(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    phone = Column(String(64), nullable=True)
    is_bot = Column(Boolean, default=False, nullable=False)
    mutual_contact = Column(Boolean, default=False, nullable=False)
    source_group = Column(String(128), nullable=True)
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(64), nullable=True)
    saved_file = Column(String(255), nullable=True)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    type = Column(Enum(JobType), nullable=False)
    owner = Column(String(100), nullable=True)
    payload = Column(JSON, default=dict, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.pending, nullable=False)
    progress = Column(Float, default=0.0, nullable=False)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    account = relationship("Account", back_populates="jobs")
    logs = relationship("ItemLog", back_populates="job")


class ItemLog(Base):
    __tablename__ = "item_logs"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    user_id = Column(String(128), nullable=True)
    target = Column(String(255), nullable=True)
    action = Column(String(64), nullable=False)
    status = Column(String(64), nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("Job", back_populates="logs")


class SentLog(Base):
    __tablename__ = "sent_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(128), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    status = Column(String(64), nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    last_error = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False)


__all__ = [
    "Account",
    "AccountStatus",
    "GroupRecord",
    "GroupStatus",
    "Job",
    "JobStatus",
    "JobType",
    "ItemLog",
    "MemberRecord",
    "SentLog",
]
