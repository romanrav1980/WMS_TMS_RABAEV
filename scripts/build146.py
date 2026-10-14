from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/services/warehouse_task_service.py");text=p.read_text(encoding="utf-8")
start=text.index("    def _complete_task_locked(");end=text.index("    def cancel_task(",start)
text=text[:start]+text[end:]
text=text.replace("from decimal import Decimal\n","").replace("from .warehouse_task_domain_sync_service import WarehouseTaskDomainSyncService\n","")
start=text.index("    def _resource_context(");end=text.index("    def _resource_event_statement(",start)
text=text[:start]+'''    def _resource_context(self, request: WarehouseTaskStatusRequest,
                          task: dict[str, Any], action: str,
                          assignee: str | None = None) -> dict[str, Any]:
        from ..modules.resources.public import existing_task_resource_context
        return existing_task_resource_context(self.gateway, task, action, request, assignee or request.updated_by)

'''+text[end:]
needle="            except (ValueError, LookupError) as exc:"
assert text.count(needle)==1
text=text.replace(needle,"            except PermissionError as exc:\n                raise HTTPException(403, detail=str(exc)) from exc\n"+needle)
out[str(p)]=text
out["api/wms_api_server/app/modules/inventory/infrastructure/receipt_task_access.py"]='''"""Current native task scope shared with normal assignment and physical posting."""
import oracledb

def assert_receipt_task_scope(cursor: oracledb.Cursor,task_id: int,actor: str) -> None:
    try:
        cursor.execute("begin RRL_WAREHOUSE_TASK_ACCESS.assert_scope(:task,:actor);end;",
                       {"task":task_id,"actor":actor})
    except oracledb.DatabaseError as exc:
        if getattr(exc.args[0],"code",None)==20882:
            raise PermissionError("TASK_USER_WAREHOUSE_FORBIDDEN") from exc
        raise
'''
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/receiving.py");text=p.read_text(encoding="utf-8")
text=text.replace("from .metadata_transactions import receipt_task_metadata","from .metadata_transactions import receipt_task_metadata\nfrom .receipt_task_access import assert_receipt_task_scope")
needle="        with receipt_task_metadata(self.gateway, 'Replan incoming pallet destination', actor, 'warehouse_task_assign') as cur:"
assert text.count(needle)==1
text=text.replace(needle,needle+"\n            assert_receipt_task_scope(cur,task_id,actor)")
needle="        with receipt_task_metadata(self.gateway, 'Cancel putaway and release storage reservation', actor, 'warehouse_task_edit') as cur:"
assert text.count(needle)==1
text=text.replace(needle,needle+"\n            assert_receipt_task_scope(cur,task_id,actor)")
needle="            task = cur.fetchone()"
assert text.count(needle)==2
text=text.replace(needle,needle+"\n            assert_receipt_task_scope(cur,task_id,actor)")
text=text.replace("if normalize_incoming_sscc(body['scanned_pallet'])!=task[0] or body['scanned_from_cell']!=task[1]:","if (body['scanned_pallet']!=task[0] and normalize_incoming_sscc(body['scanned_pallet'])!=task[0]) or body['scanned_from_cell']!=task[1]:")
out[str(p)]=text
p=Path("api/wms_api_server/app/modules/inventory/api/receiving_routes.py");text=p.read_text(encoding="utf-8")
start=text.index("def replan_putaway(");end=text.index('@router.post("/supply-orders',start)
segment=text[start:end].replace("    except (LookupError, ValueError) as exc:","    except PermissionError as exc:\n        raise HTTPException(403,str(exc)) from exc\n    except (LookupError, ValueError) as exc:")
text=text[:start]+segment+text[end:]
# Only the replan scanned pallet field is changed; legacy label/source fields retain their own contracts.
start=text.index("class ReplanPutaway(");end=text.index('@router.post("/putaway/',start)
segment=text[start:end].replace("scanned_pallet: str = Field(min_length=1, max_length=25)","scanned_pallet: str = Field(min_length=1, max_length=150)")
out[str(p)]=text[:start]+segment+text[end:]
print(json.dumps(out,ensure_ascii=True))
