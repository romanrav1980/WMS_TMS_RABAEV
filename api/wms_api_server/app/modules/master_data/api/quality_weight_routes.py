from ..contracts_quality_weight import WeightPolicyInput
from decimal import Decimal
from typing import Protocol
from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel, ConfigDict, Field
from ...platform.public import AdminUser, require_permission


class WeightPolicyPort(Protocol):
    def get(self, warehouse: int, article: str) -> dict: ...
    def set(self, warehouse: int, article: str, request: WeightPolicyInput, actor: str) -> dict: ...




def quality_weight_service() -> WeightPolicyPort:
    raise RuntimeError("Quality weight policy service not wired")


router = APIRouter(prefix="/api/sku-quality-weight", tags=["sku-quality-weight"])


@router.get("/{warehouse}/{article}")
def get_policy(warehouse: int = Path(gt=0), article: str = Path(min_length=1, max_length=160),
               _user: AdminUser = Depends(require_permission("finished_goods_view")),
               service: WeightPolicyPort = Depends(quality_weight_service)) -> dict:
    return service.get(warehouse, article)


@router.put("/{warehouse}/{article}")
def set_policy(body: WeightPolicyInput, warehouse: int = Path(gt=0),
               article: str = Path(min_length=1, max_length=160),
               user: AdminUser = Depends(require_permission("warehouse_settings_edit")),
               service: WeightPolicyPort = Depends(quality_weight_service)) -> dict:
    return service.set(warehouse, article, body, user.username)
