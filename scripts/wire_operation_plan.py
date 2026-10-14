from pathlib import Path
p=Path("api/wms_api_server/app/modules/transport/public.py")
s=p.read_text(encoding="utf-8-sig")+"\nfrom .infrastructure.operation_plan import generate_existing_operations\n"
p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/services/transport_service.py");s=p.read_text(encoding="utf-8-sig")
start=s.index("    def plan_operations(");end=s.index("    def get_operations(",start)
s=s[:start]+'''    def plan_operations(self, task_id: int, user_id: str) -> list[dict[str,Any]]:
        from ..modules.transport.public import generate_existing_operations,TransportPlanError
        try:
            result=generate_existing_operations(self.gateway,task_id,user_id)
        except TransportPlanError as exc:
            raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc
        _clear_vehicle_availability_cache()
        return result

'''+s[end:];p.write_text(s,encoding="utf-8")
p=Path("api/wms_api_server/app/routers/transport.py");s=p.read_text(encoding="utf-8-sig")
s=s.replace("return TransportService().plan_operations(task_id)","return TransportService().plan_operations(task_id, _user.username)")
p.write_text(s,encoding="utf-8")
