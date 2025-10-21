from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Iterable

from sqlalchemy import select

from ..database import session_scope
from ..models import GroupRecord, GroupStatus, JobStatus, JobType, MemberRecord
from .files import file_service
from .jobs import job_service
from .telegram import MemberResult, telegram_service


class MemberExtractionService:
    def start_extraction(
        self,
        *,
        groups: Iterable[str],
        file_name: str,
        owner: str | None = None,
        batch_size: int = 200,
    ) -> tuple[int, str]:
        group_list = list(groups)
        job = job_service.create_job(
            JobType.member_extraction,
            {
                "groups": group_list,
                "file_name": file_name,
                "batch_size": batch_size,
            },
            owner=owner,
        )
        job_service.update_status(job.id, status=JobStatus.running)
        all_members: list[MemberResult] = []
        for group_id in group_list:
            members = telegram_service.extract_members(group_id, count=batch_size)
            all_members.extend(members)
            job_service.update_status(
                job.id,
                progress=min(1.0, len(all_members) / (len(group_list) * batch_size)) if group_list else 1.0,
            )
        rows = [
            {
                **asdict(member),
                "extracted_at": datetime.utcnow().isoformat(),
            }
            for member in all_members
        ]
        file_path = file_service.save_members(file_name, rows)

        with session_scope() as session:
            for row in rows:
                record = session.execute(
                    select(MemberRecord).where(MemberRecord.user_id == row["user_id"])
                ).scalar_one_or_none()
                if record:
                    record.username = row["username"]
                    record.first_name = row["first_name"]
                    record.last_name = row["last_name"]
                    record.phone = row["phone"]
                    record.is_bot = row["is_bot"]
                    record.mutual_contact = row["mutual_contact"]
                    record.source_group = row["source_group"]
                    record.extracted_at = datetime.fromisoformat(row["extracted_at"])
                    record.saved_file = file_name
                else:
                    session.add(
                        MemberRecord(
                            user_id=row["user_id"],
                            username=row["username"],
                            first_name=row["first_name"],
                            last_name=row["last_name"],
                            phone=row["phone"],
                            is_bot=row["is_bot"],
                            mutual_contact=row["mutual_contact"],
                            source_group=row["source_group"],
                            extracted_at=datetime.fromisoformat(row["extracted_at"]),
                            saved_file=file_name,
                        )
                    )
            session.query(GroupRecord).filter(GroupRecord.group_id.in_(list(groups))).update(
                {GroupRecord.status: GroupStatus.extracted}, synchronize_session=False
            )
        job_service.update_status(job.id, status=JobStatus.success, progress=1.0, finished=True)
        return job.id, str(file_path)


member_extraction_service = MemberExtractionService()

__all__ = ["MemberExtractionService", "member_extraction_service"]
