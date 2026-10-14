from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/infrastructure/warehouse_depot.py");s=p.read_text(encoding="utf-8")
s+="""
    def resolve(self,operation: str,body: dict,actor: str) -> dict:
        request=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=True)
        try:
            with self.gateway.transaction("Await warehouse origin configuration outcome")as cur:
                entered=False
                try:
                    check=cur.var(oracledb.DB_TYPE_CLOB);cur.callproc("RRL_WARE_DEPOT_API.context",[body["warehouse_id"],actor,check])
                    cur.callproc("RRL_STOCK_METADATA_TX.begin_change",[actor,"warehouse_settings_edit"]);entered=True
                    cur.callproc("RRL_WARE_DEPOT_API.context",[body["warehouse_id"],actor,check])
                    cur.execute("select WARE_ID,ACTOR,REQUEST_JSON,RESULT_JSON from RRL_WARE_DEPOT_HISTORY where OPERATION_ID=:operation_id",operation_id=operation)
                    row=cur.fetchone()
                    if row is None:return {"state":"NOT_RECORDED","operation_id":operation,"warehouse_id":body["warehouse_id"],"stock_changed":False}
                    saved=row[2].read()if hasattr(row[2],"read")else str(row[2])
                    if row[0]!=body["warehouse_id"]or row[1]!=actor or saved!=request:
                        from ..contracts_plan import TransportPlanError
                        raise TransportPlanError("WARE_DEPOT_OPERATION_PAYLOAD_CONFLICT","Сохранённая команда отличается от исходной",409)
                    return {"state":"RECORDED","operation_id":operation,"result":read_oracle_json(row[3]),"stock_changed":False}
                finally:
                    if entered:cur.callproc("RRL_STOCK_METADATA_TX.end_change")
        except oracledb.DatabaseError as exc:raise trip_error(exc)from exc
""";out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/contracts_depot.py");s=p.read_text(encoding="utf-8").replace("class WarehouseDepotPort(Protocol):","class WarehouseDepotPort(Protocol):\n    def resolve(self,operation: str,body: dict,actor: str) -> dict: ...");out[str(p)]=s
p=Path("api/wms_api_server/app/modules/transport/api/warehouse_depot_routes.py");s=p.read_text(encoding="utf-8")
s+="""
@router.post("/resolve")
def resolve(body: DepotSetting,user: AdminUser=Depends(require_permission("warehouse_settings_edit")),
            service: WarehouseDepotPort=Depends(warehouse_depot_service)) -> dict:
    try:return service.resolve(body.operation_id,body.model_dump(mode="json",exclude={"operation_id"}),user.username)
    except TransportPlanError as exc:raise HTTPException(exc.status,{"code":exc.code,"message":str(exc)})from exc
""";out[str(p)]=s
p=Path("db/migrations/2026-10-11_ni081_warehouse_depot/rollback.sql");s=p.read_text(encoding="utf-8").replace("@@004_before_time_body.sql\n","");s=s.replace("/\ndrop trigger","/\n@@004_before_time_body.sql\ndrop trigger",1);out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
