import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];f=r/"db/migrations/2026-10-11_ni033_mixed_wave";out={}
a=(f/"000_before_access.sql").read_text(encoding="utf-8")
a=a.replace(" function deferred_snapshot_json(p_wave number) return clob;"," function deferred_snapshot_json(p_wave number) return clob;\n function mixed_snapshot_json(p_wave number) return clob;",1)
a=a.replace("if v_disposition!='RETURNED_TO_PLANNING'then","if v_disposition not in('RETURNED_TO_PLANNING','PARTIAL_SHIPPED_RETURNED')then")
bodypos=a.index("create or replace package body")
pos=a.index(" function deferred_snapshot_json(p_wave number)return clob is",bodypos)
a=a[:pos]+a[pos:].replace(" function deferred_snapshot_json(p_wave number)return clob is"," function decision_snapshot(p_wave number,p_allow_done number)return clob is",1)
a=a.replace("where wt.PICK_WAVE_ID=p_wave and (pt.STATUS is null or pt.STATUS!='CANCELLED');",
 """where wt.PICK_WAVE_ID=p_wave and (pt.STATUS is null or pt.STATUS not in('CANCELLED','DONE')or(p_allow_done=0 and pt.STATUS='DONE'));""",1)
needle="  if n>0 then deny('WAVE_DEFER_PICKING_NOT_CANCELLED');end if;"
assert a.count(needle)==1
a=a.replace(needle,needle+"""
  select count(*)into n from RRL_PICK_WAVE_TASK wt join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID
   where wt.PICK_WAVE_ID=p_wave and pt.STATUS='CANCELLED';
  if n=0 then deny('WAVE_DEFER_CANCELLED_DEMAND_REQUIRED');end if;
  if p_allow_done=1 then
   select count(*)into n from RRL_PICK_WAVE_TASK wt join RRL_PICK_TASK pt on pt.PICK_TASK_ID=wt.PICK_TASK_ID
    where wt.PICK_WAVE_ID=p_wave and pt.STATUS='DONE';
   if n=0 then deny('WAVE_MIXED_COMPLETED_TASK_REQUIRED');end if;
  end if;""")
old="""and (ct.STATUS is null or ct.STATUS!='CANCELLED' or ct.SHIPPED_OPERATION is not null
    or exists(select 1 from RRL_CASE_CARRIER_LOT h where h.CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID));"""
new="""and (ct.STATUS is null or ct.STATUS not in('CANCELLED','SHIPPED')or(p_allow_done=0 and ct.STATUS='SHIPPED')
    or(ct.STATUS='CANCELLED'and(ct.SHIPPED_OPERATION is not null
     or exists(select 1 from RRL_CASE_CARRIER_LOT h where h.CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID))));"""
assert old in a;a=a.replace(old,new,1)
old="and (STATUS is null or STATUS not in('DONE','CANCELLED') or (STATUS='DONE'and nvl(TASK_TYPE,'-')!='REPLENISHMENT'));"
new="""and (STATUS is null or STATUS not in('DONE','CANCELLED') or (STATUS='DONE'and nvl(TASK_TYPE,'-')!='REPLENISHMENT'
    and not(p_allow_done=1 and TASK_TYPE='PICKING_MOVE'and exists(select 1 from RRL_PICK_WAVE_TASK wt join RRL_PICK_TASK pt
     on pt.PICK_TASK_ID=wt.PICK_TASK_ID where wt.PICK_WAVE_ID=p_wave and wt.PICK_WAVE_TASK_ID=RRL_WAREHOUSE_TASK.SOURCE_TASK_ID and pt.STATUS='DONE'))));"""
assert old in a;a=a.replace(old,new,1)
old="where wo.PICK_WAVE_ID=p_wave order by pl.PICK_PLAN_LINE_ID fetch first 201 rows only"
new="""where wo.PICK_WAVE_ID=p_wave and exists(select 1 from RRL_PICK_TASK pt where pt.PICK_PLAN_LINE_ID=pl.PICK_PLAN_LINE_ID and pt.STATUS='CANCELLED')
    order by pl.PICK_PLAN_LINE_ID fetch first 201 rows only"""
assert old in a;a=a.replace(old,new,1)
a=a.replace("x.put('row_status',r.ROW_STATUS);","x.put('current_planning',json_object_t.parse(RRL_STOCK_POOL_READ.line_snapshot_json(r.CUSTOMER_ORDER_ROW_ID)));x.put('row_status',r.ROW_STATUS);",1)
old="select count(*)into n from RRL_PICK_WAVE_ORDER wo join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_ID=wo.PICK_PLAN_ID where wo.PICK_WAVE_ID=p_wave;"
new="""select count(*)into n from RRL_PICK_WAVE_ORDER wo join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_ID=wo.PICK_PLAN_ID where wo.PICK_WAVE_ID=p_wave
   and exists(select 1 from RRL_PICK_TASK pt where pt.PICK_PLAN_LINE_ID=pl.PICK_PLAN_LINE_ID and pt.STATUS='CANCELLED');"""
assert old in a;a=a.replace(old,new,1)
old="""and (ff.SHIPPED_OPERATION_ID is not null or ff.PICKED_CASE_TASK_ID is not null or ff.PICKED_WAREHOUSE_TASK_ID is not null or nvl(ff.FACT_QTY,0)>0);"""
new="""and (ff.SHIPPED_OPERATION_ID is not null or ff.PICKED_CASE_TASK_ID is not null or ff.PICKED_WAREHOUSE_TASK_ID is not null or nvl(ff.FACT_QTY,0)>0)
   and (p_allow_done=0 or exists(select 1 from RRL_CASE_PICK_TASK ct where ct.PICK_WAVE_ID=p_wave
     and ct.STATUS='CANCELLED'and ct.CASE_PICK_TASK_ID=ff.PICKED_CASE_TASK_ID));"""
assert old in a;a=a.replace(old,new,1)
pos=a.rindex("\nend;\n/")
a=a[:pos]+"""
 function deferred_snapshot_json(p_wave number)return clob is begin return decision_snapshot(p_wave,0);end;
 function mixed_snapshot_json(p_wave number)return clob is begin return decision_snapshot(p_wave,1);end;
"""+a[pos:]
out[str(f.relative_to(r)/"001_access.sql")]=a
s=(f/"000_before_finish.sql").read_text(encoding="utf-8")
needle="  elsif p_disposition is not null then raise_application_error(-20881,'WAVE_DISPOSITION_UNSUPPORTED');end if;"
assert s.count(needle)==1
s=s.replace(needle,"""  elsif p_disposition='PARTIAL_SHIPPED_RETURNED'then
   defer:=json_object_t.parse(RRL_WAVE_EXEC_ACCESS.mixed_snapshot_json(p_wave));j.put('deferred_decision',defer);
  elsif p_disposition is not null then raise_application_error(-20881,'WAVE_DISPOSITION_UNSUPPORTED');end if;""")
s=s.replace("d.get_object('metadata').get_string('disposition')='RETURNED_TO_PLANNING'then\n   for line",
 "d.get_object('metadata').get_string('disposition') in('RETURNED_TO_PLANNING','PARTIAL_SHIPPED_RETURNED')then\n   for line")
s=s.replace("(v_disposition='RETURNED_TO_PLANNING'and exists(","(v_disposition in('RETURNED_TO_PLANNING','PARTIAL_SHIPPED_RETURNED')and exists(")
needle="  else\n   if not j.get_boolean('ready') then raise_application_error(-20886,'WAVE_EXECUTION_OR_SHIPPING_PENDING');end if;"
assert s.count(needle)==1
s=s.replace(needle,"""  elsif d.get_object('metadata').get_string('disposition')='PARTIAL_SHIPPED_RETURNED'then
   if not j.get_object('deferred_decision').get_boolean('eligible')then
    raise_application_error(-20886,'WAVE_MIXED_NOT_ELIGIBLE:'||j.get_object('deferred_decision').get_string('reason'));end if;
   declare items json_array_t:=j.get_array('items');entry json_object_t;kind varchar2(40);status varchar2(40);reason varchar2(100);
   begin
    for i in 0..items.get_size-1 loop
     entry:=treat(items.get(i)as json_object_t);kind:=entry.get_string('kind');status:=entry.get_string('status');reason:=entry.get_string('reason');
     if reason is not null and not(
       kind='PICK_TASK'and status='CANCELLED'and reason='CANCELLED_DEMAND_REQUIRES_RECONCILIATION'
       or kind='CASE'and status='CANCELLED'and reason in('CASE_CONTROL_OR_SHIPPING_PENDING','EMPTY_CASE_DECISION_PENDING'))then
      raise_application_error(-20886,'WAVE_MIXED_EXECUTION_PENDING:'||reason);end if;
    end loop;
   end;
   j.put('completion_outcome','MIXED_SHIPPED_AND_RETURNED');
   j.put('order_fulfillment_changed',false);j.put('physical_stock_changed',false);
  else
   if not j.get_boolean('ready') then raise_application_error(-20886,'WAVE_EXECUTION_OR_SHIPPING_PENDING');end if;""")
out[str(f.relative_to(r)/"002_finish_contract.sql")]=s
out[str(f.relative_to(r)/"002_finish_body.sql")]=s[s.lower().index("create or replace package body"):]
out[str(f.relative_to(r)/"apply.sql")]="-- MIGRATION_ID:2026-10-11-172-mixed-wave-decision\n@@001_access.sql\n@@002_finish_body.sql\n"
out[str(f.relative_to(r)/"rollback.sql")]="@@000_before_finish.sql\n@@000_before_access.sql\n-- Restore package contracts only; no stock/order/decision history removal.\n"
out[str(f.relative_to(r)/"verify.sql")]="select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_WAVE_EXEC_ACCESS','RRL_STOCK_WAVE_FINISH_CMD');\nselect NAME,LINE,TEXT from USER_ERRORS where NAME in('RRL_WAVE_EXEC_ACCESS','RRL_STOCK_WAVE_FINISH_CMD');\n"
print(json.dumps(out))
