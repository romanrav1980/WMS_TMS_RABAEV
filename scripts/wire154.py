import json
from pathlib import Path
p=Path("api/wms_api_server/app/modules/integrations/public.py");s=p.read_text(encoding="utf-8");s+="\nfrom .infrastructure.outbox_delivery import OutboxDelivery\n"
p2=Path("api/wms_api_server/app/services/traceability_service.py");t=p2.read_text(encoding="utf-8")
t=t.replace("        reason: str | None = None,\n    ) -> dict[str, Any]:","        reason: str | None = None,\n        actor: str | None = None,\n    ) -> dict[str, Any]:",1)
start=t.index('        error_note = f"Manual retry requested:');end=t.index("\n    def list_adapter_requests",start)
t=t[:start]+'''        from ..modules.integrations.public import OutboxDelivery
        if actor is None:
            raise HTTPException(status_code=403, detail="Current retry actor required")
        try:
            OutboxDelivery(self.gateway).retry(event_outbox_id, actor, reason)
        except Exception as exc:
            code = getattr(exc.args[0], "code", 0) if exc.args else 0
            if code in (20881,20882,20886):
                raise HTTPException(status_code=403 if code==20882 else 409, detail=str(exc).split("\\n",1)[0]) from exc
            raise
        return {"dry_run": False,"event_outbox_id": event_outbox_id,"updated": 1,"status": "PENDING"}
''' +t[end:]
p3=Path("api/wms_api_server/app/routers/traceability.py");r=p3.read_text(encoding="utf-8").replace("reason=request.reason,","reason=request.reason,\n        actor=user.username,",1)
print(json.dumps({str(p):s,str(p2):t,str(p3):r}))
