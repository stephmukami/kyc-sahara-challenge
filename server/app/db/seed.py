"""Seeds the starter KYC block catalog (§04 of the design doc).

Run with: uv run python -m app.db.seed
"""

import asyncio

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.enums import BlockCategory
from app.models.kyc_block_definition import KYCBlockDefinition

STARTER_CATALOG = [
    {
        "code": "phone_otp",
        "category": BlockCategory.identity,
        "supports_channels": ["app", "call"],
        "input_schema": {
            "type": "object",
            "properties": {"otp_code": {"type": "string"}},
            "required": ["otp_code"],
        },
        "default_config": {"provider": "africastalking"},
    },
    {
        "code": "id_document_upload",
        "category": BlockCategory.identity,
        "supports_channels": ["app"],
        "input_schema": {
            "type": "object",
            "properties": {"document_image_ref": {"type": "string"}},
            "required": ["document_image_ref"],
        },
        "default_config": {},
    },
    {
        "code": "selfie_liveness",
        "category": BlockCategory.biometric,
        "supports_channels": ["app"],
        "input_schema": {
            "type": "object",
            "properties": {"selfie_image_ref": {"type": "string"}},
            "required": ["selfie_image_ref"],
        },
        "default_config": {},
    },
    {
        "code": "voice_otp_challenge",
        "category": BlockCategory.biometric,
        "supports_channels": ["app", "call"],
        "input_schema": {
            "type": "object",
            "properties": {"audio_ref": {"type": "string"}},
            "required": ["audio_ref"],
        },
        "default_config": {"provider": "sahara"},
    },
    {
        "code": "consent_capture",
        "category": BlockCategory.consent,
        "supports_channels": ["app", "call"],
        "input_schema": {
            "type": "object",
            "properties": {"audio_ref": {"type": "string"}},
            "required": ["audio_ref"],
        },
        "default_config": {"provider": "sahara"},
    },
    {
        "code": "aml_screening",
        "category": BlockCategory.compliance,
        "supports_channels": [],
        "input_schema": {
            "type": "object",
            "properties": {"full_name": {"type": "string"}},
            "required": ["full_name"],
        },
        "default_config": {"provider": "internal_mock"},
    },
]


async def seed_block_catalog() -> None:
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(KYCBlockDefinition.code))
        existing_codes = set(existing.scalars().all())

        new_blocks = [
            KYCBlockDefinition(**entry)
            for entry in STARTER_CATALOG
            if entry["code"] not in existing_codes
        ]
        if not new_blocks:
            print("Block catalog already seeded — nothing to do.")
            return

        db.add_all(new_blocks)
        await db.commit()
        print(f"Seeded {len(new_blocks)} block(s): {[b.code for b in new_blocks]}")


if __name__ == "__main__":
    asyncio.run(seed_block_catalog())
