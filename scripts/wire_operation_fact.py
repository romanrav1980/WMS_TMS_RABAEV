from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/transport/public.py")
out[str(p)]=p.read_text(encoding="utf-8-sig")+"\nfrom .infrastructure.operation_fact import update_existing_operation_fact\n"
p=Path("api/wms_api_server/app/services/transport_service.py");s=p.read_text(encoding="utf-8-sig")
start=s.index("    def update_operation_fact(");end=s.index("    def get_vehicles_gantt(",start)
s=s[:start]+'''    def update_operation_fact(self, op_id: int, data: OperationFactUpdate, user_id: str) -> dict[str,Any]:
        from ..modules.transport.public import update_existing_operation_fact,TransportPlanError
        fields=data.model_dump(exclude_none=True,mode="json")
        if not fields:raise HTTPException(status_code=400,detail="Нет полей для обновления")
        try:
            result=update_existing_operation_fact(self.gateway,op_id,fields,user_id)
        except TransportPlanError as exc:
            raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc
        _clear_vehicle_availability_cache()
        return result

'''+s[end:];out[str(p)]=s
p=Path("api/wms_api_server/app/routers/transport.py")
out[str(p)]=p.read_text(encoding="utf-8-sig").replace("return TransportService().update_operation_fact(op_id, data)","return TransportService().update_operation_fact(op_id, data, _user.username)")
print(json.dumps(out,ensure_ascii=True))
