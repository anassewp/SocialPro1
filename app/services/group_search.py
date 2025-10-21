from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from sqlalchemy import select

from ..models import GroupRecord, GroupStatus, JobStatus, JobType
from ..database import session_scope
from .files import file_service
from .jobs import job_service
from .telegram import telegram_service


class GroupSearchService:
    def start_search(
        self,
        *,
        keywords: Iterable[str],
        limit_per_keyword: int,
        file_name: str,
        owner: str | None = None,
        min_members: int = 0,
    ) -> tuple[int, str]:
        job = job_service.create_job(
            JobType.group_search,
            {
                "keywords": list(keywords),
                "limit_per_keyword": limit_per_keyword,
                "file_name": file_name,
                "min_members": min_members,
            },
            owner=owner,
        )
        job_service.update_status(job.id, status=JobStatus.running)
        results = telegram_service.search_groups(keywords, limit_per_keyword)
        filtered = [r for r in results if r.members_count >= min_members]
        file_path = file_service.save_group_results(file_name, [asdict(r) for r in filtered])

        with session_scope() as session:
            for entry in filtered:
                record = session.execute(
                    select(GroupRecord).where(GroupRecord.group_id == entry.group_id)
                ).scalar_one_or_none()
                if record:
                    record.title = entry.group_title
                    record.invite_link = entry.invite_link
                    record.members_count = entry.members_count
                    record.found_keyword = entry.found_keyword
                    record.source_file = file_path.name
                    record.members_hidden = entry.members_hidden
                else:
                    session.add(
                        GroupRecord(
                            group_id=entry.group_id,
                            title=entry.group_title,
                            invite_link=entry.invite_link,
                            members_count=entry.members_count,
                            found_keyword=entry.found_keyword,
                            source_file=file_path.name,
                            status=GroupStatus.new,
                            members_hidden=entry.members_hidden,
                        )
                    )
        job_service.update_status(job.id, status=JobStatus.success, progress=1.0, finished=True)
        return job.id, str(file_path)


group_search_service = GroupSearchService()

__all__ = ["GroupSearchService", "group_search_service"]
