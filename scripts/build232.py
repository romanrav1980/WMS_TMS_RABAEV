from pathlib import Path
import json
f=Path("db/migrations/2026-10-11_ni053_final_custody");out={}
out[str(f/"001_schema.sql")]="""create table RRL_STORE_LOAD_CUSTODY(
 OPERATION_ID varchar2(100)primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100)not null unique references RRL_STORE_RECEIPT_FACT(OPERATION_ID),
 LOAD_OPERATION_ID varchar2(100)not null unique references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 RELEASED_AT timestamp with time zone not null,
 RELEASED_BY nvarchar2(50)not null
);
"""
out[str(f/"002_command.sql")]="""create or replace package RRL_STOCK_STORE_CUSTODY_CMD authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_STORE_RECEIPT_CMD)as
 procedure assert_scope(p_receipt varchar2,p_actor varchar2);
 procedure declare_receipt(p_receipt varchar2,p_load varchar2,p_uid varchar2,p_resources in out nocopy json_array_t);
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
 procedure declare_receipt(p_receipt varchar2,p_load varchar2,p_uid varchar2,p_resources in out nocopy json_array_t)is
 begin
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_RECEIPT_FACT',p_receipt);
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_TT_HU_LOAD_FACT',p_load);
  RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_LOAD_CUSTODY',p_receipt);
  RRL_STOCK_PLAN_HELPER.anchor(p_resources,30,'HU',p_uid);
  RRL_STOCK_PLAN_HELPER.anchor(p_resources,70,'UNIQUE','TT.LOAD.HU:'||p_uid);
 end;
 procedure describe_source(p_receipt varchar2,p_domain out json_object_t)is
  r RRL_STORE_RECEIPT_FACT%rowtype;l RRL_TT_HU_LOAD_FACT%rowtype;n number;
 begin
  select *into r from RRL_STORE_RECEIPT_FACT where OPERATION_ID=p_receipt;
  select *into l from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=r.LOAD_OPERATION_ID;
  if r.RECEIPT_STATE!='ACCEPTED'or l.STATUS!='DEPARTED'or l.CUSTODY_RELEASED_AT is not null or l.CUSTODY_RELEASE_OPERATION_ID is not null or l.ROOT_UID is null or dbms_lob.compare(r.COMPOSITION_JSON,l.COMPOSITION_JSON)!=0 then raise_application_error(-20886,'STORE_CUSTODY_FULL_ACCEPTED_DEPARTED_SOURCE_REQUIRED');end if;
  select count(*)into n from RRL_STORE_LOAD_CUSTODY where RECEIPT_OPERATION_ID=p_receipt;
  if n>0 then raise_application_error(-20886,'STORE_CUSTODY_ALREADY_RELEASED');end if;
  select count(*)into n from RRL_STORE_RECEIPT_LINE where OPERATION_ID=p_receipt and(ACCEPTED_BASE_QTY!=SHIPPED_BASE_QTY or MISSING_BASE_QTY!=0 or REFUSED_BASE_QTY!=0 or DAMAGED_BASE_QTY!=0 or EXTRA_BASE_QTY!=0);
  if n>0 then raise_application_error(-20886,'STORE_CUSTODY_DISCREPANCY_REMAINS');end if;
  p_domain:=json_object_t();p_domain.put('receipt_operation_id',p_receipt);p_domain.put('load_operation_id',r.LOAD_OPERATION_ID);p_domain.put('uid',l.ROOT_UID);p_domain.put('warehouse_id',l.WARE_ID);
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
  declare_receipt(receipt,v.get_string('load_operation_id'),v.get_string('uid'),r);
  RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
  p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);receipt varchar2(100):=d.get_object('source').get_string('receipt_operation_id');v json_object_t;plan clob;fresh json_object_t;j json_object_t:=json_object_t();
 begin
  select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=d.get_string('operation_id');v:=json_object_t.parse(plan).get_object('domain');
  assert_scope(receipt,p_actor);describe_source(receipt,fresh);
  if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: final receipt custody');end if;
  release_accepted(receipt,p_actor);
  j.put('operation_id',d.get_string('operation_id'));j.put('receipt_operation_id',receipt);j.put('load_operation_id',v.get_string('load_operation_id'));j.put('stock_changed',false);j.put('original_departure_retained',true);j.put('custody','STORE');p_result:=j.to_clob;
 end;
end;
/
"""
# Final receipt declares the same custody closure and releases only full physically accepted cargo.
s=(f/"000_before_rrl_stock_store_receipt_cmd.sql").read_text(encoding="utf-8")
s=s.replace("  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RECEIPT_FACT',p_operation);","  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RECEIPT_FACT',p_operation);\n  RRL_STOCK_STORE_CUSTODY_CMD.declare_receipt(p_operation,load_op,v.get_string('root'),r);",1)
s=s.replace("  RRL_STOCK_STORE_WEIGHT_CORE.persist(op,fresh_weight,p_actor);","  RRL_STOCK_STORE_WEIGHT_CORE.persist(op,fresh_weight,p_actor);\n  if state_text='ACCEPTED'then RRL_STOCK_STORE_CUSTODY_CMD.release_accepted(op,p_actor);j.put('load_custody_released',true);else j.put('load_custody_released',false);end if;",1)
out[str(f/"003_receipt.sql")]=s
for name,filename in[("rrl_stock_store_return_tr_cmd","004_transport.sql"),("rrl_stock_store_return_cust_cmd","005_return_custody.sql")]:
 s=(f/("000_before_"+name+".sql")).read_text(encoding="utf-8")
 s=s.replace("STATUS in('LOADED','DEPARTED')","STATUS in('LOADED','DEPARTED')and CUSTODY_RELEASED_AT is null")
 out[str(f/filename)]=s
out[str(f/"006_proof_guard.sql")]="""create or replace trigger RRL_STORE_LOAD_CUSTODY_GUARD before insert or update or delete on RRL_STORE_LOAD_CUSTODY for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind varchar2(80);state_value varchar2(30);n number;
begin
 if not inserting then raise_application_error(-20863,'STORE_CUSTODY_APPEND_ONLY');end if;
 if op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)or:new.RELEASED_BY!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'STORE_CUSTODY_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE into kind,state_value from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if kind not in('STORE_RECEIPT','STORE_CUSTODY_RELEASE')or state_value!='IN_FLIGHT'then raise_application_error(-20863,'STORE_CUSTODY_COMMAND_REQUIRED');end if;
 if kind='STORE_RECEIPT'and:new.RECEIPT_OPERATION_ID!=op then raise_application_error(-20863,'STORE_CUSTODY_RECEIPT_SOURCE_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_LOAD_CUSTODY',:new.RECEIPT_OPERATION_ID));
 select count(*)into n from RRL_STORE_RECEIPT_FACT where OPERATION_ID=:new.RECEIPT_OPERATION_ID and LOAD_OPERATION_ID=:new.LOAD_OPERATION_ID and RECEIPT_STATE='ACCEPTED'and RECEIVED_AT=:new.RELEASED_AT;
 if n!=1 then raise_application_error(-20863,'STORE_CUSTODY_FULL_PHYSICAL_RECEIPT_REQUIRED');end if;
end;
/
"""
# Extend fresh current original load guard narrowly, preserving every prior immutable field/transition.
s=(f/"000_before_rrl_tt_hu_load_fact_guard.sql").read_text(encoding="utf-8")
out[str(f/"007_load_guard_pending.sql")]=s
s=(f/"000_before_rrl_stock_posting_api.sql").read_text(encoding="utf-8")
s=s.replace("  if g_kind='STORE_RETURN_APPROVE'then","  if g_kind='STORE_CUSTODY_RELEASE'then declare doc json_object_t:=json_object_t.parse(p_request);begin RRL_STOCK_STORE_CUSTODY_CMD.assert_scope(doc.get_object('source').get_string('receipt_operation_id'),p_actor);end;end if;\n  if g_kind='STORE_RETURN_APPROVE'then")
s=s.replace("   elsif g_kind='RESERVATION_ALLOCATE_POOL'","   elsif g_kind='STORE_CUSTODY_RELEASE'then RRL_STOCK_STORE_CUSTODY_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n   elsif g_kind='RESERVATION_ALLOCATE_POOL'",1)
s=s.replace("  elsif g_kind='LOAD_SHIPMENT' then RRL_STOCK_SINGLE_LOAD_CMD.execute_command","  elsif g_kind='STORE_CUSTODY_RELEASE'then RRL_STOCK_STORE_CUSTODY_CMD.execute_command(g_request,g_actor,p_result);\n  elsif g_kind='LOAD_SHIPMENT' then RRL_STOCK_SINGLE_LOAD_CMD.execute_command",1)
out[str(f/"008_root.sql")]=s
out["wiki/database/nicora_ni053_final_custody_design_20261011.md"]="# NI05.3: физическая ответственность рейса после полной приёмки\n232 retains DEPARTED/load/ST/history and releases only full ACCEPTED physical store receipt custody. Append-only source receipt proof/same transaction, no stock/unit/tare/government/accounting mutation. Automatic for new complete receipts; explicit scoped dispatcher command for existing immutable full receipts, no old result rewrite. Discrepancy keeps custody/capacity. Existing return plan/handover capacity excludes only proven custody-released cargo. Fresh owner/load guard snapshots/forward repair after facts.\n"
print(json.dumps(out,ensure_ascii=True))
