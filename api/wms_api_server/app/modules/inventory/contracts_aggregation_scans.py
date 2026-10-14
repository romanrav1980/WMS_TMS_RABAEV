from ..master_data.contracts import MarkingProfileCode
"""Shared scanner boundary for registered box/pallet aggregation evidence."""
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field


class AggregationCodeScan(BaseModel):
    model_config=ConfigDict(extra="forbid")
    system_code: str=Field(strict=True,min_length=1,max_length=40)
    profile_code: MarkingProfileCode
    level: Literal["BOX","PALLET"]
    code: str=Field(strict=True,min_length=1,max_length=4000)
