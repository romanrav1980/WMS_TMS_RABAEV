from fastapi import APIRouter, Depends, HTTPException
from ...platform.public import AdminUser, require_permission
from ..application.ports import PreparationPort
from .store_order_routes import preparation_service

router=APIRouter(prefix="/api/integrations/sap/store-orders",tags=["sap-store-orders"])

@router.get("/{order_id}/preparation-readiness")
def readiness(order_id: int,user: AdminUser=Depends(require_permission("customer_order_view")),
              service: PreparationPort=Depends(preparation_service)) -> dict:
    try:
        return service.readiness(order_id,user.username)
    except PermissionError as exc:
        raise HTTPException(403,str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404,str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409,str(exc)) from exc

from pydantic import BaseModel,ConfigDict,Field
from typing import Annotated
class LayoutProposal(BaseModel):
    model_config=ConfigDict(extra="forbid")
    article_pallet_counts: dict[str,Annotated[int,Field(strict=True,ge=1,le=100)]]=Field(default_factory=dict,max_length=1000)

@router.post("/{order_id}/preparation-layout")
def layout(order_id: int,body: LayoutProposal,user: AdminUser=Depends(require_permission("customer_order_view")),
           service: PreparationPort=Depends(preparation_service)) -> dict:
    try:return service.layout(order_id,body.article_pallet_counts,user.username)
    except PermissionError as exc:raise HTTPException(403,str(exc))from exc
    except LookupError as exc:raise HTTPException(404,str(exc))from exc
    except ValueError as exc:raise HTTPException(409,str(exc))from exc


from decimal import Decimal
class AutoLimits(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_goods_weight_kg: Decimal = Field(gt=0, max_digits=18, decimal_places=6, allow_inf_nan=False)
    max_goods_volume_m3: Decimal = Field(gt=0, max_digits=18, decimal_places=9, allow_inf_nan=False)
    max_pallets: int = Field(strict=True, ge=1, le=100)

class AutoPreparationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation_id: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9_.:-]+$")
    source_signature: str = Field(pattern=r"^[a-f0-9]{64}$")
    limits: AutoLimits

import oracledb
from collections.abc import Callable

def auto_call(method: Callable[[int, dict, str], dict], order_id: int, body: dict, user: AdminUser) -> dict:
    try:
        return method(order_id, body, user.username)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    except oracledb.DatabaseError as exc:
        if getattr(exc.args[0], "code", 0) in (54, 60, 30006):
            raise HTTPException(409, "AUTO_PREPARATION_RESOURCE_BUSY_RETRY_SAVED_REQUEST") from exc
        raise

@router.post("/{order_id}/automatic-layout")
def auto_preview(order_id: int, body: AutoLimits,
                 user: AdminUser=Depends(require_permission("customer_order_view")),
                 service: PreparationPort=Depends(preparation_service)) -> dict:
    return auto_call(service.auto_preview, order_id, body.model_dump(mode="json"), user)

@router.post("/{order_id}/prepare-st/automatic")
def auto_prepare(order_id: int, body: AutoPreparationRequest,
                 user: AdminUser=Depends(require_permission("customer_order_import")),
                 service: PreparationPort=Depends(preparation_service)) -> dict:
    return auto_call(service.auto_prepare, order_id, body.model_dump(mode="json"), user)

@router.post("/{order_id}/prepare-st/automatic/resolve")
def auto_resolve(order_id: int, body: AutoPreparationRequest,
                 user: AdminUser=Depends(require_permission("customer_order_import")),
                 service: PreparationPort=Depends(preparation_service)) -> dict:
    return auto_call(service.auto_resolve, order_id, body.model_dump(mode="json"), user)
