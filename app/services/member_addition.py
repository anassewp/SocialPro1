from __future__ import annotations

import random
import time
from typing import Iterable

from ..models import ItemLog, JobStatus, JobType
from ..database import session_scope
from .jobs import job_service
from .telegram import MemberResult, telegram_service


class MemberAdditionService:
    def add_members(
        self,
        *,
        members: Iterable[MemberResult],
        group_id: str,
        account_labels: list[str],
        adds_per_hour: int,
        max_retry_per_user: int = 2,
        owner: str | None = None,
    ) -> int:
        job = job_service.create_job(
            JobType.member_addition,
            {
                "group_id": group_id,
                "accounts": account_labels,
                "adds_per_hour": adds_per_hour,
                "max_retry": max_retry_per_user,
            },
            owner=owner,
        )
        job_service.update_status(job.id, status=JobStatus.running)
        if not account_labels:
            job_service.update_status(
                job.id,
                status=JobStatus.failed,
                last_error="No accounts available",
                finished=True,
            )
            return job.id
        cooldown = max(1, int(3600 / max(adds_per_hour, 1)))
        account_cycle = iter(account_labels)
        member_list = list(members)

        def next_account() -> str:
            nonlocal account_cycle
            try:
                return next(account_cycle)
            except StopIteration:
                account_cycle = iter(account_labels)
                return next(account_cycle)

        successes = 0
        for member in member_list:
            attempts = 0
            account = next_account()
            while attempts <= max_retry_per_user:
                attempts += 1
                success, error = telegram_service.add_member(account, group_id, member)
                with session_scope() as session:
                    session.add(
                        ItemLog(
                            job_id=job.id,
                            user_id=member.user_id,
                            target=group_id,
                            action="ADD_MEMBER",
                            status="SUCCESS" if success else "FAILED",
                            attempts=attempts,
                            last_error=error,
                        )
                    )
                if success:
                    successes += 1
                    break
                if error == "PRIVACY_RESTRICTION":
                    break
                time.sleep(random.uniform(1, 5))
            time.sleep(random.uniform(cooldown * 0.5, cooldown * 1.5))
            job_service.update_status(job.id, progress=successes / max(1, len(member_list)))

        job_service.update_status(job.id, status=JobStatus.success, progress=1.0, finished=True)
        return job.id


member_addition_service = MemberAdditionService()

__all__ = ["MemberAdditionService", "member_addition_service"]
