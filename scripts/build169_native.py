import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];f=r/"db/migrations/2026-10-10_ni033_wave_defer";out={}
a=(f/"001_access.sql").read_text(encoding="utf-8")
a=a.replace("upper(trim(grp))!='GLOBAL_ADMIN'","nvl(upper(trim(grp)),'-')!='GLOBAL_ADMIN'")
a=a.replace("and (STATUS is null or STATUS not in('DONE','CANCELLED'));\n  if n>0 then deny('WAVE_DEFER_PHYSICAL_TASK_PENDING')",
 "and (STATUS is null or STATUS not in('DONE','CANCELLED') or (STATUS='DONE'and nvl(TASK_TYPE,'-')!='REPLENISHMENT'));\n  if n>0 then deny('WAVE_DEFER_PHYSICAL_TASK_PENDING')")
a=a.replace("if v_count=0 then deny('WAVE_DEFER_ORIGINAL_DEMAND_MISSING');end if;",
 """select count(*)into n from RRL_PICK_WAVE_ORDER wo join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_ID=wo.PICK_PLAN_ID where wo.PICK_WAVE_ID=p_wave;
  if v_count=0 or v_count!=n then deny('WAVE_DEFER_ORIGINAL_DEMAND_MISSING');end if;""")
out[str(f.relative_to(r)/"001_access.sql")]=a
root=(f/"000_before_root.sql").read_text(encoding="utf-8")
needle="if g_kind in('CASE_PICK_CONFIRM','CASE_CARRIER_MOVE','CASE_CARRIER_RETURN','CASE_SHORT_APPROVE')then RRL_CASE_TASK_ACCESS.assert_command(p_request,p_actor);end if;"
assert root.count(needle)==2
root=root.replace(needle,needle+"\n  if g_kind='WAVE_EXECUTION_FINISH'then RRL_WAVE_EXEC_ACCESS.assert_command(p_request,p_actor);end if;")
out[str(f.relative_to(r)/"003_root_contract.sql")]=root
out[str(f.relative_to(r)/"003_root_body.sql")]=root[root.lower().index("create or replace package body"):]
finish=(f/"000_before_finish.sql").read_text(encoding="utf-8")
# private closure includes the explicit deferred decision source, leaving normal native snapshot unchanged
pos=finish.index(" procedure compile_command(",finish.index("create or replace package body"))
finish=finish[:pos]+""" function closure_json(p_wave number,p_disposition varchar2)return clob is
  j json_object_t:=json_object_t.parse(snapshot_json(p_wave));defer json_object_t;
 begin
  if p_disposition='RETURNED_TO_PLANNING'then
   defer:=json_object_t.parse(RRL_WAVE_EXEC_ACCESS.deferred_snapshot_json(p_wave));j.put('deferred_decision',defer);
  elsif p_disposition is not null then raise_application_error(-20881,'WAVE_DISPOSITION_UNSUPPORTED');end if;
  return j.to_clob;
 end;
"""+finish[pos:]
finish=finish.replace("s:=snapshot_json(v_wave);","s:=closure_json(v_wave,d.get_object('metadata').get_string('disposition'));")
needle="  for ff in(select ff.FULFILLMENT_ID from RRL_CUSTOMER_ORDER_FULFILLMENT ff where"
assert finish.count(needle)==1
finish=finish.replace(needle,"""  if d.get_object('metadata').get_string('disposition')='RETURNED_TO_PLANNING'then
   for line in(select pl.PICK_PLAN_LINE_ID,pl.PICK_PLAN_ID,cr.CUSTOMER_ORDER_ROW_ID,cr.CUSTOMER_ORDER_ID
    from RRL_PICK_WAVE_ORDER wo join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_ID=wo.PICK_PLAN_ID
    join RRL_CUSTOMER_ORDER_ROW cr on cr.CUSTOMER_ORDER_ROW_ID=pl.CUSTOMER_ORDER_ROW_ID
    where wo.PICK_WAVE_ID=v_wave order by pl.PICK_PLAN_LINE_ID fetch first 201 rows only)loop
    v_ff:=v_ff+1;if v_ff>200 then raise_application_error(-20881,'WAVE_DEFER_DEMAND_BOUND_200');end if;
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_PLAN',RRL_STOCK_PLAN_HELPER.decimal_text(line.PICK_PLAN_ID));
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PICK_PLAN_LINE',RRL_STOCK_PLAN_HELPER.decimal_text(line.PICK_PLAN_LINE_ID));
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(line.CUSTOMER_ORDER_ID));
    RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_CUSTOMER_ORDER_ROW',RRL_STOCK_PLAN_HELPER.decimal_text(line.CUSTOMER_ORDER_ROW_ID));
   end loop;v_ff:=0;
  end if;
"""+needle+"""
   (d.get_object('metadata').get_string('disposition')='RETURNED_TO_PLANNING'and exists(
    select 1 from RRL_PICK_WAVE_ORDER wo where wo.PICK_WAVE_ID=v_wave and wo.CUSTOMER_ORDER_ID=ff.CUSTOMER_ORDER_ID))
   or""")
# SQL cannot call JSON member method from SQL where; use declaration scalar
finish=finish.replace("s clob;v_kind varchar2(40);","v_disposition varchar2(100):=d.get_object('metadata').get_string('disposition');s clob;v_kind varchar2(40);")
finish=finish.replace("(d.get_object('metadata').get_string('disposition')='RETURNED_TO_PLANNING'and exists(","(v_disposition='RETURNED_TO_PLANNING'and exists(")
needle="  if not j.get_boolean('ready') then raise_application_error(-20886,'WAVE_EXECUTION_OR_SHIPPING_PENDING');end if;"
assert finish.count(needle)==1
finish=finish.replace(needle,"""  RRL_WAVE_EXEC_ACCESS.assert_command(p_request,p_actor);
  if d.get_object('metadata').get_string('disposition')='RETURNED_TO_PLANNING'then
   if not j.get_object('deferred_decision').get_boolean('eligible')then
    raise_application_error(-20886,'WAVE_DEFER_NOT_ELIGIBLE:'||j.get_object('deferred_decision').get_string('reason'));end if;
   j.put('completion_outcome','UNFULFILLED_RETURNED_TO_PLANNING');
   j.put('order_fulfilled',false);j.put('physical_stock_changed',false);
  else
   if not j.get_boolean('ready') then raise_application_error(-20886,'WAVE_EXECUTION_OR_SHIPPING_PENDING');end if;
   j.put('completion_outcome','PHYSICAL_EXECUTION_COMPLETE');
  end if;""")
out[str(f.relative_to(r)/"002_finish_contract.sql")]=finish
out[str(f.relative_to(r)/"002_finish_body.sql")]=finish[finish.lower().index("create or replace package body"):]
out[str(f.relative_to(r)/"apply.sql")]="-- MIGRATION_ID:2026-10-10-169-wave-deferred-demand\n@@001_access.sql\n@@002_finish_body.sql\n@@003_root_body.sql\n"
out[str(f.relative_to(r)/"rollback.sql")]="@@000_before_root.sql\n@@000_before_finish.sql\n-- Additive helper retained while readers reference it; no history or quantity removal.\n"
out[str(f.relative_to(r)/"verify.sql")]="select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_WAVE_EXEC_ACCESS','RRL_STOCK_WAVE_FINISH_CMD','RRL_STOCK_POSTING_API');\nselect NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_WAVE_EXEC_ACCESS','RRL_STOCK_WAVE_FINISH_CMD','RRL_STOCK_POSTING_API');\n"
print(json.dumps(out))
