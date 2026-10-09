import json
from pathlib import Path
D=Path("db/migrations/2026-10-08_stock_posting_core");out={}
p=D/"068_shipping.sql";s=p.read_text(encoding="utf-8")
s=s.replace("accessible by(package RRL_STOCK_POSTING_API)","accessible by(package RRL_STOCK_PALLET_QC_CMD,package RRL_STOCK_POSTING_API)",1);out[str(p)]=s
p=D/"024_posting.sql";s=p.read_text(encoding="utf-8")
s=s.replace("elsif g_kind='CASE_SHORT_APPROVE' then RRL_STOCK_CASE_SHORT_CMD.compile_command","elsif g_kind='OUTGOING_PALLET_CHECK' then RRL_STOCK_PALLET_QC_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   elsif g_kind='CASE_SHORT_APPROVE' then RRL_STOCK_CASE_SHORT_CMD.compile_command",1)
s=s.replace("elsif g_kind='CASE_SHORT_APPROVE' then RRL_STOCK_CASE_SHORT_CMD.execute_command","elsif g_kind='OUTGOING_PALLET_CHECK' then RRL_STOCK_PALLET_QC_CMD.execute_command(g_request,g_actor,p_result);\n   elsif g_kind='CASE_SHORT_APPROVE' then RRL_STOCK_CASE_SHORT_CMD.execute_command",1);out[str(p)]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8")
s=s.replace('"CASE_SHORT_APPROVE",','"OUTGOING_PALLET_CHECK", "CASE_SHORT_APPROVE",',1);out[str(p)]=s
m=json.loads((D/"current_runtime_manifest.json").read_text(encoding="utf-8"))
for component,package in (("183_pallet_quality_command.sql","RRL_STOCK_PALLET_QC_CMD"),("184_quality_entry.sql","RRL_STOCK_QUALITY_ENTRY")):
 if component not in m["components"]:m["components"].insert(m["components"].index("024_posting.sql"),component)
 if package not in m["packages"]:m["packages"].append(package)
if "180_remains_adapter.sql" not in m["additional_scripts"]:m["additional_scripts"].append("180_remains_adapter.sql")
out[str(D/"current_runtime_manifest.json")]=json.dumps(m,indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
