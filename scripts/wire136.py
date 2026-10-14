from pathlib import Path
import json
out={}
p=Path('api/wms_api_server/app/modules/transport/infrastructure/st_assignment.py');s=p.read_text(encoding='utf-8-sig')
begin=s.index('def assign_sts(');end=s.index('\n\ndef unassign_st(',begin)
s=s[:begin]+"""def assign_sts(gateway: OracleGateway, task_id: int, st_numbers: list[str], actor: str) -> dict:
    from .plan_application import assign_validated_sts
    return assign_validated_sts(gateway,task_id,st_numbers,actor)
"""+s[end:]
out[str(p)]=s
p=Path('api/wms_api_server/app/modules/transport/public.py');s=p.read_text(encoding='utf-8-sig')+'\nfrom .infrastructure.plan_application import apply_existing_plan,TransportPlanError\n';out[str(p)]=s
p=Path('api/wms_api_server/app/services/transport_service.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace('result = assign_sts(self.gateway, task_id, st_numbers)', 'result = assign_sts(self.gateway, task_id, st_numbers,user_id)')
s=s.replace('        from ..modules.transport.public import assign_sts\n', '        from ..modules.transport.public import assign_sts,TransportPlanError\n')
needle='        except ValueError as exc:\n            raise HTTPException(status_code=409, detail=str(exc)) from exc\n        _clear_available_sts_cache()'
replacement='        except TransportPlanError as exc:\n            raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc\n'+needle
# Replace only the first matching assign block; other unassign/cancel don't import new exception.
assert needle in s;s=s.replace(needle,replacement,1)
begin=s.index('    def apply_vrp_plan(');end=s.index('    def get_plan_metrics(',begin)
s=s[:begin]+"""    def apply_vrp_plan(self, plan_id: int, shipment_date: date, dock: str | None, user_id: str) -> dict[str, Any]:
        from ..modules.transport.public import apply_existing_plan,TransportPlanError
        try:
            result=apply_existing_plan(self.gateway,plan_id,shipment_date,dock,user_id)
        except TransportPlanError as exc:
            raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc
        _clear_available_sts_cache()
        for trip in result["created_task_ids"]:_clear_task_sts_cache(trip)
        return result

"""+s[end:]
out[str(p)]=s
p=Path('api/wms_api_server/app/routers/transport.py');s=p.read_text(encoding='utf-8-sig')
needle='        plan_id=body.plan_id,\n        shipment_date=body.shipment_date,\n        dock=body.dock,\n'
assert needle in s;s=s.replace(needle,needle+'        user_id=_user.username,\n',1)
out[str(p)]=s
p=Path('api/wms_api_server/app/schemas.py');s=p.read_text(encoding='utf-8-sig')
start=s.index('class VrpApplyRequest(');end=s.index('\n\n',start)
block=s[start:end].replace('Field(..., description="ID плана', 'Field(..., strict=True,gt=0,description="ID плана').replace('dock: str | None = None', 'dock: str | None = Field(default=None,max_length=100)')
s=s[:start]+block+s[end:];out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
