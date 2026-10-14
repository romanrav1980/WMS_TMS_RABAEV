from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/contracts_warehouse_scale.py");s=p.read_text(encoding="utf-8")
at=s.index("\n\nclass WarehouseScalePort")
new="""

class WarehouseFinalScalePacket(BaseModel):
    model_config = ConfigDict(extra="forbid")
    device_id: str = Field(strict=True,min_length=1,max_length=100)
    capture_id: str = Field(strict=True,min_length=1,max_length=100)
    post_cell: str = Field(strict=True,min_length=1,max_length=60)
    case_task_id: int = Field(strict=True,ge=1)
    expected_content_version: int = Field(strict=True,ge=0)
    scan_container: str = Field(strict=True,min_length=1,max_length=150)
    purpose: Literal["EMPTY_TARE","FINAL_GROSS"]
    tare_capture_key: str|None = Field(default=None,pattern=r"^[A-F0-9]{64}$")
    device_policy_version: int = Field(strict=True,ge=1)
    calibration_ref: str = Field(strict=True,min_length=1,max_length=100)
    unit: Literal["KG"]
    basis: Literal["GROSS"]
    preset_tare_kg: Literal["0"]
    zero_confirmed: bool = Field(strict=True)
    zero_check_kg: str = Field(strict=True,pattern=r"^-?[0-9]{1,18}(\\.[0-9]{1,9})?$")
    zero_check_at: str = Field(strict=True,pattern=UTC_PATTERN)
    measured_at: str = Field(strict=True,pattern=UTC_PATTERN)
    samples: list[WarehouseScaleSample] = Field(min_length=5,max_length=25)
"""
s=s[:at]+new+s[at:];s=s.replace("body: WarehouseScalePacket, actor:", "body: WarehouseScalePacket|WarehouseFinalScalePacket, actor:")
needle="    def reading(self, key: str, actor: str) -> dict[str, Any]: ..."
s=s.replace(needle,needle+"\n    def final_readings(self, task: int, actor: str) -> dict[str, Any]: ...");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/warehouse_scales.py");s=p.read_text(encoding="utf-8").replace("WarehouseScaleConfiguration, WarehouseScalePacket","WarehouseScaleConfiguration, WarehouseScalePacket, WarehouseFinalScalePacket")
s=s.replace("body: WarehouseScalePacket, actor:","body: WarehouseScalePacket|WarehouseFinalScalePacket, actor:")
s=s.replace("body.model_dump(), ensure_ascii=True","body.model_dump(exclude_none=True), ensure_ascii=True")
s=s.replace('                inp, out = q.var(oracledb.DB_TYPE_CLOB), q.var(oracledb.DB_TYPE_CLOB)\n                inp.setvalue(0, wire)\n                q.callproc("RRL_WH_SCALE_API.capture", [inp, actor, out])','                out = q.var(oracledb.DB_TYPE_CLOB)\n                q.callproc("RRL_WH_SCALE_API.capture", [wire, actor, out])')
s=s.replace("where CASE_PICK_TASK_ID=:p_task and CASE_PICK_LINE_ID=:p_line", "where CASE_PICK_TASK_ID=:p_task and CASE_PICK_LINE_ID=:p_line and CAPTURE_PURPOSE='PICK'")
s+="""

    def final_readings(self,task:int,actor:str)->dict[str,Any]:
        try:
            with self.gateway.transaction("Whole CASE final scale archive scoped READ ONLY")as q:
                q.execute("set transaction read only")
                q.callproc("RRL_CASE_TASK_ACCESS.assert_scope",[task,actor,"case_pick_execute"])
                q.execute("select RESULT_JSON from RRL_WH_SCALE_CAPTURE where CASE_PICK_TASK_ID=:task and CAPTURE_PURPOSE in('EMPTY_TARE','FINAL_GROSS') order by RECEIVED_AT desc,CAPTURE_KEY desc fetch first 51 rows only",task=task)
                rows=q.fetchall()
                return {"items":[read_oracle_json(row[0])for row in rows[:50]],"has_older":len(rows)>50}
        except oracledb.DatabaseError as exc:raise scale_error(exc)from exc
"""
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/warehouse_scale_routes.py");s=p.read_text(encoding="utf-8").replace("WarehouseScaleConfiguration, WarehouseScalePacket, WarehouseScalePort,","WarehouseScaleConfiguration, WarehouseScalePacket, WarehouseFinalScalePacket, WarehouseScalePort,")
s+="""

@router.post("/final-captures")
def final_capture(body:WarehouseFinalScalePacket,user:AdminUser=Depends(require_permission("warehouse_scale_ingest")),
                  service:WarehouseScalePort=Depends(warehouse_scale_service))->dict[str,Any]:
    try:return service.capture(body,user.username)
    except WarehouseScaleError as exc:
        error=failure(exc);error.detail.update(device_id=body.device_id,capture_id=body.capture_id);raise error from exc

@router.get("/final-captures")
def final_readings(task:int=Query(ge=1),user:AdminUser=Depends(require_permission("case_pick_execute")),
                   service:WarehouseScalePort=Depends(warehouse_scale_service))->dict[str,Any]:
    try:return service.final_readings(task,user.username)
    except WarehouseScaleError as exc:raise failure(exc)from exc
"""
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
