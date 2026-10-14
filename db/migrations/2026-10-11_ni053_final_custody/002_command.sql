create or replace package RRL_STOCK_STORE_CUSTODY_CMD authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_STORE_RECEIPT_CMD)as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2);
 procedure declare_receipt(p_receipt varchar2,p_load varchar2,p_uid varchar2,p_resources in out nocopy json_array_t,p_operation varchar2 default null);
 procedure release_accepted(p_receipt varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_STORE_CUSTODY_CMD as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2)is n number;
 begin
  select count(*)into n from RRL_STORE_RECEIPT_FACT r join RRL_TT_HU_LOAD_FACT l on l.LOAD_OPERATION_ID=r.LOAD_OPERATION_ID join RUSERS u on u.ID=p_actor
   where r.OPERATION_ID=p_receipt and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_close')=1 and(u.WARE_ID=l.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'STORE_CUSTODY_CURRENT_DISPATCHER_REQUIRED');end if;
 end;
 procedure declare_receipt(p_receipt varchar2,p_load varchar2,p_uid varchar2,p_resources in out nocopy json_array_t,p_operation varchar2 default null)is
 begin
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_RECEIPT_FACT',p_receipt);
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_TT_HU_LOAD_FACT',p_load);
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_LOAD_CUSTODY',nvl(p_operation,p_receipt));
  RRL_STOCK_PLAN_HELPER.anchor(p_resources,30,'HU',p_uid);
  RRL_STOCK_PLAN_HELPER.anchor(p_resources,70,'UNIQUE','TT.LOAD.HU:'||p_uid);
 end;
 procedure describe_source(p_receipt varchar2,p_domain out json_object_t)is
  r RRL_STORE_RECEIPT_FACT%rowtype;l RRL_TT_HU_LOAD_FACT%rowtype;n number;
 begin
  select *into r from RRL_STORE_RECEIPT_FACT where OPERATION_ID=p_receipt;
  select *into l from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=r.LOAD_OPERATION_ID;
  if r.RECEIPT_STATE!='ACCEPTED'or l.STATUS!='DEPARTED'or l.CUSTODY_RELEASED_AT is not null or l.CUSTODY_RELEASE_OPERATION_ID is not null or(l.ROOT_UID is null and l.ROOT_CASE_TASK_ID is null) or dbms_lob.compare(r.COMPOSITION_JSON,l.COMPOSITION_JSON)!=0 then raise_application_error(-20886,'STORE_CUSTODY_FULL_ACCEPTED_DEPARTED_SOURCE_REQUIRED');end if;
  select count(*)into n from RRL_STORE_LOAD_CUSTODY where RECEIPT_OPERATION_ID=p_receipt;
  if n>0 then raise_application_error(-20886,'STORE_CUSTODY_ALREADY_RELEASED');end if;
  select count(*)into n from RRL_STORE_RECEIPT_LINE where OPERATION_ID=p_receipt and(ACCEPTED_BASE_QTY!=SHIPPED_BASE_QTY or MISSING_BASE_QTY!=0 or REFUSED_BASE_QTY!=0 or DAMAGED_BASE_QTY!=0 or REPORTED_EXTRA_BASE_QTY!=0);
  if n>0 then raise_application_error(-20886,'STORE_CUSTODY_DISCREPANCY_REMAINS');end if;
  p_domain:=json_object_t();p_domain.put('receipt_operation_id',p_receipt);p_domain.put('load_operation_id',r.LOAD_OPERATION_ID);p_domain.put('uid',nvl(l.ROOT_UID,'CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(l.ROOT_CASE_TASK_ID)));p_domain.put('warehouse_id',l.WARE_ID);
 end;
 procedure release_accepted(p_receipt varchar2,p_actor varchar2)is
  op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');d json_object_t;load_id varchar2(100);now_value timestamp with time zone;
 begin
  describe_source(p_receipt,d);load_id:=d.get_string('load_operation_id');
  select RECEIVED_AT into now_value from RRL_STORE_RECEIPT_FACT where OPERATION_ID=p_receipt;
  insert into RRL_STORE_LOAD_CUSTODY(OPERATION_ID,RECEIPT_OPERATION_ID,LOAD_OPERATION_ID,RELEASED_AT,RELEASED_BY)values(op,p_receipt,load_id,now_value,p_actor);
  update RRL_TT_HU_LOAD_FACT set CUSTODY_RELEASED_AT=now_value,CUSTODY_RELEASE_OPERATION_ID=op where LOAD_OPERATION_ID=load_id and CUSTODY_RELEASED_AT is null and CUSTODY_RELEASE_OPERATION_ID is null;
  if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: final store custody');end if;
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
  d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();receipt varchar2(100):=d.get_object('source').get_string('receipt_operation_id');
 begin
  assert_scope(receipt,d.get_string('actor'));describe_source(receipt,v);
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
  declare_receipt(receipt,v.get_string('load_operation_id'),v.get_string('uid'),r,p_operation);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);receipt varchar2(100):=d.get_object('source').get_string('receipt_operation_id');v json_object_t;plan clob;fresh json_object_t;op varchar2(100):=d.get_string('operation_id');j json_object_t:=json_object_t();
 begin
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
  assert_scope(receipt,p_actor);describe_source(receipt,fresh);
  if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: final receipt custody');end if;
  release_accepted(receipt,p_actor);
  j.put('operation_id',d.get_string('operation_id'));j.put('receipt_operation_id',receipt);j.put('load_operation_id',v.get_string('load_operation_id'));j.put('stock_changed',false);j.put('original_departure_retained',true);j.put('custody','STORE');p_result:=j.to_clob;
 end;
end;
/
