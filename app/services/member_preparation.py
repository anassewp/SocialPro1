from __future__ import annotations

import csv
from pathlib import Path

from ..models import JobStatus, JobType
from .files import file_service
from .jobs import job_service


class MemberPreparationService:
    def prepare(
        self,
        *,
        source_file: Path,
        blacklist: set[str] | None = None,
        whitelist: set[str] | None = None,
        chunk_size: int = 1000,
        owner: str | None = None,
    ) -> dict[str, list[Path]]:
        job = job_service.create_job(
            JobType.member_preparation,
            {
                "source_file": str(source_file),
                "chunk_size": chunk_size,
            },
            owner=owner,
        )
        job_service.update_status(job.id, status=JobStatus.running)
        blacklist = blacklist or set()
        whitelist = whitelist or set()

        with source_file.open("r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            seen_ids: set[str] = set()
            filtered: list[dict] = []
            for row in reader:
                user_id = row.get("user_id")
                phone = row.get("phone")
                username = row.get("username")
                if not user_id:
                    continue
                if user_id in whitelist:
                    continue
                if user_id in blacklist or phone in blacklist or username in blacklist:
                    continue
                if row.get("is_bot") in {"True", "true", True}:
                    continue
                if user_id in seen_ids:
                    continue
                seen_ids.add(user_id)
                filtered.append(row)

        chunks: dict[str, list[Path]] = {"files": []}
        for index in range(0, len(filtered), chunk_size):
            chunk_rows = filtered[index : index + chunk_size]
            chunk_name = file_service.timestamped_filename(
                f"prepared_{source_file.stem}_chunk_{index // chunk_size:03d}",
                ext="csv",
            )
            path = file_service.save_prepared_members(chunk_name, chunk_rows)
            chunks.setdefault("files", []).append(path)

        job_service.update_status(job.id, status=JobStatus.success, progress=1.0, finished=True)
        chunks["job_id"] = job.id
        return chunks


member_preparation_service = MemberPreparationService()

__all__ = ["MemberPreparationService", "member_preparation_service"]
