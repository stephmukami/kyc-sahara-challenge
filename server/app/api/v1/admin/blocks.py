import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.app import App
from app.models.app_kyc_block_config import AppKYCBlockConfig
from app.models.kyc_block_definition import KYCBlockDefinition
from app.schemas.block import (
    AppBlockConfigRead,
    AppBlocksBulkSetRequest,
    KYCBlockDefinitionRead,
)

router = APIRouter(tags=["admin:blocks"])


@router.get("/admin/kyc-blocks", response_model=list[KYCBlockDefinitionRead])
async def list_block_catalog(
    db: AsyncSession = Depends(get_db),
) -> list[KYCBlockDefinition]:
    result = await db.execute(
        select(KYCBlockDefinition).order_by(KYCBlockDefinition.category, KYCBlockDefinition.code)
    )
    return list(result.scalars().all())


@router.get("/admin/apps/{app_id}/blocks", response_model=list[AppBlockConfigRead])
async def get_app_blocks(
    app_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[AppKYCBlockConfig]:
    if await db.get(App, app_id) is None:
        raise HTTPException(status_code=404, detail="app not found")

    result = await db.execute(
        select(AppKYCBlockConfig)
        .where(AppKYCBlockConfig.app_id == app_id)
        .options(selectinload(AppKYCBlockConfig.block))
        .order_by(AppKYCBlockConfig.order_index)
    )
    return list(result.scalars().all())


@router.put("/admin/apps/{app_id}/blocks", response_model=list[AppBlockConfigRead])
async def set_app_blocks(
    app_id: uuid.UUID,
    payload: AppBlocksBulkSetRequest,
    db: AsyncSession = Depends(get_db),
) -> list[AppKYCBlockConfig]:
    if await db.get(App, app_id) is None:
        raise HTTPException(status_code=404, detail="app not found")

    await db.execute(delete(AppKYCBlockConfig).where(AppKYCBlockConfig.app_id == app_id))

    configs = [
        AppKYCBlockConfig(
            app_id=app_id,
            block_id=item.block_id,
            order_index=item.order_index,
            is_required=item.is_required,
            is_enabled=item.is_enabled,
            config_overrides=item.config_overrides,
            updated_by_id=payload.updated_by_id,
        )
        for item in payload.blocks
    ]
    db.add_all(configs)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="invalid block_id, duplicate block in the list, or invalid updated_by_id",
        ) from exc

    result = await db.execute(
        select(AppKYCBlockConfig)
        .where(AppKYCBlockConfig.app_id == app_id)
        .options(selectinload(AppKYCBlockConfig.block))
        .order_by(AppKYCBlockConfig.order_index)
    )
    return list(result.scalars().all())
