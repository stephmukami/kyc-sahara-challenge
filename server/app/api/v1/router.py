from fastapi import APIRouter

from app.api.v1.admin import apps as admin_apps
from app.api.v1.admin import blocks as admin_blocks

api_router = APIRouter()
api_router.include_router(admin_apps.router)
api_router.include_router(admin_blocks.router)
