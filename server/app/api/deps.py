import uuid

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.models.enums import AdminRole

bearer_scheme = HTTPBearer()


async def get_current_admin_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    try:
        payload = decode_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="invalid or expired token") from exc

    if payload.get("type") != "access" or "role" not in payload:
        raise HTTPException(status_code=401, detail="invalid token")

    admin = await db.get(AdminUser, uuid.UUID(payload["sub"]))
    if admin is None:
        raise HTTPException(status_code=401, detail="admin no longer exists")
    return admin


async def require_super_admin(
    admin: AdminUser = Depends(get_current_admin_user),
) -> AdminUser:
    if admin.role != AdminRole.super_admin:
        raise HTTPException(status_code=403, detail="super_admin role required")
    return admin
