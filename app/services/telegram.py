from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, List

from ..config import get_settings


@dataclass
class GroupResult:
    group_id: str
    group_title: str
    invite_link: str | None
    members_count: int
    found_keyword: str
    members_hidden: bool = False


@dataclass
class MemberResult:
    user_id: str
    username: str | None
    first_name: str | None
    last_name: str | None
    phone: str | None
    is_bot: bool
    mutual_contact: bool
    source_group: str


class TelegramService:
    """Facade for Telegram interactions (search, extraction, messaging).

    This implementation provides deterministic mocked data so the backend can
    be developed and tested without live Telegram connectivity. Replace the
    mock implementations with real Telethon/Pyrogram logic in production.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    # --- Group Search ---
    def search_groups(self, keywords: Iterable[str], limit: int) -> List[GroupResult]:
        results: list[GroupResult] = []
        for keyword in keywords:
            for index in range(1, limit + 1):
                group_id = f"{hash(keyword) & 0xFFFF:x}{index:03d}"
                results.append(
                    GroupResult(
                        group_id=group_id,
                        group_title=f"{keyword.title()} Community {index}",
                        invite_link=f"https://t.me/{keyword}_{index}",
                        members_count=random.randint(100, 10000),
                        found_keyword=keyword,
                        members_hidden=random.random() < 0.1,
                    )
                )
        return results

    # --- Member Extraction ---
    def extract_members(self, group_id: str, count: int = 200) -> List[MemberResult]:
        members: list[MemberResult] = []
        for idx in range(1, count + 1):
            members.append(
                MemberResult(
                    user_id=f"{group_id}_{idx}",
                    username=f"user_{group_id}_{idx}" if idx % 5 != 0 else None,
                    first_name=f"First{idx}",
                    last_name=f"Last{idx}" if idx % 7 != 0 else None,
                    phone=f"+1000{idx:07d}" if idx % 3 == 0 else None,
                    is_bot=idx % 11 == 0,
                    mutual_contact=idx % 4 == 0,
                    source_group=group_id,
                )
            )
        return members

    # --- Member addition / Messaging (stubs) ---
    def add_member(self, account_label: str, group_id: str, member: MemberResult) -> tuple[bool, str | None]:
        if member.is_bot:
            return False, "TARGET_IS_BOT"
        if random.random() < 0.05:
            return False, "PRIVACY_RESTRICTION"
        return True, None

    def send_message(self, account_label: str, member: MemberResult, message: str) -> tuple[bool, str | None]:
        if random.random() < 0.05:
            return False, "USER_BLOCKED"
        return True, None


telegram_service = TelegramService()

__all__ = ["GroupResult", "MemberResult", "TelegramService", "telegram_service"]
