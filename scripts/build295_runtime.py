from pathlib import Path
import json
d=Path("db/migrations/2026-10-11_ni061_shortage_disposition");out={}
p=d/"002_command.sql";s=p.read_text(encoding="utf-8")
s=s.replace("n number;reporter varchar2(100);","n number;reporter varchar2(100);v_request varchar2(100);")
s=s.replace("select RECEIPT_OPERATION_ID,ACTOR into rec_id,reporter from RRL_INTERWARE_SHORTAGE_REQUEST where OPERATION_ID=d.get_object('source').get_string('request_operation_id');","v_request:=d.get_object('source').get_string('request_operation_id');select RECEIPT_OPERATION_ID,ACTOR into rec_id,reporter from RRL_INTERWARE_SHORTAGE_REQUEST where OPERATION_ID=v_request;")
s=s.replace("  if json_value(req.SOURCE_JSON,'$.missing_units' returning clob)is not null then null;end if;\n","")
s=s.replace("units clob;\n begin","units clob;domain_wire clob;\n begin")
s=s.replace("units:=v.get_array('missing_units').to_clob;","units:=v.get_array('missing_units').to_clob;domain_wire:=v.to_clob;")
s=s.replace("reason,ref,v.to_clob);","reason,ref,domain_wire);")
out[p.as_posix()]=s
s=(d/"000_before_rrl_stock_posting_api_package_body.sql").read_text(encoding="utf-8")
needle="  if g_kind='INTERWARE_CUSTODY_RELEASE'then"
# Scope occurs before cache and once after locks through prepare path; add explicit new command scope at every custody scope.
s=s.replace(needle,"  if g_kind in('INTERWARE_SHORTAGE_REPORT','INTERWARE_SHORTAGE_CONFIRM')then RRL_STOCK_INTERWARE_SHORT_CMD.assert_scope(p_request,p_actor);end if;\n"+needle)
s=s.replace("   if g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE') then RRL_STOCK_INTERWARE_REC.compile_command","   if g_kind in('INTERWARE_SHORTAGE_REPORT','INTERWARE_SHORTAGE_CONFIRM')then RRL_STOCK_INTERWARE_SHORT_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   elsif g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE') then RRL_STOCK_INTERWARE_REC.compile_command",1)
s=s.replace("  elsif g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE') then RRL_STOCK_INTERWARE_REC.execute_command","  elsif g_kind in('INTERWARE_SHORTAGE_REPORT','INTERWARE_SHORTAGE_CONFIRM')then RRL_STOCK_INTERWARE_SHORT_CMD.execute_command(g_request,g_actor,p_result);\n  elsif g_kind in('INTERWARE_UNLOAD','INTERWARE_RECEIVE') then RRL_STOCK_INTERWARE_REC.execute_command",1)
assert "RRL_STOCK_INTERWARE_SHORT_CMD.execute_command"in s
out[(d/"004_root_body.sql").as_posix()]=s
# Preserve full current UNIT spec/body and restrict mutation of confirmed missing keys under exact UNIT60 lock.
s=Path("db/migrations/2026-10-11_ni061_marked_partial/001_unit_core.sql").read_text(encoding="utf-8")
s=s.replace("procedure own_unit(p_key varchar2) is\n begin","procedure own_unit(p_key varchar2) is n number;\n begin",1)
needle="  if p_key is null then raise_application_error(-20884,'UNIT_BINDING_REQUIRED');end if;"
s=s.replace(needle,needle+"\n  select count(*)into n from RRL_INTERWARE_SHORTAGE_UNIT where PHYSICAL_UNIT_KEY=p_key;if n!=0 then raise_application_error(-20886,'UNIT_CONFIRMED_CARRIER_LOSS_REQUIRES_CORRECTION');end if;",1)
out[(d/"005_unit_core.sql").as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8");s=s.replace('{"STORE_CUSTODY_RELEASE",','{"INTERWARE_SHORTAGE_REPORT","INTERWARE_SHORTAGE_CONFIRM","STORE_CUSTODY_RELEASE",',1);out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
