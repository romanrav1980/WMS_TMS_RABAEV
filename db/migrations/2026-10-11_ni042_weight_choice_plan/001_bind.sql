create or replace package RRL_WEIGHT_PLAN_BIND authid definer accessible by(package RRL_PICKING_API)as
 function bound_plan(p_order number,p_strategy varchar2,p_actor varchar2)return number;
 function target_json(p_row number,p_actor varchar2)return clob;
 procedure finish_bind(p_choice varchar2,p_plan number,p_line number,p_actor varchar2);
end;
/
create context RRL_WEIGHT_PLAN_CTX using RRL_WEIGHT_PLAN_BIND;
create or replace package body RRL_WEIGHT_PLAN_BIND as
 procedure assert_admission(p_order number,p_actor varchar2)is
 begin
  RRL_PICK_PLAN_ACCESS.assert_scope(p_order,p_actor);
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),4);
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CUSTOMER_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(p_order)));
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')is not null then raise_application_error(-20863,'WEIGHT_PLAN_EXISTING_METADATA_OWNER_REQUIRED');end if;
 end;
 procedure clear_context is begin
  dbms_session.set_context('RRL_WEIGHT_PLAN_CTX','TX_ID',null);dbms_session.set_context('RRL_WEIGHT_PLAN_CTX','CHOICE_ID',null);
  dbms_session.set_context('RRL_WEIGHT_PLAN_CTX','ACTOR',null);
 end;
 function bound_plan(p_order number,p_strategy varchar2,p_actor varchar2)return number is
  n number;plan_id number;strategy_value varchar2(30);choices number;used_choices number;valid_choices number;
 begin
  assert_admission(p_order,p_actor);
  select count(*),nvl(sum(case when STATUS='USED'then 1 else 0 end),0)into choices,used_choices from RRL_PICK_WEIGHT_CHOICE
   where CUSTOMER_ORDER_ID=p_order and STATUS in('ACCEPTED','USED');
  if used_choices=0 then return 0;end if;
  if used_choices!=choices then return 0;end if;
  select count(distinct c.PICK_PLAN_ID),max(c.PICK_PLAN_ID),max(p.PLAN_STRATEGY),count(*)into n,plan_id,strategy_value,valid_choices
   from RRL_PICK_WEIGHT_CHOICE c join RRL_PICK_PLAN p on p.PICK_PLAN_ID=c.PICK_PLAN_ID
   where c.CUSTOMER_ORDER_ID=p_order and c.STATUS='USED'and p.STATUS in('DRAFT','PLANNED_FULL','PLANNED_PARTIAL','RELEASED','DONE')
    and exists(select 1 from RRL_PICK_TASK pt where pt.PICK_PLAN_LINE_ID=c.PICK_PLAN_LINE_ID and pt.STATUS not in('CANCELLED','FAILED'));
  if n!=1 or valid_choices!=used_choices then raise_application_error(-20886,'WEIGHT_PLAN_RETIRE_PREVIOUS_CHOICE_BEFORE_REPLANNING');end if;
  if strategy_value!=p_strategy then raise_application_error(-20873,'WEIGHT_PLAN_EXISTING_STRATEGY_CONTENT_CONFLICT');end if;
  return plan_id;
 end;
 function target_json(p_row number,p_actor varchar2)return clob is
  c RRL_PICK_WEIGHT_CHOICE%rowtype;source_wire clob;j json_object_t;result_json json_object_t:=json_object_t();
  order_id number;ware number;n number;
 begin
  select CUSTOMER_ORDER_ID into order_id from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ROW_ID=p_row;
  assert_admission(order_id,p_actor);
  select count(*)into n from RRL_PICK_WEIGHT_CHOICE where case when STATUS in('ACCEPTED','USED')then CUSTOMER_ORDER_ROW_ID end=p_row;
  if n=0 then return null;end if;
  if n!=1 then raise_application_error(-20886,'WEIGHT_PLAN_ACTIVE_CHOICE_NOT_UNIQUE');end if;
  select *into c from RRL_PICK_WEIGHT_CHOICE where case when STATUS in('ACCEPTED','USED')then CUSTOMER_ORDER_ROW_ID end=p_row;
  if c.STATUS='USED'then
   select count(*)into n from RRL_PICK_PLAN p where p.PICK_PLAN_ID=c.PICK_PLAN_ID
    and p.STATUS in('DRAFT','PLANNED_FULL','PLANNED_PARTIAL','RELEASED','DONE')
    and exists(select 1 from RRL_PICK_TASK pt where pt.PICK_PLAN_LINE_ID=c.PICK_PLAN_LINE_ID and pt.STATUS not in('CANCELLED','FAILED'));
   if n!=1 then raise_application_error(-20886,'WEIGHT_PLAN_RETIRE_RETURNED_CHOICE_BEFORE_REPLANNING');end if;
   result_json.put('already_planned',true);return result_json.to_clob;
  end if;
  RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CUSTOMER_ORDER_ROW',RRL_STOCK_PLAN_HELPER.decimal_text(p_row)));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',c.SOURCE_UID));
  source_wire:=RRL_WEIGHT_BOX_PLANNING_READ.snapshot_json(p_row,p_actor);j:=json_object_t.parse(source_wire);
  if j.get_string('source_signature')!=c.SOURCE_SIGNATURE or j.get_number('warehouse_id')!=c.WARE_ID
   or j.get_number('policy_version')!=c.POLICY_VERSION then raise_application_error(-20886,'WEIGHT_PLAN_APPROVED_SOURCE_CHANGED');end if;
  result_json.put('choice_id',c.CHOICE_ID);result_json.put('source_uid',c.SOURCE_UID);result_json.put('source_cell',c.SOURCE_CELL);
  result_json.put('physical_unit_key',c.PHYSICAL_UNIT_KEY);result_json.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(c.NET_WEIGHT_KG));
  result_json.put('choice_mode',c.CHOICE_MODE);result_json.put('original_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(c.ORIGINAL_REMAINING_KG));
  return result_json.to_clob;
 end;
 procedure finish_bind(p_choice varchar2,p_plan number,p_line number,p_actor varchar2)is
  c RRL_PICK_WEIGHT_CHOICE%rowtype;n number;planned number;soft_qty number;wire clob;
 begin
  select *into c from RRL_PICK_WEIGHT_CHOICE where CHOICE_ID=p_choice;
  assert_admission(c.CUSTOMER_ORDER_ID,p_actor);
  if c.STATUS!='ACCEPTED'then raise_application_error(-20886,'WEIGHT_PLAN_CHOICE_BIND_ONCE_REQUIRED');end if;
  select count(*),max(PLANNED_QTY)into n,planned from RRL_PICK_PLAN_LINE
   where PICK_PLAN_LINE_ID=p_line and PICK_PLAN_ID=p_plan and CUSTOMER_ORDER_ROW_ID=c.CUSTOMER_ORDER_ROW_ID and ARTICUL=c.ARTICLE;
  if n!=1 or planned!=c.NET_WEIGHT_KG then raise_application_error(-20887,'WEIGHT_PLAN_EXACT_SELECTED_QUANTITY_REQUIRED');end if;
  select count(*),nvl(sum(RESERVED_QTY),0)into n,soft_qty from RRL_PICK_RESERVATION
   where PICK_PLAN_LINE_ID=p_line and PICK_PLAN_ID=p_plan and PALLET_UID=c.SOURCE_UID and SOURCE_CELL_CODE=c.SOURCE_CELL
    and RESERVATION_LEVEL='SOFT'and RESERVATION_STATUS='ACTIVE';
  if n!=1 or soft_qty!=c.NET_WEIGHT_KG then raise_application_error(-20887,'WEIGHT_PLAN_EXACT_SOURCE_SOFT_REQUIRED');end if;
  dbms_session.set_context('RRL_WEIGHT_PLAN_CTX','TX_ID',dbms_transaction.local_transaction_id(false));
  dbms_session.set_context('RRL_WEIGHT_PLAN_CTX','CHOICE_ID',p_choice);dbms_session.set_context('RRL_WEIGHT_PLAN_CTX','ACTOR',p_actor);
  update RRL_PICK_WEIGHT_CHOICE set STATUS='USED',PICK_PLAN_ID=p_plan,PICK_PLAN_LINE_ID=p_line,USED_AT=systimestamp where CHOICE_ID=p_choice;
  clear_context;
 exception when others then clear_context;raise;
 end;
end;
/
