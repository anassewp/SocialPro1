from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Sequence

from ..config import GROUPS_DIR, MEMBERS_DIR, PREPARED_DIR


class FileService:
    """Handle persistence of group and member data on disk."""

    def __init__(self) -> None:
        self.groups_dir = GROUPS_DIR
        self.members_dir = MEMBERS_DIR
        self.prepared_dir = PREPARED_DIR

    # Group files
    def save_group_results(self, filename: str, rows: Sequence[dict]) -> Path:
        path = self.groups_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for row in rows:
                line = "|".join(
                    [
                        str(row.get("group_id", "")),
                        row.get("group_title", ""),
                        row.get("invite_link", ""),
                        str(row.get("members_count", "")),
                        row.get("found_keyword", ""),
                    ]
                )
                f.write(f"{line}\n")
        return path

    def save_members(self, filename: str, rows: Sequence[dict]) -> Path:
        path = self.members_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=[
                    "user_id",
                    "username",
                    "first_name",
                    "last_name",
                    "phone",
                    "is_bot",
                    "mutual_contact",
                    "source_group",
                    "extracted_at",
                ],
            )
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return path

    def save_prepared_members(self, filename: str, rows: Sequence[dict]) -> Path:
        path = self.prepared_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys() if rows else [])
            if rows:
                writer.writeheader()
                for row in rows:
                    writer.writerow(row)
        return path

    def dump_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def timestamped_filename(prefix: str, ext: str = "txt") -> str:
        suffix = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{suffix}.{ext}"


file_service = FileService()

__all__ = ["FileService", "file_service"]
