from pathlib import Path
import json
out={}
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/stock_posting_uow.py");s=p.read_text(encoding="utf-8")
start=s.index('                from .birth_capture import plan_births')
end=s.index('        posting_started = True',start)
s=s[:start]+'''                from .birth_capture_commands import prepare_birth_capture
                resolution,birth_captures=prepare_birth_capture(cursor,command_document,operation_id)
'''+s[end:]
s=s.replace("from .birth_capture import stage_births\n                stage_births(cursor,command_document,birth_captures)","from .birth_capture_commands import stage_checked_births\n                stage_checked_births(cursor,command_document,birth_captures)",1)
out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/inventory_observations.py");s=p.read_text(encoding="utf-8")
needle='''        return self.posting.post(StockCommand(operation_id=operation_id,
            command_type="INVENTORY_REGISTER_LOT",actor=actor,lines=(),
            source={"revision_id":revision_id},metadata=metadata))'''
replacement='''        from ..contracts_stock import StockPostingError
        try:
            return self.posting.post(StockCommand(operation_id=operation_id,
                command_type="INVENTORY_REGISTER_LOT",actor=actor,lines=(),
                source={"revision_id":revision_id},metadata=metadata))
        except StockPostingError as exc:
            status=403 if exc.oracle_code==20882 else 409 if exc.oracle_code is not None and 20800<=exc.oracle_code<=20999 else 503
            raise InventoryObservationError(exc.rule_reason or exc.code,status,operation_id) from exc'''
assert needle in s;s=s.replace(needle,replacement,1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/api/inventory_count_routes.py");s=p.read_text(encoding="utf-8")
needle='raise HTTPException(exc.status,detail={"code":exc.code}) from exc'
# Only lot route's final error boundary, not unrelated create-revision behavior.
pos=s.index('@router.post("/inventory/lots")')
tail=s[pos:].replace(needle,'raise HTTPException(exc.status,detail={"code":exc.code,"operation_id":request.operation_id,"outcome_confirmed":exc.status==409}) from exc',1)
out[str(p)]=s[:pos]+tail
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/birth_capture.py");s=p.read_text(encoding="utf-8").replace('"source_doc":source_doc}','"source_doc":source_doc,"actor":document["actor"]}',1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/trace_aggregation_source.py");s=p.read_text(encoding="utf-8")
s=s.replace("source_doc: int,policy_version: int,profiles:","source_doc: int,actor: str,policy_version: int,profiles:",1)
s=s.replace("and m.POLICY_VERSION=:policy","and m.POLICY_VERSION=:policy and exists(select 1 from RUSERS u where u.ID=:actor and nvl(u.DELETED,0)=0 and(u.WARE_ID=m.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN'))",1)
s=s.replace("doc=source_doc,policy=policy_version)","doc=source_doc,policy=policy_version,actor=actor)",1)
out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
