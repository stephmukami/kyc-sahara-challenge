import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.app import App
from app.models.enums import SessionStatus
from app.models.kyc_session import KYCSession
from app.schemas.app import AppCreate, AppListItem, AppRead

router = APIRouter(prefix="/admin/apps", tags=["admin:apps"])

ACTIVE_SESSION_STATUSES = (
    SessionStatus.created,
    SessionStatus.in_progress,
    SessionStatus.pending_review,
)


@router.get("", response_model=list[AppListItem])
async def list_apps(db: AsyncSession = Depends(get_db)) -> list[AppListItem]:
    session_counts = (
        select(
            KYCSession.app_id,
            func.count(KYCSession.id).label("active_session_count"),
        )
        .where(KYCSession.status.in_(ACTIVE_SESSION_STATUSES))
        .group_by(KYCSession.app_id)
        .subquery()
    )

    stmt = select(App, func.coalesce(session_counts.c.active_session_count, 0)).outerjoin(
        session_counts, session_counts.c.app_id == App.id
    )
    result = await db.execute(stmt)

    return [
        AppListItem(**AppRead.model_validate(app).model_dump(), active_session_count=count)
        for app, count in result.all()
    ]


@router.post("", response_model=AppRead, status_code=201)
async def create_app(payload: AppCreate, db: AsyncSession = Depends(get_db)) -> App:
    app = App(
        name=payload.name,
        slug=payload.slug,
        allowed_channels=[c.value for c in payload.allowed_channels],
        phone_trigger_number=payload.phone_trigger_number,
        default_language=payload.default_language,
        webhook_url=payload.webhook_url,
        created_by_id=payload.created_by_id,
    )
    db.add(app)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=409, detail="slug already exists or created_by_id is invalid"
        ) from exc
    await db.refresh(app)
    return app


@router.get("/{app_id}", response_model=AppRead)
async def get_app(app_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> App:
    app = await db.get(App, app_id)
    if app is None:
        raise HTTPException(status_code=404, detail="app not found")
    return app
