from pathlib import Path
import json
out={}
root="db/migrations/2026-10-11_ni072_review/"
out[root+"001_schema.sql"]="""create table RRL_DAY_REVIEW(
 OPERATION_ID varchar2(100) primary key,
 WARE_ID number not null,BUSINESS_DATE date not null,TIMEZONE_REGION varchar2(64) not null,
 VERSION_NO number not null,ACTOR varchar2(50) not null,
 REQUEST_HASH varchar2(64) not null,REQUEST_JSON clob not null,SOURCE_HASH varchar2(64) not null,
 REPORT_JSON clob not null,RESULT_JSON clob not null,
 CAPTURED_AT timestamp with time zone not null,RECORDED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_DAY_REVIEW_VER_U unique(WARE_ID,BUSINESS_DATE,TIMEZONE_REGION,VERSION_NO),
 constraint RRL_DAY_REVIEW_VER_C check(VERSION_NO>0 and VERSION_NO=trunc(VERSION_NO)and BUSINESS_DATE=trunc(BUSINESS_DATE)),
 constraint RRL_DAY_REVIEW_REQ_J check(REQUEST_JSON is json),
 constraint RRL_DAY_REVIEW_REPORT_J check(REPORT_JSON is json),
 constraint RRL_DAY_REVIEW_RESULT_J check(RESULT_JSON is json)
);
"""
out[root+"002_api.sql"]="""create or replace package RRL_DAY_REVIEW_API authid definer as
 function write_allowed return number;
 procedure context(p_ware number,p_day date,p_zone varchar2,p_actor varchar2,p_result out clob);
 procedure lookup(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob);
 procedure append_review(p_actor varchar2,p_operation varchar2,p_body clob,p_material clob,p_captured timestamp with time zone,p_result out clob);
end;
/
create or replace package body RRL_DAY_REVIEW_API as
 g_tx varchar2(100);
 function write_allowed return number is begin
  if g_tx is not null and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure access(p_ware number,p_actor varchar2,p_right varchar2)is n number;begin
  select count(*)into n from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0
   and(u.WARE_ID=p_ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,p_right)=1
   and 1=(select count(*)from RRL_WARES where ID=p_ware);
  if n!=1 then raise_application_error(-20882,'DAY_REVIEW_CURRENT_WARE_ACTOR_REQUIRED');end if;
 end;
 procedure context(p_ware number,p_day date,p_zone varchar2,p_actor varchar2,p_result out clob)is
  v_version number;r json_object_t:=json_object_t();
 begin
  access(p_ware,p_actor,'transport_dispatch_view');
  select nvl(max(VERSION_NO),0)into v_version from RRL_DAY_REVIEW where WARE_ID=p_ware and BUSINESS_DATE=trunc(p_day)and TIMEZONE_REGION=p_zone;
  r.put('version',v_version);r.put('warehouse_id',p_ware);r.put('business_date',to_char(p_day,'YYYY-MM-DD'));r.put('timezone_region',p_zone);r.put('day_closed',false);p_result:=r.to_clob;
 end;
 procedure lookup(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob)is
  b json_object_t;saved RRL_DAY_REVIEW%rowtype;v_ware number;v_hash varchar2(64);
 begin
  b:=json_object_t.parse(p_body);v_ware:=b.get_number('warehouse_id');access(v_ware,p_actor,'transport_dispatch_edit');
  v_hash:=lower(rawtohex(sys.dbms_crypto.hash(p_body,sys.dbms_crypto.hash_sh256)));
  begin select *into saved from RRL_DAY_REVIEW where OPERATION_ID=p_operation;
   if saved.ACTOR!=p_actor or saved.WARE_ID!=v_ware or saved.REQUEST_HASH!=v_hash or dbms_lob.compare(saved.REQUEST_JSON,p_body)!=0 then raise_application_error(-20886,'DAY_REVIEW_OPERATION_PAYLOAD_CONFLICT');end if;
   access(saved.WARE_ID,p_actor,'transport_dispatch_edit');p_result:=saved.RESULT_JSON;
  exception when no_data_found then p_result:=null;end;
 end;
 procedure append_review(p_actor varchar2,p_operation varchar2,p_body clob,p_material clob,p_captured timestamp with time zone,p_result out clob)is
  b json_object_t;material json_object_t;r json_object_t:=json_object_t();f json_array_t:=json_array_t();resources json_array_t:=json_array_t();
  v_ware number;v_day date;v_zone varchar2(64);v_version number;v_hash varchar2(64);v_source varchar2(64);v_open number;v_lock boolean:=false;
 begin
  if p_operation is null or lengthb(p_operation)>100 or not regexp_like(p_operation,'^[A-Za-z0-9_.:-]+$')or p_body is null or dbms_lob.getlength(p_body)>4000 then raise_application_error(-20886,'DAY_REVIEW_REQUEST_BOUND');end if;
  b:=json_object_t.parse(p_body);v_ware:=b.get_number('warehouse_id');v_zone:=b.get_string('timezone_region');
  v_day:=to_date(b.get_string('business_date'),'FXYYYY-MM-DD');
  access(v_ware,p_actor,'transport_dispatch_edit');
  if b.get_size!=6 or b.get_number('expected_version')is null or b.get_number('expected_version')<0 or b.get_number('expected_version')!=trunc(b.get_number('expected_version'))
   or v_zone is null or b.get_string('reason')is null or length(trim(b.get_string('reason')))<8 or b.get_string('source_hash')is null then raise_application_error(-20886,'DAY_REVIEW_EXPLICIT_SOURCE_REQUIRED');end if;
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.row_key(resources,'RRL_DAY_REVIEW',to_char(v_ware,'TM9')||':'||to_char(v_day,'YYYY-MM-DD')||':'||v_zone);
  RRL_STOCK_PLAN_HELPER.anchor(resources,70,'UNIQUE','DAY.REVIEW:'||p_operation);
  RRL_STOCK_LOCK_API.begin_plan;v_lock:=true;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(resources.to_clob);
  savepoint RRL_DAY_REVIEW269;
  access(v_ware,p_actor,'transport_dispatch_edit');lookup(p_actor,p_operation,p_body,p_result);
  if p_result is not null then RRL_STOCK_LOCK_API.clear_plan;return;end if;
  select nvl(max(VERSION_NO),0)into v_version from RRL_DAY_REVIEW where WARE_ID=v_ware and BUSINESS_DATE=v_day and TIMEZONE_REGION=v_zone;
  if b.get_number('expected_version')!=v_version then raise_application_error(-20886,'DAY_REVIEW_VERSION_CHANGED');end if;
  if p_material is null or dbms_lob.getlength(p_material)>4*1024*1024 or p_captured is null or p_captured>systimestamp then raise_application_error(-20886,'DAY_REVIEW_CAPTURE_BOUND');end if;
  material:=json_object_t.parse(p_material);
  if material.get_number('warehouse_id')!=v_ware or material.get_string('business_date')!=to_char(v_day,'YYYY-MM-DD')or material.get_string('timezone_region')!=v_zone
   or not material.get_boolean('consistent_snapshot')or material.get_boolean('day_closed')then raise_application_error(-20886,'DAY_REVIEW_CAPTURE_SCOPE_INVALID');end if;
  v_source:=lower(rawtohex(sys.dbms_crypto.hash(p_material,sys.dbms_crypto.hash_sh256)));
  if v_source!=b.get_string('source_hash')then raise_application_error(-20886,'DAY_REVIEW_SOURCE_CHANGED');end if;
  v_hash:=lower(rawtohex(sys.dbms_crypto.hash(p_body,sys.dbms_crypto.hash_sh256)));
  r.put('operation_id',p_operation);r.put('warehouse_id',v_ware);r.put('business_date',to_char(v_day,'YYYY-MM-DD'));r.put('timezone_region',v_zone);
  r.put('version',v_version+1);r.put('source_hash',v_source);r.put('actor',p_actor);r.put('reason',b.get_string('reason'));
  r.put('state','REVIEW_RECORDED');r.put('day_closed',false);r.put('stock_changed',false);r.put('external_obligations_closed',false);
  r.put('report',material);p_result:=r.to_clob;g_tx:=dbms_transaction.local_transaction_id(false);
  insert into RRL_DAY_REVIEW(OPERATION_ID,WARE_ID,BUSINESS_DATE,TIMEZONE_REGION,VERSION_NO,ACTOR,REQUEST_HASH,REQUEST_JSON,SOURCE_HASH,REPORT_JSON,RESULT_JSON,CAPTURED_AT)
   values(p_operation,v_ware,v_day,v_zone,v_version+1,p_actor,v_hash,p_body,v_source,p_material,p_result,p_captured);
  g_tx:=null;RRL_STOCK_LOCK_API.clear_plan;
 exception when others then
  g_tx:=null;if v_lock then RRL_STOCK_LOCK_API.clear_plan;end if;raise;
 end;
end;
/
create or replace trigger RRL_DAY_REVIEW_GUARD before insert or update or delete on RRL_DAY_REVIEW for each row
begin
 if updating or deleting or RRL_DAY_REVIEW_API.write_allowed!=1 then raise_application_error(-20863,'DAY_REVIEW_IMMUTABLE_NATIVE_ONLY');end if;
end;
/
"""
out[root+"apply.sql"]="@001_schema.sql\n@002_api.sql\n"
out[root+"rollback.sql"]="""declare n number;begin
 select count(*)into n from RRL_DAY_REVIEW;
 if n>0 then raise_application_error(-20886,'DAY_REVIEW_HISTORY_RETAINED');end if;
end;
/
drop trigger RRL_DAY_REVIEW_GUARD;
drop package RRL_DAY_REVIEW_API;
drop table RRL_DAY_REVIEW;
"""
print(json.dumps(out,ensure_ascii=True))
