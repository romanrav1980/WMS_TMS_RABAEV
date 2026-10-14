"""Versioned settings for warehouse/store/load-place QC policies."""
from decimal import Decimal
from typing import Any, Literal
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, ConfigDict, Field
from ...platform.public import AdminUser, require_permission
from ..contracts_quality_scope import QualityScopeError, QualityScopePort, quality_scope_service

class QualityScopeInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    expected_version: int=Field(ge=0)
    store_addr: str=Field(min_length=1,max_length=255)
    place_category: Literal["ANY","STOCK","CASE"]
    active: bool=True
    control_mode: Literal["NONE","ANY","SCAN","WEIGHT","BOTH"]
    independent: bool
    sample_percent: Decimal=Field(ge=0,le=100,max_digits=5,decimal_places=2)
    exempt_whole: bool=False
    exempt_storage: bool=False
    reason: str=Field(min_length=8,max_length=1000)

router=APIRouter(prefix="/api/inventory/quality-policies/warehouses/{warehouse}",tags=["outgoing-quality"])

@router.get("")
def read(warehouse: int=Path(gt=0),store_addr: str=Query(default="*",min_length=1,max_length=255),
         place_category: Literal["ANY","STOCK","CASE"]="ANY",
         user: AdminUser=Depends(require_permission("warehouse_settings_view")),
         service: QualityScopePort=Depends(quality_scope_service)) -> dict[str,Any]:
    try:return service.read(warehouse,user.username,store_addr,place_category)
    except QualityScopeError as exc:raise HTTPException(exc.status,str(exc)) from exc

@router.post("")
def save(body: QualityScopeInput,warehouse: int=Path(gt=0),
         user: AdminUser=Depends(require_permission("warehouse_settings_edit")),
         service: QualityScopePort=Depends(quality_scope_service)) -> dict[str,Any]:
    try:return service.save(warehouse,user.username,body.model_dump(mode="json"))
    except QualityScopeError as exc:raise HTTPException(exc.status,{"code":str(exc),"outcome_confirmed":True}) from exc
