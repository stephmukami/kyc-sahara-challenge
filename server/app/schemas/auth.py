import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AdminRole


class MessageResponse(BaseModel):
    detail: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AdminSignupRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)
    role: AdminRole = AdminRole.app_admin


class AdminRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    role: AdminRole
    created_at: datetime


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AdminForgotPasswordRequest(BaseModel):
    email: str


class AdminResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class ClientSignupRequest(BaseModel):
    phone_number: str = Field(pattern=r"^\+?[1-9]\d{6,14}$")
    first_name: str
    last_name: str


class ClientSignupVerifyRequest(BaseModel):
    phone_number: str
    otp_code: str


class ClientLoginRequest(BaseModel):
    phone_number: str


class ClientLoginVerifyRequest(BaseModel):
    phone_number: str
    otp_code: str
