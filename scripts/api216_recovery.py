from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/api/tare_assembly_routes.py");s=p.read_text(encoding="utf-8")
cls="""class LoadRecovery(BaseModel):
    model_config=ConfigDict(extra="forbid")
    load_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    original_booking_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    return_offer_operation_id: str=Field(strict=True,min_length=1,max_length=100)
    expected_load_version: int=Field(strict=True,ge=0)
    scan_place: str=Field(strict=True,min_length=1,max_length=200)

"""
s=s.replace("class Book(BaseModel):",cls+"class Book(BaseModel):",1).replace('    expected_warehouse_id: int|None','    load_recovery: LoadRecovery|None=None\n    expected_warehouse_id: int|None',1)
s=s.replace('    return command(service,"TARE_BOOK",','    if body.load_recovery is not None:metadata["load_recovery"]=body.load_recovery.model_dump()\n    return command(service,"TARE_BOOK",',1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
