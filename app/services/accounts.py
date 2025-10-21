from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select

from ..database import session_scope
from ..models import Account, AccountStatus
from .security import encryption_service


class AccountService:
    def register_account(
        self,
        *,
        label: str,
        phone: str,
        api_id: str,
        api_hash: str,
        session_path: str | None = None,
        limits: dict[str, Any] | None = None,
    ) -> Account:
        with session_scope() as session:
            encrypted_id = encryption_service.encrypt(api_id)
            encrypted_hash = encryption_service.encrypt(api_hash)
            account = Account(
                label=label,
                phone=phone,
                api_id_encrypted=encrypted_id,
                api_hash_encrypted=encrypted_hash,
                session_path=session_path,
                limits=limits or {},
                status=AccountStatus.offline,
            )
            session.add(account)
            session.flush()
            session.refresh(account)
            return account

    def list_accounts(self) -> list[Account]:
        with session_scope() as session:
            return list(session.scalars(select(Account).order_by(Account.created_at.desc())))

    def update_status(self, account_id: int, status: AccountStatus) -> Account | None:
        with session_scope() as session:
            account = session.get(Account, account_id)
            if not account:
                return None
            account.status = status
            account.last_activity = datetime.utcnow()
            session.add(account)
            session.flush()
            session.refresh(account)
            return account


account_service = AccountService()

__all__ = ["AccountService", "account_service"]
