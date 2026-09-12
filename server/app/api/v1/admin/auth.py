from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_super_admin
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.schemas.auth import (
    AdminForgotPasswordRequest,
    AdminLoginRequest,
    AdminRead,
    AdminResetPasswordRequest,
    AdminSignupRequest,
    MessageResponse,
    TokenResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/admin/auth", tags=["admin:auth"])


@router.post("/signup", response_model=AdminRead, status_code=201)
async def signup_admin(
    payload: AdminSignupRequest,
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(require_super_admin),
) -> AdminUser:
    try:
        return await auth_service.create_admin(
            db, email=payload.email, password=payload.password, role=payload.role
        )
    except auth_service.EmailAlreadyExistsError as exc:
        raise HTTPException(
            status_code=409, detail="an admin with this email already exists"
        ) from exc


@router.post("/login", response_model=TokenResponse)
async def login_admin(
    payload: AdminLoginRequest, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    try:
        return await auth_service.authenticate_admin(
            db, email=payload.email, password=payload.password
        )
    except auth_service.InvalidCredentialsError as exc:
        raise HTTPException(status_code=401, detail="invalid email or password") from exc


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_admin_password(
    payload: AdminForgotPasswordRequest, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    await auth_service.request_admin_password_reset(db, email=payload.email)
    return MessageResponse(
        detail="if an account with that email exists, a reset link has been sent"
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_admin_password(
    payload: AdminResetPasswordRequest, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    try:
        await auth_service.reset_admin_password(
            db, token=payload.token, new_password=payload.new_password
        )
    except auth_service.InvalidResetTokenError as exc:
        raise HTTPException(
            status_code=400, detail="reset token is invalid or expired"
        ) from exc
    return MessageResponse(detail="password has been reset")
