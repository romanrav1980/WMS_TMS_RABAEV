from typing import Any
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field
from ...platform.public import AdminUser,require_permission
from ..contracts import TransportLoadingError
from ..contracts_driver_binding import DriverBindingPort,driver_binding_service

router=APIRouter(prefix="/api/transport/driver-bindings",tags=["authenticated-driver-binding"])


class DriverBindingRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    user_id: str=Field(strict=True,min_length=1,max_length=50)
    active: bool=Field(strict=True)
    expected_version: int=Field(strict=True,ge=0)


@router.put("/{driver_id}")
def configure(driver_id: int,body: DriverBindingRequest,user: AdminUser=Depends(require_permission("warehouse_settings_edit")),
              service: DriverBindingPort=Depends(driver_binding_service)) -> dict[str,Any]:
    if driver_id<1:
        raise HTTPException(422,"Укажите водителя")
    try:
        return service.configure(driver_id,body.user_id,body.active,body.expected_version,user.username)
    except TransportLoadingError as exc:
        raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc


@router.get("/{driver_id}")
def get(driver_id: int,user: AdminUser=Depends(require_permission("warehouse_settings_edit")),
        service: DriverBindingPort=Depends(driver_binding_service)) -> dict[str,Any]:
    return service.get(driver_id)
