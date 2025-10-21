from __future__ import annotations

from fastapi import FastAPI

from .config import get_settings
from .database import Base, engine
from .api import accounts, groups, jobs, members


def create_application() -> FastAPI:
    _ = get_settings()
    Base.metadata.create_all(bind=engine)
    app = FastAPI(title="SocialPro Automation Backend")

    app.include_router(accounts.router)
    app.include_router(groups.router)
    app.include_router(members.router)
    app.include_router(jobs.router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_application()
