import uuid

from pydantic import BaseModel, ConfigDict

from app.models.enums import BlockCategory


class KYCBlockDefinitionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    category: BlockCategory
    supports_channels: list[str]
    input_schema: dict
    default_config: dict
    version: int


class AppBlockConfigItem(BaseModel):
    block_id: uuid.UUID
    order_index: int
    is_required: bool = True
    is_enabled: bool = True
    config_overrides: dict = {}


class AppBlocksBulkSetRequest(BaseModel):
    updated_by_id: uuid.UUID
    blocks: list[AppBlockConfigItem]


class AppBlockConfigRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order_index: int
    is_required: bool
    is_enabled: bool
    config_overrides: dict
    block: KYCBlockDefinitionRead
