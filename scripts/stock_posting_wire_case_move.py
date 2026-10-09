"""Expose the carrier snapshot reader and add its fixed move handler."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];files={}
def edit(path,old,new):
 text=files.get(path,(ROOT/path).read_text(encoding="utf-8"))
 if text.count(old)!=(2 if old==" procedure compile_command(" else 1):raise RuntimeError("Missing anchor "+path+" "+old[:30])
 files[path]=text.replace(old,new,1)
path="db/migrations/2026-10-08_stock_posting_core/160_case_pick_command.sql"
edit(path,"accessible by(package RRL_STOCK_POSTING_API) as","accessible by(package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_POSTING_API) as")
edit(path," procedure compile_command("," function carrier_rows(p_task number) return clob;\n procedure compile_command(")
path="db/migrations/2026-10-08_stock_posting_core/032_transfer_core.sql"
edit(path,"accessible by(package RRL_STOCK_CASE_PICK_CMD,","accessible by(package RRL_STOCK_CASE_MOVE_CMD,package RRL_STOCK_CASE_PICK_CMD,")
edit(path,"  elsif p_location_mode='PUTAWAY' then","""  elsif p_location_mode='CASE_EXIT' then
   if p_from!='CPT_'||RRL_STOCK_PLAN_HELPER.decimal_text(nvl(p_source_warehouse,p_warehouse)) then raise_application_error(-20886,'CASE_TRANSIT_SOURCE_REQUIRED');end if;
   RRL_STOCK_LOCATION_CORE.assert_quarantine(p_from,nvl(p_source_warehouse,p_warehouse));
   RRL_STOCK_LOCATION_CORE.assert_ordinary(p_to,p_warehouse,'TARGET');
  elsif p_location_mode='PUTAWAY' then""")
path="db/migrations/2026-10-08_stock_posting_core/024_posting.sql"
edit(path,"elsif g_kind='CASE_PICK_CONFIRM' then RRL_STOCK_CASE_PICK_CMD.compile_command",
 "elsif g_kind='CASE_CARRIER_MOVE' then RRL_STOCK_CASE_MOVE_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   elsif g_kind='CASE_PICK_CONFIRM' then RRL_STOCK_CASE_PICK_CMD.compile_command")
edit(path,"elsif g_kind='CASE_PICK_CONFIRM' then RRL_STOCK_CASE_PICK_CMD.execute_command",
 "elsif g_kind='CASE_CARRIER_MOVE' then RRL_STOCK_CASE_MOVE_CMD.execute_command(g_request,g_actor,p_result);\n   elsif g_kind='CASE_PICK_CONFIRM' then RRL_STOCK_CASE_PICK_CMD.execute_command")
path="api/wms_api_server/app/modules/inventory/contracts_stock.py"
edit(path,'{"CASE_PICK_CONFIRM",','{"CASE_CARRIER_MOVE", "CASE_PICK_CONFIRM",')
print(json.dumps(files,ensure_ascii=True))
