from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni061_task_replan");out={}
s=(f/"000_before_rrl_stock_interware_put.sql").read_text(encoding="utf-8")
s=s.replace("procedure assert_scope(p_receipt varchar2,p_actor varchar2);","procedure assert_scope(p_receipt varchar2,p_actor varchar2,p_superseded number default null);",1)
s=s.replace("procedure assert_scope(p_receipt varchar2,p_actor varchar2)is n number;","procedure assert_scope(p_receipt varchar2,p_actor varchar2,p_superseded number default null)is n number;",1)
s=s.replace("if n!=1 then raise_application_error(-20882,'INTERWARE_PLACEMENT_ACTOR_REQUIRED');end if;\n end;","""if n!=1 then raise_application_error(-20882,'INTERWARE_PLACEMENT_ACTOR_REQUIRED');end if;
  if p_superseded is not null and RRL_HAS_WRIGHT(p_actor,'warehouse_task_edit')!=1 then raise_application_error(-20882,'INTERWARE_REPLAN_TASK_EDIT_REQUIRED');end if;
 end;""",1)
s=s.replace("p_domain out json_object_t) is\n receipt","p_domain out json_object_t,p_replacing boolean default false) is\n receipt",1)
s=s.replace("if p_task is not null then\n  select TEMP_DECISION","if p_task is not null and not p_replacing then\n  select TEMP_DECISION",1)
anchor=" procedure declare_rows(p_domain json_object_t"
helper=""" procedure describe_plan(p_request clob,p_actor varchar2,p_domain out json_object_t)is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');
  receipt_id varchar2(100):=d.get_object('source').get_string('receipt_operation_id');old_task number:=m.get_number('superseded_task_id');
  t RRL_WAREHOUSE_TASK%rowtype;p RRL_INTERWARE_PUT_PLAN%rowtype;reason nvarchar2(500):=m.get_string('replan_reason');n number;
 begin
  assert_scope(receipt_id,p_actor,old_task);
  if old_task is not null then
   if old_task<=0 or old_task!=trunc(old_task)or trim(reason)is null then raise_application_error(-20871,'INTERWARE_REPLAN_OLD_TASK_REASON_REQUIRED');end if;
   select *into p from RRL_INTERWARE_PUT_PLAN where TASK_ID=old_task;
   select *into t from RRL_WAREHOUSE_TASK where TASK_ID=old_task;
   if p.RECEIPT_OPERATION_ID!=receipt_id or t.STATUS is null or t.STATUS!='PLANNED'or t.TASK_TYPE!='PUTAWAY'or t.TASK_SOURCE!='MANUAL'or t.SOURCE_DOC_TYPE!='INTERWARE'or t.STARTED_AT is not null or t.STARTED_AT_INSTANT is not null or t.FACT_QTY is not null or t.RESOURCE_ID is not null or t.RESOURCE_SESSION_ID is not null or t.EQUIPMENT_ID is not null then raise_application_error(-20886,'INTERWARE_REPLAN_UNSTARTED_UNASSIGNED_ORIGINAL_TASK_REQUIRED');end if;
   select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=p.OPERATION_ID and STATE='APPLIED'and COMMAND_TYPE='INTERWARE_PUTAWAY_PLAN';if n!=1 then raise_application_error(-20886,'INTERWARE_REPLAN_ORIGINAL_APPLIED_PLAN_REQUIRED');end if;
   describe_current(receipt_id,p_actor,old_task,p_domain,true);
   if t.UID_PALLET!=p_domain.get_string('uid')or t.FROM_CELL!=p_domain.get_string('from_cell')or t.QTY!=RRL_STOCK_MATH.quantity(p_domain.get_string('quantity'))or t.UNIT_CODE!=p_domain.get_string('base_uom')or t.QTY_MODE!='PALLET'then raise_application_error(-20886,'INTERWARE_REPLAN_ORIGINAL_TASK_IDENTITY_REQUIRED');end if;
   p_domain.put('superseded_task_id',old_task);p_domain.put('superseded_plan_operation_id',p.OPERATION_ID);p_domain.put('replan_reason',reason);
  else
   if m.has('replan_reason')then raise_application_error(-20871,'INTERWARE_REPLAN_SUPERSEDED_TASK_REQUIRED');end if;
   describe_current(receipt_id,p_actor,null,p_domain);
  end if;
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_REPLAN_ORIGINAL_TASK_REQUIRED');
 end;
"""
assert anchor in s;s=s.replace(anchor,helper+anchor,1)
s=s.replace("RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_INTERWARE_PLAN',p_domain.get_string('plan_operation_id'));","""RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_INTERWARE_PLAN',p_domain.get_string('plan_operation_id'));
 if p_domain.has('superseded_task_id')then
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(p_domain.get_number('superseded_task_id')));
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_INTERWARE_PUT_PLAN',p_domain.get_string('superseded_plan_operation_id'));
 end if;""",1)
s=s.replace("describe_current(d.get_object('source').get_string('receipt_operation_id'),d.get_string('actor'),null,v);","describe_plan(p_request,d.get_string('actor'),v);",1)
s=s.replace("describe_current(v_receipt,p_actor,null,fresh);fresh.put('task_id',v_task);","describe_plan(p_request,p_actor,fresh);fresh.put('task_id',v_task);",1)
s=s.replace("temp_op varchar2(100);temp_lo number;temp_hi number;","temp_op varchar2(100);temp_lo number;temp_hi number;old_task number;reason nvarchar2(500);",1)
s=s.replace("insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID","""if v.has('superseded_task_id')then
  old_task:=v.get_number('superseded_task_id');reason:=v.get_string('replan_reason');
  update RRL_WAREHOUSE_TASK set STATUS='CANCELLED',CANCELLED_AT=systimestamp,CANCELLED_BY=p_actor,LAST_ERROR=reason where TASK_ID=old_task and STATUS='PLANNED'and STARTED_AT is null and STARTED_AT_INSTANT is null and RESOURCE_ID is null and RESOURCE_SESSION_ID is null and EQUIPMENT_ID is null;
  if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: superseded interwarehouse task');end if;
  j.put('superseded_task_id',old_task);j.put('replan_reason',reason);
 end if;
 insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID""",1)
out[str(f/"001_placement.sql")]=s
s=(f/"000_before_rrl_stock_posting_api.sql").read_text(encoding="utf-8")
old="RRL_STOCK_INTERWARE_PUT.assert_scope(doc.get_object('source').get_string('receipt_operation_id'),p_actor);"
assert s.count(old)==2
s=s.replace(old,"RRL_STOCK_INTERWARE_PUT.assert_scope(doc.get_object('source').get_string('receipt_operation_id'),p_actor,doc.get_object('metadata').get_number('superseded_task_id'));")
out[str(f/"002_root.sql")]=s
out[str(f/"003_recompile.sql")]="\n".join("alter package "+name+" compile body;"for name in["RRL_STOCK_TASK_PLAN","RRL_STOCK_TASK_CORE","RRL_STOCK_TASK_DOMAIN","RRL_STOCK_POSTING_API"])
print(json.dumps(out,ensure_ascii=True))
