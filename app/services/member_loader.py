from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator

from .telegram import MemberResult


def load_members_from_csv(file_path: Path) -> Iterator[MemberResult]:
    with file_path.open("r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield MemberResult(
                user_id=row.get("user_id", ""),
                username=row.get("username") or None,
                first_name=row.get("first_name") or None,
                last_name=row.get("last_name") or None,
                phone=row.get("phone") or None,
                is_bot=row.get("is_bot") in {"True", "true", "1", 1, True},
                mutual_contact=row.get("mutual_contact") in {"True", "true", "1", 1, True},
                source_group=row.get("source_group") or "",
            )


__all__ = ["load_members_from_csv"]
