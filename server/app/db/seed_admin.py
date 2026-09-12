"""Creates the first super_admin. This has to exist before /admin/auth/signup
can be used at all, since that endpoint requires an authenticated super_admin.

Run with: uv run python -m app.db.seed_admin <email> <password>
"""

import asyncio
import sys

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.admin_user import AdminUser
from app.models.enums import AdminRole


async def seed_super_admin(email: str, password: str) -> None:
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(AdminUser).where(AdminUser.email == email))
        if existing.scalar_one_or_none() is not None:
            print(f"Admin with email {email} already exists — nothing to do.")
            return

        admin = AdminUser(
            email=email, password_hash=hash_password(password), role=AdminRole.super_admin
        )
        db.add(admin)
        await db.commit()
        print(f"Created super_admin: {email}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: uv run python -m app.db.seed_admin <email> <password>")
        sys.exit(1)

    asyncio.run(seed_super_admin(sys.argv[1], sys.argv[2]))
