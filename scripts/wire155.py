import json
from pathlib import Path
out={}
p=Path("api/wms_api_server/app/modules/integrations/public.py");out[str(p)]=p.read_text(encoding="utf-8")+"\nfrom .infrastructure.outbox_response_journal import OutboxResponseJournal\n"
p=Path("api/wms_api_server/app/services/outbox_service.py");s=p.read_text(encoding="utf-8")
s=s.replace("regulatory_delivery_decision, OutboxDelivery)","regulatory_delivery_decision, OutboxDelivery, OutboxResponseJournal)")
s=s.replace("adapter: RegulatoryAdapter | None = None) -> None:", "adapter: RegulatoryAdapter | None = None,\n                 journal: OutboxResponseJournal | None = None) -> None:")
s=s.replace("self.delivery = OutboxDelivery(self.gateway)","self.delivery = OutboxDelivery(self.gateway)\n        self.journal = journal or OutboxResponseJournal()")
s=s.replace("        if not self.adapter.configured:", "        recovered = self.journal.recover_one(self.delivery, target_system)\n        if recovered is not None:\n            return recovered\n        if not self.adapter.configured:")
s=s.replace("        claim = self.delivery.claim", "        self.journal.ready()\n        claim = self.delivery.claim")
start=s.index("        # Database finalization errors")
s=s[:start]+'''        key = self.journal.save(claim, request_id, str(event.get("target_system") or "INTERNAL"),
                                body, self.adapter.simulated, real_ack)
        saved = self.journal.finalize(key, self.delivery)
        if saved is None:
            return {"event_outbox_id": claim["event_outbox_id"], "adapter_request_id": request_id,
                    "status": "RESPONSE_PENDING", "real_external_ack": False}
        return {**saved, "response_recovered": False}
'''
out[str(p)]=s
print(json.dumps(out))
