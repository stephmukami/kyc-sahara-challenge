from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import (
    ClientLoginRequest,
    ClientLoginVerifyRequest,
    ClientSignupRequest,
    ClientSignupVerifyRequest,
    MessageResponse,
    TokenResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/client/auth", tags=["client:auth"])


@router.post("/signup", response_model=MessageResponse)
async def signup(
    payload: ClientSignupRequest, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    try:
        await auth_service.start_user_signup(
            db,
            phone_number=payload.phone_number,
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
    except auth_service.PhoneAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=409, detail="this phone number is already registered"
        ) from exc
    return MessageResponse(detail="an OTP has been sent to your phone")


@router.post("/signup/verify", response_model=TokenResponse)
async def verify_signup(
    payload: ClientSignupVerifyRequest, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    try:
        return await auth_service.verify_user_signup(
            db, phone_number=payload.phone_number, code=payload.otp_code
        )
    except auth_service.InvalidOTPError as exc:
        raise HTTPException(status_code=400, detail="invalid or expired OTP") from exc


@router.post("/login", response_model=MessageResponse)
async def login(
    payload: ClientLoginRequest, db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    try:
        await auth_service.start_user_login(db, phone_number=payload.phone_number)
    except auth_service.PhoneNotRegisteredError as exc:
        raise HTTPException(status_code=404, detail="phone number is not registered") from exc
    return MessageResponse(detail="an OTP has been sent to your phone")


@router.post("/login/verify", response_model=TokenResponse)
async def verify_login(
    payload: ClientLoginVerifyRequest, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    try:
        return await auth_service.verify_user_login(
            db, phone_number=payload.phone_number, code=payload.otp_code
        )
    except auth_service.InvalidOTPError as exc:
        raise HTTPException(status_code=400, detail="invalid or expired OTP") from exc
