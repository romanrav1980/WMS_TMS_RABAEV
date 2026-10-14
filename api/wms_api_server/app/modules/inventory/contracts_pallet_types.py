"""Existing logistics carrier type contract with an explicit final weight requirement."""
from decimal import Decimal
from pydantic import BaseModel,Field

class PalletTypeUpsertRequest(BaseModel):
    pallet_type_id: int | None = None
    pallet_type_code: str = Field(min_length=1,max_length=50)
    pallet_type_name: str = Field(min_length=1,max_length=160)
    load_unit_class: str = Field(default="PALLET",min_length=1,max_length=20)
    default_volume_m3: Decimal | None = Field(default=None, ge=0, max_digits=27, decimal_places=9)
    default_weight_kg: Decimal | None = Field(default=None, ge=0, max_digits=27, decimal_places=9)
    length_mm: Decimal | None = Field(default=None, ge=0, max_digits=27, decimal_places=9)
    width_mm: Decimal | None = Field(default=None, ge=0, max_digits=27, decimal_places=9)
    height_mm: Decimal | None = Field(default=None, ge=0, max_digits=27, decimal_places=9)
    default_max_client_pallets: int = Field(default=1, ge=1, le=3)
    expected_version: int | None = Field(default=None,ge=0,strict=True)
    final_weight_required: bool | None = None
    active: int = Field(default=1,ge=0,le=1)
    updated_by: str | None = None
