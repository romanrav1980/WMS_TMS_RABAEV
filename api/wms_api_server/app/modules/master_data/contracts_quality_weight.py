from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class WeightPolicyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(strict=True, ge=0)
    base_uom: str = Field(min_length=1,max_length=20,pattern=r'^[A-Z0-9_]+$')
    base_weight_kg: Decimal | None = Field(default=None, gt=0, max_digits=18, decimal_places=9)
    box_weight_kg: Decimal | None = Field(default=None, gt=0, max_digits=18, decimal_places=9)

