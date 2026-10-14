from datetime import date
from decimal import Decimal
from typing import Any
from fastapi import APIRouter,Depends,HTTPException,Path
from pydantic import BaseModel,ConfigDict,Field,model_validator
from ...platform.public import AdminUser,require_permission
from ..contracts_slotting import SlottingDemandPort,SlottingError,slotting_demand_service

class FaceTravelCost(BaseModel):
    model_config=ConfigDict(extra="forbid")
    pick_face_id: int=Field(gt=0)
    pick_seconds_per_base: Decimal=Field(ge=0,max_digits=20,decimal_places=6)
    replenish_seconds_per_pallet: Decimal=Field(ge=0,max_digits=20,decimal_places=6)
    basis: str=Field(min_length=8,max_length=200)

class SlottingScenarioInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    period_from: date
    period_to_exclusive: date
    declared_period_forecast: Decimal|None=Field(default=None,ge=0,max_digits=30,decimal_places=6)
    forecast_base_uom: str|None=Field(default=None,min_length=1,max_length=20)
    declared_pallet_gross_weight_kg: Decimal|None=Field(default=None,gt=0,max_digits=20,decimal_places=6)
    candidate_pick_route_id: int|None=Field(default=None,gt=0)
    recommendation_costs: list[FaceTravelCost]=Field(default_factory=list,max_length=100)
    @model_validator(mode="after")
    def bounded_period(self) -> "SlottingScenarioInput":
        if not 1<=(self.period_to_exclusive-self.period_from).days<=31:
            raise ValueError("Positive horizon at most31 calendar days")
        if self.declared_period_forecast is not None and self.forecast_base_uom is None:
            raise ValueError("Forecast BASE unit required")
        if len({row.pick_face_id for row in self.recommendation_costs})!=len(self.recommendation_costs):
            raise ValueError("Duplicate face cost")
        return self

router=APIRouter(prefix="/api/inventory/slotting",tags=["warehouse-slotting"])

@router.post("/warehouses/{ware_id}/articles/{article}/scenario")
def preview(request: SlottingScenarioInput,ware_id: int=Path(gt=0),article: str=Path(min_length=1,max_length=40),
            user: AdminUser=Depends(require_permission("pick_topology_view")),service: SlottingDemandPort=Depends(slotting_demand_service)) -> dict[str,Any]:
    try:return service.preview(ware_id,article.strip().upper(),request.period_from,request.period_to_exclusive,
        request.declared_period_forecast,request.forecast_base_uom,user.username,request.declared_pallet_gross_weight_kg,
        [row.model_dump(mode="json")for row in request.recommendation_costs],request.candidate_pick_route_id)
    except SlottingError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)}) from exc
