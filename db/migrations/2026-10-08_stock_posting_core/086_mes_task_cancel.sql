create or replace package RRL_STOCK_MES_CANCEL_CMD authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_MES_CANCEL_CMD as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
  d json_object_t:=json_object_t.parse(p_request);t RRL_MES_RAW_TRANSFER_TASK%rowtype;sr RRL_STOCK_RESERVATION%rowtype;
  f json_array_t:=json_array_t();r json_array_t:=json_array_t();v json_object_t:=json_object_t();a json_array_t:=json_array_t();
 begin
  declare
 v_json_sql_1_1 number:=d.get_object('source').get_number('raw_task_id');
begin
select * into t from RRL_MES_RAW_TRANSFER_TASK where TASK_ID=v_json_sql_1_1;
end;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRODUCTION_ORDER',RRL_STOCK_PLAN_HELPER.decimal_text(t.PRODUCTION_ORDER_ID));
  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_MES_RAW_TRANSFER_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(t.TASK_ID));
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  if t.RESERVATION_ID is not null then
   select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=t.RESERVATION_ID;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(sr.RESERVATION_ID));
   RRL_STOCK_PLAN_HELPER.stock_closure(f,r,sr.UID_PALLET,sr.ARTICUL,sr.CELL,null);
   v.put('reservation',sr.RESERVATION_ID);v.put('reservation_version',sr.RESERVATION_VERSION);
  end if;
  for w in(select TASK_ID from RRL_WAREHOUSE_TASK where TASK_SOURCE='MES_RAW_SUPPLY' and SOURCE_TASK_ID=t.TASK_ID and STATUS not in('DONE','CANCELLED') order by TASK_ID) loop
   if a.get_size>=200 then raise_application_error(-20881,'MES_CANCEL_TASK_BOUND');end if;
   RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(w.TASK_ID));a.append(w.TASK_ID);
  end loop;
  v.put('document',t.PRODUCTION_ORDER_ID);v.put('raw_task',t.TASK_ID);v.put('warehouse_tasks',a);
  p_domain:=v.to_clob;p_policies:=f.to_clob;p_resources:=r.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;j json_object_t:=json_object_t();a json_array_t;
  plan clob;t RRL_MES_RAW_TRANSFER_TASK%rowtype;sr RRL_STOCK_RESERVATION%rowtype;status varchar2(40);ver number;n number;id number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'mes_raw_transfer_cancel')!=1 then raise_application_error(-20882,'MES_CANCEL_FORBIDDEN');end if;
  declare
 v_json_sql_2_1 varchar2(32767):=d.get_string('operation_id');
begin
select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=v_json_sql_2_1;
end;v:=json_object_t.parse(plan).get_object('domain');a:=v.get_array('warehouse_tasks');
  declare
 v_json_sql_3_1 number:=v.get_number('document');
begin
select STATUS into status from RRL_PRODUCTION_ORDER where PRODUCTION_ORDER_ID=v_json_sql_3_1 for update;
end;
  declare
 v_json_sql_4_1 number:=v.get_number('raw_task');
begin
select * into t from RRL_MES_RAW_TRANSFER_TASK where TASK_ID=v_json_sql_4_1 for update;
end;
  if t.PRODUCTION_ORDER_ID!=v.get_number('document') or nvl(t.RESERVATION_ID,-1)!=nvl(v.get_number('reservation'),-1) then raise_application_error(-20890,'CLOSURE_CHANGED: MES cancellation');end if;
  if t.TASK_STATUS='DONE' then raise_application_error(-20886,'COMPLETED_TASK_CANNOT_CANCEL');end if;
  select count(*) into n from RRL_WAREHOUSE_TASK where TASK_SOURCE='MES_RAW_SUPPLY' and SOURCE_TASK_ID=t.TASK_ID and STATUS not in('DONE','CANCELLED');
  if n!=a.get_size then raise_application_error(-20890,'CLOSURE_CHANGED: MES task children');end if;
  if t.RESERVATION_ID is not null then
   select * into sr from RRL_STOCK_RESERVATION where RESERVATION_ID=t.RESERVATION_ID for update;
   if sr.RESERVATION_VERSION!=v.get_number('reservation_version') or sr.SOURCE_DOC_TYPE!='PRODUCTION_ORDER' or sr.SOURCE_DOC_ID!=t.PRODUCTION_ORDER_ID then raise_application_error(-20890,'CLOSURE_CHANGED: MES reservation');end if;
   if sr.STATUS in('ACTIVE','ALLOCATED','PICKING') then
    if sr.RESERVATION_KIND!='HARD' then raise_application_error(-20869,'MES_HARD_RESERVATION_REQUIRED');end if;
    select max(POLICY_VERSION) into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=sr.ARTICUL and INPUT_UOM=sr.BASE_UOM and BASE_UOM=sr.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;
    if ver is null then raise_application_error(-20868,'MES_BASE_POLICY_REQUIRED');end if;
    RRL_STOCK_UNIT_CORE.release_units(sr.RESERVATION_ID,sr.BASE_QTY,null,0);
    RRL_STOCK_RESERVE_CORE.release_hard(sr.RESERVATION_ID,sr.BASE_QTY,ver,'PRODUCTION_ORDER',t.PRODUCTION_ORDER_ID,p_actor);
    RRL_STOCK_CTX_API.begin_effect('RESERVATION',sr.UID_PALLET,sr.CELL,sr.RESERVATION_ID);
    declare
 v_json_sql_5_1 varchar2(32767):=d.get_object('metadata').get_string('reason');
begin
update RRL_STOCK_RESERVATION set STATUS='CANCELLED',RELEASE_REASON=v_json_sql_5_1,RESERVATION_VERSION=RESERVATION_VERSION+1 where RESERVATION_ID=sr.RESERVATION_ID;
end;
    RRL_STOCK_CTX_API.end_effect;
   end if;
  end if;
  for i in 0..a.get_size-1 loop
   id:=a.get_number(i);select STATUS into status from RRL_WAREHOUSE_TASK where TASK_ID=id for update;
   if status in('DONE','CANCELLED') then raise_application_error(-20890,'CLOSURE_CHANGED: MES child state');end if;
   declare
 v_json_sql_6_1 varchar2(32767):=d.get_object('metadata').get_string('reason');
begin
update RRL_WAREHOUSE_TASK set STATUS='CANCELLED',CANCELLED_AT=systimestamp,CANCELLED_BY=p_actor,LAST_ERROR=v_json_sql_6_1 where TASK_ID=id;
end;
  end loop;
  declare
 v_json_sql_7_1 varchar2(32767):=d.get_object('metadata').get_string('reason');
begin
update RRL_MES_RAW_TRANSFER_TASK set TASK_STATUS='CANCELLED',CANCELLED_AT=systimestamp,CANCELLED_BY=p_actor,LAST_ERROR=v_json_sql_7_1 where TASK_ID=t.TASK_ID;
end;
  j.put('operation_id',d.get_string('operation_id'));j.put('raw_task_id',t.TASK_ID);j.put('status','CANCELLED');p_result:=j.to_clob;
 end;
end;
/
