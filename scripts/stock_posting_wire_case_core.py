"""Add fixed CASE confirmation to the existing posting coordinator."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];files={}
def edit(path,old,new):
 text=files.get(path,(ROOT/path).read_text(encoding="utf-8"))
 if text.count(old)!=1:raise RuntimeError("Missing unique anchor "+path)
 files[path]=text.replace(old,new,1)
path="db/migrations/2026-10-08_stock_posting_core/032_transfer_core.sql"
edit(path,"accessible by(package RRL_STOCK_INTERNAL_CMD,","accessible by(package RRL_STOCK_CASE_PICK_CMD,package RRL_STOCK_INTERNAL_CMD,")
path="db/migrations/2026-10-08_stock_posting_core/024_posting.sql"
edit(path,"elsif g_kind='RECEIPT_REVERSE' then RRL_STOCK_RECEIPT_REVERSE.compile_command",
 "elsif g_kind='CASE_PICK_CONFIRM' then RRL_STOCK_CASE_PICK_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   elsif g_kind='RECEIPT_REVERSE' then RRL_STOCK_RECEIPT_REVERSE.compile_command")
edit(path,"elsif g_kind='RECEIPT_REVERSE' then RRL_STOCK_RECEIPT_REVERSE.execute_command",
 "elsif g_kind='CASE_PICK_CONFIRM' then RRL_STOCK_CASE_PICK_CMD.execute_command(g_request,g_actor,p_result);\n   elsif g_kind='RECEIPT_REVERSE' then RRL_STOCK_RECEIPT_REVERSE.execute_command")
path="api/wms_api_server/app/modules/inventory/contracts_stock.py"
edit(path,'{"RECEIPT_REVERSE",','{"CASE_PICK_CONFIRM", "RECEIPT_REVERSE",')
print(json.dumps(files,ensure_ascii=True))
