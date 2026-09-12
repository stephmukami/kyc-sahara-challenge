import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_otp,
    generate_reset_token,
    hash_lookup_token,
    hash_otp,
    hash_password,
    verify_otp,
    verify_password,
)
from app.models.admin_password_reset_token import AdminPasswordResetToken
from app.models.admin_user import AdminUser
from app.models.enums import AdminRole, Channel, OTPPurpose
from app.models.end_user import EndUser
from app.models.otp_code import OTPCode
from app.services.providers.telephony.africastalking import get_telephony_provider

settings = get_settings()
logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Base class for auth-flow errors; routes map these to HTTP responses."""


class EmailAlreadyExistsError(AuthError):
    pass


class InvalidCredentialsError(AuthError):
    pass


class InvalidResetTokenError(AuthError):
    pass


class PhoneAlreadyRegisteredError(AuthError):
    pass


class PhoneNotRegisteredError(AuthError):
    pass


class InvalidOTPError(AuthError):
    pass


def _tokens_for_admin(admin: AdminUser) -> dict[str, str]:
    return {
        "access_token": create_access_token(subject=admin.id, role=admin.role.value),
        "refresh_token": create_refresh_token(subject=admin.id, role=admin.role.value),
        "token_type": "bearer",
    }


def _tokens_for_end_user(user: EndUser) -> dict[str, str]:
    return {
        "access_token": create_access_token(subject=user.id, role="end_user"),
        "refresh_token": create_refresh_token(subject=user.id, role="end_user"),
        "token_type": "bearer",
    }


async def create_admin(
    db: AsyncSession, *, email: str, password: str, role: AdminRole
) -> AdminUser:
    admin = AdminUser(email=email, password_hash=hash_password(password), role=role)
    db.add(admin)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise EmailAlreadyExistsError from exc
    await db.refresh(admin)
    return admin


async def authenticate_admin(db: AsyncSession, *, email: str, password: str) -> dict[str, str]:
    result = await db.execute(select(AdminUser).where(AdminUser.email == email))
    admin = result.scalar_one_or_none()
    if admin is None or not verify_password(password, admin.password_hash):
        raise InvalidCredentialsError
    return _tokens_for_admin(admin)


async def request_admin_password_reset(db: AsyncSession, *, email: str) -> None:
    result = await db.execute(select(AdminUser).where(AdminUser.email == email))
    admin = result.scalar_one_or_none()
    if admin is None:
        return  # caller always reports success — no account enumeration

    raw_token = generate_reset_token()
    reset_token = AdminPasswordResetToken(
        admin_user_id=admin.id,
        token_hash=hash_lookup_token(raw_token),
        expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=settings.password_reset_token_ttl_minutes),
    )
    db.add(reset_token)
    await db.commit()

    # TODO: wire a real email provider (SES/SendGrid/etc). Logging the raw
    # token is a placeholder so the reset flow is runnable in dev without one.
    logger.warning("Password reset token for %s: %s", admin.email, raw_token)


async def reset_admin_password(db: AsyncSession, *, token: str, new_password: str) -> None:
    result = await db.execute(
        select(AdminPasswordResetToken).where(
            AdminPasswordResetToken.token_hash == hash_lookup_token(token)
        )
    )
    reset_token = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if reset_token is None or reset_token.used_at is not None or reset_token.expires_at < now:
        raise InvalidResetTokenError

    admin = await db.get(AdminUser, reset_token.admin_user_id)
    if admin is None:
        raise InvalidResetTokenError

    admin.password_hash = hash_password(new_password)
    reset_token.used_at = now
    await db.commit()


async def _get_or_create_end_user(
    db: AsyncSession, *, phone_number: str, full_name: str | None
) -> EndUser:
    result = await db.execute(select(EndUser).where(EndUser.phone_number == phone_number))
    user = result.scalar_one_or_none()
    if user is None:
        user = EndUser(phone_number=phone_number, full_name=full_name)
        db.add(user)
        await db.flush()
    return user


async def _issue_otp(
    db: AsyncSession, *, user: EndUser, purpose: OTPPurpose, channel: Channel
) -> None:
    # Invalidate any still-outstanding OTP for this purpose before issuing a new one.
    result = await db.execute(
        select(OTPCode).where(
            OTPCode.end_user_id == user.id,
            OTPCode.purpose == purpose,
            OTPCode.consumed_at.is_(None),
        )
    )
    for stale in result.scalars().all():
        stale.consumed_at = datetime.now(timezone.utc)

    code = generate_otp()
    otp = OTPCode(
        end_user_id=user.id,
        code_hash=hash_otp(code),
        purpose=purpose,
        channel=channel,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.otp_ttl_minutes),
    )
    db.add(otp)
    await db.commit()

    get_telephony_provider().send_otp(user.phone_number, code)


async def start_user_signup(
    db: AsyncSession, *, phone_number: str, first_name: str, last_name: str
) -> None:
    result = await db.execute(select(EndUser).where(EndUser.phone_number == phone_number))
    existing = result.scalar_one_or_none()
    if existing is not None and existing.is_verified:
        raise PhoneAlreadyRegisteredError

    full_name = f"{first_name} {last_name}".strip()
    user = existing or await _get_or_create_end_user(
        db, phone_number=phone_number, full_name=full_name
    )
    user.full_name = full_name
    await db.commit()

    await _issue_otp(db, user=user, purpose=OTPPurpose.signup, channel=Channel.app)


async def start_user_login(db: AsyncSession, *, phone_number: str) -> None:
    result = await db.execute(select(EndUser).where(EndUser.phone_number == phone_number))
    user = result.scalar_one_or_none()
    if user is None or not user.is_verified:
        raise PhoneNotRegisteredError

    await _issue_otp(db, user=user, purpose=OTPPurpose.login, channel=Channel.app)


async def _consume_otp(
    db: AsyncSession, *, phone_number: str, code: str, purpose: OTPPurpose
) -> EndUser:
    result = await db.execute(select(EndUser).where(EndUser.phone_number == phone_number))
    user = result.scalar_one_or_none()
    if user is None:
        raise InvalidOTPError

    result = await db.execute(
        select(OTPCode)
        .where(
            OTPCode.end_user_id == user.id,
            OTPCode.purpose == purpose,
            OTPCode.consumed_at.is_(None),
        )
        .order_by(OTPCode.created_at.desc())
    )
    otp = result.scalars().first()
    now = datetime.now(timezone.utc)
    if otp is None or otp.expires_at < now or otp.attempts >= settings.otp_max_attempts:
        raise InvalidOTPError

    if not verify_otp(code, otp.code_hash):
        otp.attempts += 1
        await db.commit()
        raise InvalidOTPError

    otp.consumed_at = now
    await db.commit()
    return user


async def verify_user_signup(db: AsyncSession, *, phone_number: str, code: str) -> dict[str, str]:
    user = await _consume_otp(db, phone_number=phone_number, code=code, purpose=OTPPurpose.signup)
    user.is_verified = True
    await db.commit()
    return _tokens_for_end_user(user)


async def verify_user_login(db: AsyncSession, *, phone_number: str, code: str) -> dict[str, str]:
    user = await _consume_otp(db, phone_number=phone_number, code=code, purpose=OTPPurpose.login)
    return _tokens_for_end_user(user)


async def complete_voice_signup(
    db: AsyncSession, *, phone_number: str, recording_url: str
) -> EndUser:
    """Inbound call signup: caller ID is the proof of phone ownership, so no
    OTP round-trip is needed. The spoken name is stored as an audio
    recording — transcription into `full_name` is a later, separate step."""
    result = await db.execute(select(EndUser).where(EndUser.phone_number == phone_number))
    user = result.scalar_one_or_none()
    if user is None:
        user = EndUser(phone_number=phone_number)
        db.add(user)

    user.is_verified = True
    user.full_name_audio_ref = recording_url
    await db.commit()
    await db.refresh(user)
    return user
