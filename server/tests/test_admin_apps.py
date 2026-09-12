from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_user import AdminUser
from app.models.enums import AdminRole


async def _create_admin(db: AsyncSession) -> AdminUser:
    admin = AdminUser(
        email="admin@greenwheels.africa",
        password_hash="not-a-real-hash",
        role=AdminRole.super_admin,
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin


async def test_create_and_list_apps(client: AsyncClient, db: AsyncSession):
    admin = await _create_admin(db)

    create_resp = await client.post(
        "/api/v1/admin/apps",
        json={
            "name": "Rider Onboarding",
            "slug": "rider-onboarding",
            "allowed_channels": ["app", "call"],
            "default_language": "sw-KE",
            "created_by_id": str(admin.id),
        },
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["slug"] == "rider-onboarding"

    list_resp = await client.get("/api/v1/admin/apps")
    assert list_resp.status_code == 200
    apps = list_resp.json()
    assert len(apps) == 1
    assert apps[0]["active_session_count"] == 0


async def test_create_app_duplicate_slug_conflicts(client: AsyncClient, db: AsyncSession):
    admin = await _create_admin(db)
    payload = {
        "name": "Rider Onboarding",
        "slug": "rider-onboarding",
        "created_by_id": str(admin.id),
    }
    first = await client.post("/api/v1/admin/apps", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/admin/apps", json=payload)
    assert second.status_code == 409
