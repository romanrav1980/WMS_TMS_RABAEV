from pathlib import Path
import json
d=Path("db/migrations/2026-10-11_ni061_loss_recovery");out={}
s=(d/"000_before_rrl_stock_posting_api_package_body.sql").read_text(encoding="utf-8")
needle="  if g_kind in('INTERWARE_SHORTAGE_REPORT','INTERWARE_SHORTAGE_CONFIRM')then RRL_STOCK_INTERWARE_SHORT_CMD.assert_scope"
assert s.count(needle)==2
s=s.replace(needle,"  if g_kind in('INTERWARE_RECOVERY_REPORT','INTERWARE_RECOVERY_APPROVE')then RRL_STOCK_IW_RECOVERY_PLAN.assert_scope(p_request,p_actor);end if;\n"+needle)
s=s.replace("   if g_kind in('INTERWARE_SHORTAGE_REPORT','INTERWARE_SHORTAGE_CONFIRM')then","   if g_kind in('INTERWARE_RECOVERY_REPORT','INTERWARE_RECOVERY_APPROVE')then RRL_STOCK_IW_RECOVERY_PLAN.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   elsif g_kind in('INTERWARE_SHORTAGE_REPORT','INTERWARE_SHORTAGE_CONFIRM')then",1)
s=s.replace("  elsif g_kind in('INTERWARE_SHORTAGE_REPORT','INTERWARE_SHORTAGE_CONFIRM')then RRL_STOCK_INTERWARE_SHORT_CMD.execute_command","  elsif g_kind in('INTERWARE_RECOVERY_REPORT','INTERWARE_RECOVERY_APPROVE')then RRL_STOCK_IW_RECOVERY_PLAN.execute_command(g_request,g_actor,p_result);\n  elsif g_kind in('INTERWARE_SHORTAGE_REPORT','INTERWARE_SHORTAGE_CONFIRM')then RRL_STOCK_INTERWARE_SHORT_CMD.execute_command",1)
out[(d/"004_decision_root_body.sql").as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8").replace('{"INTERWARE_SHORTAGE_REPORT",','{"INTERWARE_RECOVERY_REPORT","INTERWARE_RECOVERY_APPROVE","INTERWARE_SHORTAGE_REPORT",',1);out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
