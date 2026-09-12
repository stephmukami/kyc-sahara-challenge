from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.seed import seed_block_catalog
from app.models.admin_user import AdminUser
from app.models.app import App
from app.models.enums import AdminRole
from app.models.kyc_block_definition import KYCBlockDefinition


async def test_list_block_catalog(client: AsyncClient, db: AsyncSession):
    await seed_block_catalog()

    resp = await client.get("/api/v1/admin/kyc-blocks")
    assert resp.status_code == 200
    codes = {b["code"] for b in resp.json()}
    assert "phone_otp" in codes
    assert "voice_otp_challenge" in codes


async def test_set_app_blocks(client: AsyncClient, db: AsyncSession):
    await seed_block_catalog()

    admin = AdminUser(
        email="admin@greenwheels.africa",
        password_hash="not-a-real-hash",
        role=AdminRole.super_admin,
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)

    app_obj = App(
        name="Rider Onboarding",
        slug="rider-onboarding",
        allowed_channels=["app"],
        default_language="en-KE",
        created_by_id=admin.id,
    )
    db.add(app_obj)
    await db.commit()
    await db.refresh(app_obj)

    blocks_result = await db.execute(
        select(KYCBlockDefinition).where(
            KYCBlockDefinition.code.in_(["phone_otp", "id_document_upload"])
        )
    )
    phone_otp, id_upload = blocks_result.scalars().all()

    resp = await client.put(
        f"/api/v1/admin/apps/{app_obj.id}/blocks",
        json={
            "updated_by_id": str(admin.id),
            "blocks": [
                {"block_id": str(phone_otp.id), "order_index": 0},
                {"block_id": str(id_upload.id), "order_index": 1, "is_required": False},
            ],
        },
    )
    assert resp.status_code == 200
    configs = resp.json()
    assert len(configs) == 2
    assert configs[0]["order_index"] == 0

    get_resp = await client.get(f"/api/v1/admin/apps/{app_obj.id}/blocks")
    assert get_resp.status_code == 200
    assert len(get_resp.json()) == 2
