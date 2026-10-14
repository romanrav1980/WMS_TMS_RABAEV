create or replace package RRL_CASE_WEIGHT_DECISION authid definer as
 function current_json(p_request clob,p_task number,p_line number,p_actor varchar2)return clob;
 procedure plan_order(p_order number,p_article varchar2,p_resources in out json_array_t);
end;
/
create or replace package body RRL_CASE_WEIGHT_DECISION as
 function current_json(p_request clob,p_task number,p_line number,p_actor varchar2)return clob is
  d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');
  j json_object_t:=json_object_t.parse(RRL_ORDER_WEIGHT_READ.snapshot_json(p_task,p_line,p_actor));
  reason_value varchar2(1000);
 begin
  if RRL_HAS_WRIGHT(p_actor,'case_pick_short_approve')!=1 then raise_application_error(-20882,'WEIGHT_DECISION_APPROVER_REQUIRED');end if;
  reason_value:=m.get_string('reason');
  if reason_value is null or length(trim(reason_value))<3 or lengthb(reason_value)>1000 then raise_application_error(-20886,'WEIGHT_DECISION_REASON_REQUIRED');end if;
  if m.get_number('expected_weight_policy_version')is null or m.get_number('expected_content_version')is null
   or m.get_number('expected_weight_policy_version')!=j.get_number('policy_version')
   or m.get_number('expected_content_version')!=j.get_number('content_version')
   then raise_application_error(-20886,'WEIGHT_DECISION_CURRENT_VERSIONS_REQUIRED');end if;
  if m.get_string('expected_order_weight_signature')is null
   or m.get_string('expected_order_weight_signature')!=j.get_string('order_weight_signature')
   then raise_application_error(-20886,'WEIGHT_DECISION_ORDER_SNAPSHOT_CHANGED');end if;
  if not j.get_boolean('within_tolerance')then raise_application_error(-20886,'ORDER_WEIGHT_OUTSIDE_SKU_TOLERANCE');end if;
  return j.to_clob;
 end;
 procedure plan_order(p_order number,p_article varchar2,p_resources in out json_array_t)is n number:=0;
 begin
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(p_order));
  for o in(select CUSTOMER_ORDER_ROW_ID from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=p_order and ARTICUL=p_article
   order by CUSTOMER_ORDER_ROW_ID fetch first 201 rows only)loop
   n:=n+1;if n>200 then raise_application_error(-20881,'WEIGHT_DECISION_ORDER_ROWS_BOUND');end if;
   RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_CUSTOMER_ORDER_ROW',RRL_STOCK_PLAN_HELPER.decimal_text(o.CUSTOMER_ORDER_ROW_ID));
  end loop;
  n:=0;
  for pt in(select pt.PICK_TASK_ID,pt.PICK_PLAN_ID,pt.PICK_PLAN_LINE_ID from RRL_PICK_TASK pt
   join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pt.PICK_PLAN_LINE_ID
   join RRL_CUSTOMER_ORDER_ROW cr on cr.CUSTOMER_ORDER_ROW_ID=pl.CUSTOMER_ORDER_ROW_ID
   where cr.CUSTOMER_ORDER_ID=p_order and cr.ARTICUL=p_article
   order by pt.PICK_TASK_ID fetch first 2001 rows only)loop
   n:=n+1;if n>2000 then raise_application_error(-20881,'WEIGHT_DECISION_PICK_TASKS_BOUND');end if;
   RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(pt.PICK_TASK_ID));
   RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_PICK_PLAN',RRL_STOCK_PLAN_HELPER.decimal_text(pt.PICK_PLAN_ID));
   RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_PICK_PLAN_LINE',RRL_STOCK_PLAN_HELPER.decimal_text(pt.PICK_PLAN_LINE_ID));
  end loop;
 end;
end;
/
create or replace trigger RRL_CASE_WT_DECISION_GUARD before insert or delete or update of
 WEIGHT_POLICY_VERSION,WEIGHT_TOLERANCE_PCT,WEIGHT_ORDER_REQUESTED_KG,WEIGHT_ORDER_PICKED_KG,WEIGHT_DECISION_OPERATION
 on RRL_CASE_PICK_SHORT for each row
declare wire clob;d json_object_t;op varchar2(100);state_value varchar2(20);
begin
 if inserting then
  if :new.WEIGHT_DECISION_OPERATION is not null or :new.WEIGHT_POLICY_VERSION is not null or :new.WEIGHT_TOLERANCE_PCT is not null
   or :new.WEIGHT_ORDER_REQUESTED_KG is not null or :new.WEIGHT_ORDER_PICKED_KG is not null then raise_application_error(-20863,'WEIGHT_DECISION_EXPLICIT_UPDATE_REQUIRED');end if;
  return;
 end if;
 if deleting then
  if :old.WEIGHT_DECISION_OPERATION is not null then raise_application_error(-20863,'WEIGHT_DECISION_HISTORY_IMMUTABLE');end if;
  return;
 end if;
 if :old.WEIGHT_DECISION_OPERATION is not null then raise_application_error(-20863,'WEIGHT_DECISION_ORIGINAL_IMMUTABLE');end if;
 op:=:new.WEIGHT_DECISION_OPERATION;
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null
  or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is null
  or sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=op then raise_application_error(-20863,'WEIGHT_DECISION_ROOT_TRANSACTION_REQUIRED');end if;
 select CANONICAL_REQUEST,STATE into wire,state_value from RRL_STOCK_OPERATION where OPERATION_ID=op;
 d:=json_object_t.parse(wire);
 if state_value!='IN_FLIGHT'or d.get_string('command_type')!='CASE_SHORT_APPROVE'
  or d.get_object('metadata').get_string('decision')!='WEIGHT_TOLERANCE'
  or d.get_object('source').get_number('short_id')!=:new.CASE_PICK_SHORT_ID
  or d.get_string('actor')!=:new.APPROVED_BY or :new.STATUS!='ACCEPTED'
  then raise_application_error(-20863,'WEIGHT_DECISION_CANONICAL_SOURCE_REQUIRED');end if;
end;
/
