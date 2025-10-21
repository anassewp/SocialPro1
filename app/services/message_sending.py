from __future__ import annotations

import random
import time
from typing import Iterable

from ..database import session_scope
from ..models import ItemLog, JobStatus, JobType, SentLog
from .jobs import job_service
from .telegram import MemberResult, telegram_service


class MessageSendingService:
    def send_messages(
        self,
        *,
        members: Iterable[MemberResult],
        accounts: list[str],
        template: str,
        messages_per_minute: int = 15,
        owner: str | None = None,
    ) -> int:
        job = job_service.create_job(
            JobType.message_sending,
            {
                "template": template,
                "accounts": accounts,
                "messages_per_minute": messages_per_minute,
            },
            owner=owner,
        )
        job_service.update_status(job.id, status=JobStatus.running)
        if not accounts:
            job_service.update_status(
                job.id,
                status=JobStatus.failed,
                last_error="No accounts available",
                finished=True,
            )
            return job.id
        member_list = list(members)
        delay = 60 / max(messages_per_minute, 1)
        account_cycle = iter(accounts)

        def next_account() -> str:
            nonlocal account_cycle
            try:
                return next(account_cycle)
            except StopIteration:
                account_cycle = iter(accounts)
                return next(account_cycle)

        sent = 0
        for member in member_list:
            account = next_account()
            content = template.format(
                first_name=member.first_name or "",
                last_name=member.last_name or "",
                username=member.username or "",
                group_name=member.source_group,
            )
            success, error = telegram_service.send_message(account, member, content)
            with session_scope() as session:
                session.add(
                    SentLog(
                        user_id=member.user_id,
                        job_id=job.id,
                        account_id=None,
                        status="SENT" if success else "FAILED",
                        attempts=1,
                        last_error=error,
                    )
                )
                session.add(
                    ItemLog(
                        job_id=job.id,
                        user_id=member.user_id,
                        target=member.source_group,
                        action="SEND_MESSAGE",
                        status="SUCCESS" if success else "FAILED",
                        attempts=1,
                        last_error=error,
                    )
                )
            if success:
                sent += 1
            job_service.update_status(job.id, progress=sent / max(1, len(member_list)))
            time.sleep(random.uniform(delay * 0.5, delay * 1.5))

        job_service.update_status(job.id, status=JobStatus.success, progress=1.0, finished=True)
        return job.id


message_sending_service = MessageSendingService()

__all__ = ["MessageSendingService", "message_sending_service"]
