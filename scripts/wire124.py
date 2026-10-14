from pathlib import Path
import json
out={}
root=Path("api/wms_api_server/app")
p=root/"modules/inventory/public.py";s=p.read_text(encoding="utf-8")
if "def build_trace_manifest(" not in s:s+='''

from .contracts_trace_manifest import TraceManifestPort,trace_manifest_service
from .api.trace_manifest_routes import router as trace_manifest_router
from .infrastructure.trace_sender_manifest import TraceSenderManifest

def build_trace_manifest(gateway: Any) -> TraceManifestPort:
    return TraceSenderManifest(gateway)
'''
out[str(p)]=s
p=root/"main.py";s=p.read_text(encoding="utf-8")
if "app.include_router(trace_manifest_router)" not in s:s+='''

from .modules.inventory.public import trace_manifest_router,trace_manifest_service
from .trace_manifest_composition import build_trace_manifest_service
app.include_router(trace_manifest_router)
app.dependency_overrides[trace_manifest_service]=build_trace_manifest_service
'''
out[str(p)]=s
p=root/"modules/inventory/infrastructure/receiving_marks.py";s=p.read_text(encoding="utf-8")
s=s.replace("from decimal import Decimal","from decimal import Decimal\nfrom typing import Any\nfrom ...platform.public import read_oracle_json\nfrom .trace_aggregation_source import source_header,aggregation_members,assert_sender_capture,assert_current_mark_policy,persist_scanned_aggregates",1)
s=s.replace("*, lock_policy: bool = True) -> dict:","*, lock_policy: bool = True, birth_context: dict[str,Any]|None = None) -> dict:",1)
s=s.replace("        units, quantities, scanned = {}, {}, []","""        manifest_id=payload.get("manifest_operation_id")
        header=None
        if manifest_id:
            if not birth_context or not payload["aggregations"]:
                raise ValueError("Non-SAP manifest requires an explicit birth source and aggregation scan")
            header=source_header(cur,manifest_id,**birth_context,policy_version=policy[0],profiles=profiles)
        units, quantities, scanned = {}, {}, []""",1)
s=s.replace("json.loads(document) if u['uom']","read_oracle_json(document) if u['uom']")
start=s.index("            digest = sha256(code.encode()).hexdigest()")
end=s.index("                self._quantity(quantities, member['unit_id']",start)
s=s[:start]+'''            for member in aggregation_members(cur,order_id,line_number,profile,code,level,manifest_id):
'''+s[end:]
needle='        return {"policy_version": policy[0], "profiles": profiles, "units": units, "unit_quantities": quantities, "scanned": scanned}'
assert needle in s
s=s.replace(needle,'''        if header:
            assert_sender_capture(header,units,quantities,base_uom)
        return {"policy_version": policy[0], "profiles": profiles, "units": units, "unit_quantities": quantities, "scanned": scanned,"manifest_operation_id":manifest_id}''',1)
s=s.replace("        binding_map = {b[", "        if marks.get('units'):assert_current_mark_policy(cur,pallet,marks)\n        binding_map = {b[",1)
start=s.index("        seen = set()")
end=s.index("    @staticmethod\n    def _quantity",start)
s=s[:start]+'''        persist_scanned_aggregates(cur,pallet,marks["scanned"])

'''+s[end:]
out[str(p)]=s
p=root/"modules/inventory/infrastructure/birth_capture.py";s=p.read_text(encoding="utf-8")
s=s.replace("from decimal import Decimal","from decimal import Decimal\nfrom typing import Any",1)
s=s.replace("def plan_births(cursor, document):","def plan_births(cursor: Any, document: dict[str,Any]) -> tuple[dict[str,Any],dict[str,Any]]:")
s=s.replace("def stage_births(cursor,document,captures):","def stage_births(cursor: Any,document: dict[str,Any],captures: dict[str,Any]) -> None:")
needle='        marks=ReceivingMarks(cursor).resolve("STOCK.BIRTH",article,str(movement_id or ""),qbase,payload,base,lock_policy=False)'
assert needle in s
s=s.replace(needle,'''        source_kind="INVENTORY" if kind=="INVENTORY_REGISTER_LOT" else "MES"
        source_doc=document["source"]["revision_id"] if source_kind=="INVENTORY" else movement_id
        context={"uid":uid,"article":article,"base":base,"cell":cell,"source_kind":source_kind,"source_doc":source_doc}
        marks=ReceivingMarks(cursor).resolve("STOCK.BIRTH",article,str(movement_id or ""),qbase,payload,base,lock_policy=False,birth_context=context)''',1)
s=s.replace('        cursor.execute("begin RRL_STOCK_POSTING_API.finish_birth_capture; end;")','''        if captures[birth["uid"]].get("manifest_operation_id"):
            cursor.execute("insert into RRL_TRACE_MANIFEST_USE(MANIFEST_OPERATION_ID,STOCK_OPERATION_ID,UID_PALLET,ACTOR)values(:manifest_id,:stock_op,:lot_id,:actor)",manifest_id=captures[birth["uid"]]["manifest_operation_id"],stock_op=document["operation_id"],lot_id=birth["uid"],actor=document["actor"])
        cursor.execute("begin RRL_STOCK_POSTING_API.finish_birth_capture; end;")''',1)
out[str(p)]=s
p=root/"modules/inventory/domain/trace_manifest.py";s=p.read_text(encoding="utf-8").replace('quantity=unit_quantity(item["quantity"],document["base_uom"],None)','quantity=unit_quantity(_text(item["quantity"],40),document["base_uom"],None)');out[str(p)]=s
p=root/"modules/inventory/infrastructure/trace_aggregation_source.py";s=p.read_text(encoding="utf-8").replace('m.RAW_JSON,m.PROFILES_JSON,m.DECLARED_BASE_QTY','m.RAW_JSON,m.PROFILES_JSON,to_char(m.DECLARED_BASE_QTY,\'TM9\',\'NLS_NUMERIC_CHARACTERS=\'\'.,\'\'\')');out[str(p)]=s
print(json.dumps(out,ensure_ascii=True))
