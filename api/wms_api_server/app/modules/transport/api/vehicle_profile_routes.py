from typing import Any
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,ConfigDict,Field,model_validator
from ...platform.public import AdminUser,require_permission
from ..contracts_vehicle_profile import VehicleProfileError,VehicleProfilePort,vehicle_profile_service

router=APIRouter(prefix="/api/admin/transport",tags=["existing-fleet-physical-profile"])

class FloorTypeLimit(BaseModel):
    model_config=ConfigDict(extra="forbid")
    pallet_type_id: int=Field(strict=True,gt=0)
    max_places: int=Field(strict=True,ge=1,le=1000)

class FloorLoadingVariant(BaseModel):
    model_config=ConfigDict(extra="forbid")
    code: str=Field(strict=True,pattern=r"^[A-Za-z0-9_.:-]{1,40}$")
    limits: list[FloorTypeLimit]=Field(min_length=1,max_length=8)

    @model_validator(mode="after")
    def unique_types(self) -> "FloorLoadingVariant":
        ids=[limit.pallet_type_id for limit in self.limits]
        if len(ids)!=len(set(ids)):
            raise ValueError("Тип тары повторяется в варианте загрузки")
        return self

class VehicleProfileRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    operation_id: str=Field(strict=True,min_length=1,max_length=100,pattern=r"^[A-Za-z0-9_.:-]+$")
    vehicle_id: int=Field(strict=True,gt=0)
    expected_source_hash: str=Field(strict=True,pattern=r"^[0-9A-F]{64}$")
    vehicle_size_class: str=Field(strict=True,min_length=1,max_length=40)
    cargo_length_mm: int=Field(strict=True,ge=1,le=1000000)
    cargo_width_mm: int=Field(strict=True,ge=1,le=1000000)
    cargo_height_mm: int=Field(strict=True,ge=1,le=1000000)
    expected_version: int=Field(strict=True,ge=0)
    temp_min_c: str | None=Field(default=None,strict=True,pattern=r"^-?[0-9]{1,6}(\.[0-9]{1,3})?$")
    temp_max_c: str | None=Field(default=None,strict=True,pattern=r"^-?[0-9]{1,6}(\.[0-9]{1,3})?$")
    floor_variants: list[FloorLoadingVariant] | None=Field(default=None,min_length=1,max_length=20)
    reason: str=Field(strict=True,min_length=1,max_length=500)
    evidence_reference: str=Field(strict=True,min_length=1,max_length=100)


    @model_validator(mode="after")
    def unique_variants(self) -> "VehicleProfileRequest":
        if "floor_variants" in self.model_fields_set:
            if self.floor_variants is None:
                raise ValueError("Укажите варианты загрузки или исключите поле")
            codes=[variant.code for variant in self.floor_variants]
            if len(codes)!=len(set(codes)):
                raise ValueError("Коды вариантов загрузки должны различаться")
        return self

    @model_validator(mode="after")
    def temperature_pair(self) -> "VehicleProfileRequest":
        from decimal import Decimal
        if ("temp_min_c" in self.model_fields_set) != ("temp_max_c" in self.model_fields_set):
            raise ValueError("Оба температурных предела обязательны")
        if "temp_min_c" in self.model_fields_set:
            if self.temp_min_c is None or self.temp_max_c is None or Decimal(self.temp_min_c)>Decimal(self.temp_max_c):
                raise ValueError("Укажите корректный температурный диапазон")
        return self

def failure(exc: VehicleProfileError,operation: str|None=None)->HTTPException:
    return HTTPException(exc.status,{"code":exc.code,"message":str(exc),"operation_id":operation,"outcome_confirmed":exc.status==409})

@router.post("/vehicle-profiles")
def configure(body: VehicleProfileRequest,user: AdminUser=Depends(require_permission("transport_fleet_edit")),
              service: VehicleProfilePort=Depends(vehicle_profile_service))->dict[str,Any]:
    try:return service.configure(body.model_dump(mode="json",exclude_none=True),user.username)
    except VehicleProfileError as exc:raise failure(exc,body.operation_id)from exc

@router.get("/vehicles/{vehicle_id}/profile")
def read(vehicle_id: int,user: AdminUser=Depends(require_permission("transport_dispatch_view")),
         service: VehicleProfilePort=Depends(vehicle_profile_service))->dict[str,Any]:
    if vehicle_id<1:raise HTTPException(422,"Укажите автомобиль")
    try:return service.read(vehicle_id,user.username)
    except VehicleProfileError as exc:raise failure(exc)from exc


@router.get("/vehicle-profiles/tare-types")
def tare_types(user: AdminUser=Depends(require_permission("transport_dispatch_view")),
               service: VehicleProfilePort=Depends(vehicle_profile_service))->list[dict[str,Any]]:
    try:return service.tare_types(user.username)
    except VehicleProfileError as exc:raise failure(exc)from exc
