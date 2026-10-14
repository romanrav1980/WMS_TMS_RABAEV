from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/integrations/infrastructure/supply_orders.py")
s=p.read_text(encoding="utf-8");start=s.index("    def list(self, warehouse_id:")
s=s[:start]+'''    def list(self, warehouse_id: int | None, limit: int, actor: str) -> list[dict]:
        from .supply_reads import list_supplies
        return list_supplies(self.gateway, warehouse_id, limit, actor)

    def by_receipt_document(self, document_id: int, actor: str) -> dict:
        from .supply_reads import supply_detail
        return supply_detail(self.gateway, None, document_id, actor)

    def get(self, order_id: str, actor: str) -> dict:
        from .supply_reads import supply_detail
        return supply_detail(self.gateway, order_id, None, actor)
'''
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/integrations/application/receipt_ports.py");s=p.read_text(encoding="utf-8")
s=s.replace('def list(self, warehouse_id: int | None, limit: int = 100)','def list(self, warehouse_id: int | None, limit: int, actor: str)')
s=s.replace('def get(self, order_id: str)','def get(self, order_id: str, actor: str)')
s=s.replace('def by_receipt_document(self, document_id: int)','def by_receipt_document(self, document_id: int, actor: str)')
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/integrations/api/supply_routes.py");s=p.read_text(encoding="utf-8")
s=s.replace('    return service.list(warehouse_id, limit)','''    try:
        return service.list(warehouse_id, limit, user.username)
    except PermissionError as exc:
        raise HTTPException(403, str(exc)) from exc''')
s=s.replace('service.by_receipt_document(document_id)','service.by_receipt_document(document_id, user.username)').replace('service.get(order_id)','service.get(order_id, user.username)')
s=s.replace('    except LookupError as exc:', '    except PermissionError as exc:\n        raise HTTPException(403, str(exc)) from exc\n    except LookupError as exc:')
# Detail line bound/input conflict has explicit handler too.
s+='''    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
'''
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
