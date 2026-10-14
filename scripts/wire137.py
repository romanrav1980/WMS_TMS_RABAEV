from pathlib import Path
import json
out={}
p=Path('api/wms_api_server/app/modules/transport/public.py');out[str(p)]=p.read_text(encoding='utf-8-sig')+'\nfrom .infrastructure.trip_edit import create_existing_trip,update_existing_trip\n'
p=Path('api/wms_api_server/app/services/transport_service.py');s=p.read_text(encoding='utf-8-sig')
start=s.index('    def create_task(self, req: TransportTaskCreateRequest');end=s.index('    def close_task(',start)
s=s[:start]+"""    def create_task(self, req: TransportTaskCreateRequest, user_id: str) -> int:
        from ..modules.transport.public import create_existing_trip,TransportPlanError
        try:return create_existing_trip(self.gateway,_normalize_transtype(req.transtype),req.shipment_date,user_id)
        except TransportPlanError as exc:raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc

    def update_task(self, task_id: int, req: TransportTaskUpdateRequest, user_id: str) -> None:
        from ..modules.transport.public import update_existing_trip,TransportPlanError
        fields=req.model_dump(exclude_none=True,mode="json")
        if "transtype"in fields:fields["transtype"]=_normalize_transtype(fields["transtype"])
        if not fields:return
        try:update_existing_trip(self.gateway,task_id,fields,user_id)
        except TransportPlanError as exc:raise HTTPException(exc.status,detail={"code":exc.code,"message":str(exc)}) from exc

"""+s[end:]
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
