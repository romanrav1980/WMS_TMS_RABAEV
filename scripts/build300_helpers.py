from pathlib import Path
import json
d=Path("db/migrations/2026-10-11_ni061_loss_recovery");out={}
for pkg,name in[("RRL_STOCK_BALANCE_CORE","011_balance_spec.sql"),("RRL_STOCK_LOCATION_CORE","012_location_spec.sql"),("RRL_STOCK_INTERWARE_PART","013_part_spec.sql"),("RRL_STOCK_UNIT_CORE","014_unit_spec.sql")]:
 s=(d/("000_before_"+pkg.lower()+"_package.sql")).read_text(encoding="utf-8")
 assert "accessible by("in s;s=s.replace("accessible by(","accessible by(package RRL_STOCK_IW_RECOVERY_REC,",1);out[(d/name).as_posix()]=s
s=(d/"000_before_rrl_stock_unit_core_package_body.sql").read_text(encoding="utf-8")
needle="select count(*)into n from RRL_INTERWARE_SHORTAGE_UNIT where PHYSICAL_UNIT_KEY=p_key;"
assert needle in s
s=s.replace(needle,"""select count(*)into n from RRL_INTERWARE_SHORTAGE_UNIT booked where booked.PHYSICAL_UNIT_KEY=p_key
 and not exists(select 1 from RRL_INTERWARE_RECOVERY_UNIT recovered join RRL_STOCK_OPERATION o on o.OPERATION_ID=recovered.RECOVERY_OPERATION_ID
 where recovered.PHYSICAL_UNIT_KEY=booked.PHYSICAL_UNIT_KEY and recovered.LOSS_OPERATION_ID=booked.FACT_OPERATION_ID
 and o.COMMAND_TYPE='INTERWARE_SHORTAGE_RECOVER'and(o.STATE='APPLIED'or(o.STATE='IN_FLIGHT'and o.OPERATION_ID=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID'))));""",1)
# Exact captured parameter matching retained; only a validated recovery owner may call this method.
s=s.replace("o.COMMAND_TYPE='INTERWARE_RECEIVE'and json_value(o.RESOLVED_PLAN_JSON,'$.domain.partial_receipt')='true'","o.COMMAND_TYPE in('INTERWARE_RECEIVE','INTERWARE_SHORTAGE_RECOVER')and json_value(o.RESOLVED_PLAN_JSON,'$.domain.partial_receipt')='true'",1)
out[(d/"015_unit_body.sql").as_posix()]=s
s=(d/"000_before_rrl_stock_unit_guard.sql").read_text(encoding="utf-8")
needle="select count(*)into v_loss_count from RRL_INTERWARE_SHORTAGE_UNIT where PHYSICAL_UNIT_KEY=:old.PHYSICAL_UNIT_KEY;"
assert needle in s
s=s.replace(needle,"""select count(*)into v_loss_count from RRL_INTERWARE_SHORTAGE_UNIT booked where booked.PHYSICAL_UNIT_KEY=:old.PHYSICAL_UNIT_KEY
 and not exists(select 1 from RRL_INTERWARE_RECOVERY_UNIT recovered join RRL_STOCK_OPERATION operation on operation.OPERATION_ID=recovered.RECOVERY_OPERATION_ID
 where recovered.PHYSICAL_UNIT_KEY=booked.PHYSICAL_UNIT_KEY and recovered.LOSS_OPERATION_ID=booked.FACT_OPERATION_ID
 and operation.COMMAND_TYPE='INTERWARE_SHORTAGE_RECOVER'and(operation.STATE='APPLIED'or(operation.STATE='IN_FLIGHT'and operation.OPERATION_ID=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID'))));""",1)
out[(d/"016_unit_guard.sql").as_posix()]=s
s=Path("db/migrations/2026-10-11_ni061_partial_receiving/007_sap_clone_guard.sql").read_text(encoding="utf-8")
s=s.replace("operation.COMMAND_TYPE='INTERWARE_RECEIVE'","operation.COMMAND_TYPE in('INTERWARE_RECEIVE','INTERWARE_SHORTAGE_RECOVER')",1)
out[(d/"017_pallet_guard.sql").as_posix()]=s
s=(d/"004_decision_root_body.sql").read_text(encoding="utf-8")
needle="  if g_kind in('INTERWARE_RECOVERY_REPORT','INTERWARE_RECOVERY_APPROVE')then RRL_STOCK_IW_RECOVERY_PLAN.assert_scope"
assert s.count(needle)==2
s=s.replace(needle,"  if g_kind='INTERWARE_SHORTAGE_RECOVER'then declare req json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_IW_RECOVERY_REC.assert_scope(req.get_object('source').get_string('approval_operation_id'),p_actor);end;end if;\n"+needle)
s=s.replace("   if g_kind in('INTERWARE_RECOVERY_REPORT','INTERWARE_RECOVERY_APPROVE')then","   if g_kind='INTERWARE_SHORTAGE_RECOVER'then RRL_STOCK_IW_RECOVERY_REC.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   elsif g_kind in('INTERWARE_RECOVERY_REPORT','INTERWARE_RECOVERY_APPROVE')then",1)
s=s.replace("  elsif g_kind in('INTERWARE_RECOVERY_REPORT','INTERWARE_RECOVERY_APPROVE')then RRL_STOCK_IW_RECOVERY_PLAN.execute_command","  elsif g_kind='INTERWARE_SHORTAGE_RECOVER'then RRL_STOCK_IW_RECOVERY_REC.execute_command(g_request,g_actor,p_result);\n  elsif g_kind in('INTERWARE_RECOVERY_REPORT','INTERWARE_RECOVERY_APPROVE')then RRL_STOCK_IW_RECOVERY_PLAN.execute_command",1)
out[(d/"019_receiving_root_body.sql").as_posix()]=s
p=Path("api/wms_api_server/app/modules/inventory/contracts_stock.py");s=p.read_text(encoding="utf-8").replace('{"INTERWARE_RECOVERY_REPORT",','{"INTERWARE_SHORTAGE_RECOVER","INTERWARE_RECOVERY_REPORT",',1);out[p.as_posix()]=s
print(json.dumps(out,ensure_ascii=True))
