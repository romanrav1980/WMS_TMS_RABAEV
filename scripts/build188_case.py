from pathlib import Path
import json,hashlib
out={};f=Path("db/migrations/2026-10-11_ni042_scale_use")
p=f/"001_use.sql";text=p.read_text(encoding="utf-8")
text=text.replace("declare n number;d json_object_t;k varchar2(64);","declare d json_object_t;wire clob;command_value varchar2(50);state_value varchar2(20);")
text=text.replace(" select CANONICAL_REQUEST into k from RRL_STOCK_OPERATION where 1=0;\nexception when no_data_found then\n declare wire clob;command_value varchar2(50);state_value varchar2(20);begin\n","")
text=text.replace("\n end;\nend;\n/\n","\nend;\n/\n")
out[str(p)]=text
old=(f/"000_before_case.sql").read_text(encoding="utf-8");spec,body=old.split("create or replace package body",1)
out[str(f/"002_case_contract.sql")]=spec
body="create or replace package body"+body
a="  RRL_CASE_WEIGHT_SCAN.assert_scan(p_request,l.ARTICUL,line_id,nvl(l.PICKED_QTY,0));"
assert body.count(a)==1
body=body.replace(a,a+"\n  RRL_CASE_SCALE_ADMISSION.assert_capture(p_request,nvl(l.PICKED_QTY,0));\n  if m.has('warehouse_scale_capture')then RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','WH.SCALE.USE:'||m.get_string('warehouse_scale_capture'));end if;")
a="  RRL_CASE_WEIGHT_SCAN.assert_scan(p_request,article,line_id,before_qty);"
assert body.count(a)==1
body=body.replace(a,a+"\n  RRL_CASE_SCALE_ADMISSION.claim_capture(p_request,p_operation,before_qty);")
out[str(f/"002_case_body.sql")]=body
out[str(f/"apply.sql")]="@@001_use.sql\n@@002_case_contract.sql\n@@002_case_body.sql\n"
out[str(f/"rollback.sql")]="""declare n number;begin select count(*)into n from RRL_WH_SCALE_USE;if n>0 then raise_application_error(-20863,'WAREHOUSE_SCALE_USE_HISTORY_REQUIRES_FORWARD_REPAIR');end if;end;
/
@@000_before_case.sql
drop trigger RRL_WH_SCALE_USE_GUARD;
drop package RRL_CASE_SCALE_ADMISSION;
drop table RRL_WH_SCALE_USE;
"""
out[str(f/"checkpoint.json")]=json.dumps({"migration_id":"2026-10-11-188-case-scale-consumption","before_sha256":hashlib.sha256(old.encode()).hexdigest(),"recovery":"Fresh original CASE contract; additive empty use table rollback; retained use history forward repair; no DB copy"},indent=2)
p=Path("api/wms_api_server/app/modules/inventory/contracts_weighted_case.py")
text=p.read_text(encoding="utf-8").replace("    weighted_box_barcode:","    warehouse_scale_capture: str | None = Field(default=None, pattern=r\"^[A-F0-9]{64}$\")\n    weighted_box_barcode:")
out[str(p)]=text
p=Path("api/wms_api_server/app/modules/inventory/infrastructure/weighted_case_pick.py");text=p.read_text(encoding="utf-8").replace('model_dump(mode="json")','model_dump(mode="json", exclude_none=True)')
text=text.replace("    return metadata, (key,)","    if request.warehouse_scale_capture is not None:\n        metadata[\"warehouse_scale_capture\"] = request.warehouse_scale_capture\n    return metadata, (key,)")
out[str(p)]=text
print(json.dumps(out,ensure_ascii=True))
