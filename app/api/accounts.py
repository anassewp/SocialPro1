from __future__ import annotations

from fastapi import APIRouter, status

from ..schemas import AccountCreate, AccountRead
from ..services.accounts import account_service

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def register_account(payload: AccountCreate) -> AccountRead:
    account = account_service.register_account(
        label=payload.label,
        phone=payload.phone,
        api_id=payload.api_id,
        api_hash=payload.api_hash,
        session_path=payload.session_path,
        limits=payload.limits,
    )
    return AccountRead.from_orm(account)


@router.get("", response_model=list[AccountRead])
def list_accounts() -> list[AccountRead]:
    accounts = account_service.list_accounts()
    return [AccountRead.from_orm(acc) for acc in accounts]
