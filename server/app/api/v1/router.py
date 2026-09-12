from fastapi import APIRouter

from app.api.v1.admin import apps as admin_apps
from app.api.v1.admin import auth as admin_auth
from app.api.v1.admin import blocks as admin_blocks
from app.api.v1.client import auth as client_auth
from app.api.v1.telephony import voice as telephony_voice

api_router = APIRouter()
api_router.include_router(admin_apps.router)
api_router.include_router(admin_auth.router)
api_router.include_router(admin_blocks.router)
api_router.include_router(client_auth.router)
api_router.include_router(telephony_voice.router)
