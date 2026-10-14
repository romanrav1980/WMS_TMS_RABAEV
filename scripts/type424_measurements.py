from pathlib import Path
import json
p=Path('api/wms_api_server/app/modules/inventory/api/interwarehouse_routes.py');t=p.read_text(encoding='utf-8')
addition='''class GroupMeasurements(BaseModel):
    model_config=ConfigDict(extra="forbid")
    origin: Literal["MANUAL_CONFIRMED"]
    content_version: int=Field(strict=True,ge=0)
    gross_weight_kg: Decimal=Field(gt=0,max_digits=18,decimal_places=9)
    width_m: Decimal=Field(gt=0,max_digits=18,decimal_places=9)
    depth_m: Decimal=Field(gt=0,max_digits=18,decimal_places=9)
    height_m: Decimal=Field(gt=0,max_digits=18,decimal_places=9)

'''
t=t.replace('class GroupPlacement(BaseModel):',addition+'class GroupPlacement(BaseModel):',1).replace('    measurements: dict[str,Any]','    measurements: GroupMeasurements',1)
t=t.replace('body.model_dump(exclude={"operation_id","receipt_operation_id"},exclude_none=True)','body.model_dump(mode="json",exclude={"operation_id","receipt_operation_id"},exclude_none=True)',1)
print(json.dumps({p.as_posix():t}))
