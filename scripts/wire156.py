import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/inventory/contracts_slotting.py");s=p.read_text(encoding="utf-8")
s=s.replace("forecast_unit: str|None,actor: str) -> dict[str,Any]", "forecast_unit: str|None,actor: str,pallet_weight: Decimal|None=None,costs: list[dict[str,Any]]|None=None) -> dict[str,Any]")
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/slotting_demand_reader.py");s=p.read_text(encoding="utf-8")
s=s.replace("from .slotting_layout import range_capacity","from .slotting_layout import range_capacity\nfrom .slotting_candidates import recommendation_sources")
s=s.replace("forecast_unit: str|None,actor: str) -> dict[str,Any]", "forecast_unit: str|None,actor: str,pallet_weight: Decimal|None=None,costs: list[dict[str,Any]]|None=None) -> dict[str,Any]")
s=s.replace('                    layout=range_capacity(cur,ware,article,scenario["nominal_additional_quantity"])','                    layout=range_capacity(cur,ware,article,scenario["nominal_additional_quantity"])\n                    recommendation=recommendation_sources(cur,ware,article,scenario,layout,pallet_weight,costs or [])')
s=s.replace('"existing_range":layout}', '"existing_range":layout,"range_recommendation":recommendation}')
s=s.replace('"scenario":scenario,"existing_range":layout,','"scenario":scenario,"existing_range":layout,"range_recommendation":recommendation,')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/slotting_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace("class SlottingScenarioInput(BaseModel):",'''class FaceTravelCost(BaseModel):
    model_config=ConfigDict(extra="forbid")
    pick_face_id: int=Field(gt=0)
    pick_seconds_per_base: Decimal=Field(ge=0,max_digits=20,decimal_places=6)
    replenish_seconds_per_pallet: Decimal=Field(ge=0,max_digits=20,decimal_places=6)
    basis: str=Field(min_length=8,max_length=200)

class SlottingScenarioInput(BaseModel):''')
s=s.replace('    @model_validator(mode="after")','    declared_pallet_gross_weight_kg: Decimal|None=Field(default=None,gt=0,max_digits=20,decimal_places=6)\n    recommendation_costs: list[FaceTravelCost]=Field(default_factory=list,max_length=100)\n    @model_validator(mode="after")',1)
s=s.replace('        return self','        if len({row.pick_face_id for row in self.recommendation_costs})!=len(self.recommendation_costs):\n            raise ValueError("Duplicate face cost")\n        return self',1)
s=s.replace('request.declared_period_forecast,request.forecast_base_uom,user.username)', 'request.declared_period_forecast,request.forecast_base_uom,user.username,request.declared_pallet_gross_weight_kg,\n        [row.model_dump(mode="json")for row in request.recommendation_costs])')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/slotting_candidates.py");s=p.read_text(encoding="utf-8")
s=s.replace("'TM9')","'TM9',q'[NLS_NUMERIC_CHARACTERS='.,']')")
out[str(p)]=s
print(json.dumps(out))
