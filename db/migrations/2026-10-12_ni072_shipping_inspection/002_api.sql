create or replace package RRL_DAY_INSPECT_API authid definer as
 function write_allowed(p_operation varchar2,p_actor varchar2) return number;
 procedure lookup(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob);
 procedure resolve(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob);
 procedure append_inspection(p_actor varchar2,p_operation varchar2,p_body clob,p_current_hash varchar2,p_checked_at varchar2,p_result out clob);
end;
/
create or replace package body RRL_DAY_INSPECT_API as
 g_tx varchar2(100);g_operation varchar2(100);g_actor varchar2(50);
 function write_allowed(p_operation varchar2,p_actor varchar2)return number is begin
  if g_tx is not null and g_tx=dbms_transaction.local_transaction_id(false)and g_operation=p_operation and g_actor=p_actor then return 1;end if;return 0;
 end;
 procedure access(p_ware number,p_actor varchar2,p_role varchar2)is n number;v_right varchar2(100);begin
  if p_role not in('WAREHOUSE_CHIEF','DISPATCHER')or p_role is null then raise_application_error(-20886,'DAY_INSPECTION_ROLE_REQUIRED');end if;
  v_right:=case when p_role='WAREHOUSE_CHIEF'then 'warehouse_day_inspect'else 'transport_dispatch_edit'end;
  select count(*)into n from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0
   and(u.WARE_ID=p_ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,v_right)=1
   and 1=(select count(*)from RRL_WARES where ID=p_ware);
  if n!=1 then raise_application_error(-20882,'DAY_INSPECTION_CURRENT_WARE_ACTOR_REQUIRED');end if;
 end;
 procedure lookup(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob)is
  b json_object_t;v_review varchar2(100);v_role varchar2(30);v_ware number;v_hash varchar2(64);old RRL_DAY_INSPECTION%rowtype;
 begin
  p_result:=null;
  if p_operation is null or lengthb(p_operation)>100 or not regexp_like(p_operation,'^[A-Za-z0-9_.:-]+$')or p_body is null or dbms_lob.getlength(p_body)>4000 then raise_application_error(-20886,'DAY_INSPECTION_REQUEST_BOUND');end if;
  b:=json_object_t.parse(p_body);v_review:=b.get_string('review_operation_id');v_role:=b.get_string('inspection_role');
  select WARE_ID into v_ware from RRL_DAY_REVIEW where OPERATION_ID=v_review;access(v_ware,p_actor,v_role);
  v_hash:=lower(rawtohex(sys.dbms_crypto.hash(p_body,sys.dbms_crypto.hash_sh256)));
  begin
   select *into old from RRL_DAY_INSPECTION where OPERATION_ID=p_operation;
   if old.ACTOR!=p_actor or old.REQUEST_HASH!=v_hash or dbms_lob.compare(old.REQUEST_JSON,p_body)!=0 then raise_application_error(-20886,'DAY_INSPECTION_OPERATION_CONTENT_CONFLICT');end if;
   p_result:=old.RESULT_JSON;
  exception when no_data_found then null;end;
 exception when no_data_found then raise_application_error(-20886,'DAY_INSPECTION_REVIEW_REQUIRED');
 end;
 procedure resolve(p_actor varchar2,p_operation varchar2,p_body clob,p_result out clob)is
  b json_object_t;parent RRL_DAY_REVIEW%rowtype;v_review varchar2(100);v_role varchar2(30);
  f json_array_t:=json_array_t();resources json_array_t:=json_array_t();result json_object_t:=json_object_t();v_lock boolean:=false;
 begin
  lookup(p_actor,p_operation,p_body,p_result);if p_result is not null then return;end if;
  b:=json_object_t.parse(p_body);v_review:=b.get_string('review_operation_id');v_role:=b.get_string('inspection_role');
  select *into parent from RRL_DAY_REVIEW where OPERATION_ID=v_review;access(parent.WARE_ID,p_actor,v_role);
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.row_key(resources,'RRL_DAY_REVIEW',to_char(parent.WARE_ID,'TM9')||':'||to_char(parent.BUSINESS_DATE,'YYYY-MM-DD')||':'||parent.TIMEZONE_REGION);
  RRL_STOCK_PLAN_HELPER.row_key(resources,'RRL_DAY_INSPECTION',v_review);
  RRL_STOCK_PLAN_HELPER.anchor(resources,70,'UNIQUE','DAY.INSPECTION:'||p_operation);
  RRL_STOCK_LOCK_API.begin_plan;v_lock:=true;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(resources.to_clob);
  access(parent.WARE_ID,p_actor,v_role);lookup(p_actor,p_operation,p_body,p_result);
  if p_result is null then result.put('operation_id',p_operation);result.put('state','NOT_RECORDED');result.put('day_closed',false);p_result:=result.to_clob;end if;
  RRL_STOCK_LOCK_API.clear_plan;
 exception when others then if v_lock then RRL_STOCK_LOCK_API.clear_plan;end if;raise;
 end;
 procedure append_inspection(p_actor varchar2,p_operation varchar2,p_body clob,p_current_hash varchar2,p_checked_at varchar2,p_result out clob)is
  b json_object_t;parent RRL_DAY_REVIEW%rowtype;v_review varchar2(100);v_role varchar2(30);v_source varchar2(64);v_note varchar2(2000);v_observed boolean;v_empty number;
  f json_array_t:=json_array_t();resources json_array_t:=json_array_t();result json_object_t:=json_object_t();
  v_lock boolean:=false;v_saved boolean:=false;v_latest number;v_n number;v_checked timestamp with time zone;v_hash varchar2(64);
 begin
  lookup(p_actor,p_operation,p_body,p_result);if p_result is not null then return;end if;
  b:=json_object_t.parse(p_body);v_review:=b.get_string('review_operation_id');v_role:=b.get_string('inspection_role');v_source:=b.get_string('source_hash');v_note:=b.get_string('note');v_observed:=b.get_boolean('observed_empty');
  if b.get_size!=5 or v_observed is null or v_note is null or length(trim(v_note))<8 or lengthb(v_note)>2000 or v_source is null then raise_application_error(-20886,'DAY_INSPECTION_EXPLICIT_OBSERVATION_REQUIRED');end if;
  v_empty:=case when v_observed then 1 else 0 end;
  select *into parent from RRL_DAY_REVIEW where OPERATION_ID=v_review;access(parent.WARE_ID,p_actor,v_role);
  RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
  RRL_STOCK_PLAN_HELPER.row_key(resources,'RRL_DAY_REVIEW',to_char(parent.WARE_ID,'TM9')||':'||to_char(parent.BUSINESS_DATE,'YYYY-MM-DD')||':'||parent.TIMEZONE_REGION);
  RRL_STOCK_PLAN_HELPER.row_key(resources,'RRL_DAY_INSPECTION',v_review);
  RRL_STOCK_PLAN_HELPER.anchor(resources,70,'UNIQUE','DAY.INSPECTION:'||p_operation);
  RRL_STOCK_LOCK_API.begin_plan;v_lock:=true;RRL_STOCK_LOCK_API.acquire_policies(f.to_clob);RRL_STOCK_LOCK_API.acquire_resources(resources.to_clob);
  savepoint RRL_DAY_INSPECT692;v_saved:=true;
  access(parent.WARE_ID,p_actor,v_role);lookup(p_actor,p_operation,p_body,p_result);
  if p_result is not null then RRL_STOCK_LOCK_API.clear_plan;return;end if;
  select max(VERSION_NO)into v_latest from RRL_DAY_REVIEW where WARE_ID=parent.WARE_ID and BUSINESS_DATE=parent.BUSINESS_DATE and TIMEZONE_REGION=parent.TIMEZONE_REGION;
  if parent.VERSION_NO!=v_latest then raise_application_error(-20886,'DAY_INSPECTION_LATEST_REVIEW_REQUIRED');end if;
  if v_source!=parent.SOURCE_HASH or p_current_hash is null or p_current_hash!=parent.SOURCE_HASH then raise_application_error(-20886,'DAY_INSPECTION_CURRENT_SOURCE_CHANGED');end if;
  v_checked:=to_timestamp_tz(p_checked_at,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');
  if v_checked is null or v_checked<parent.CAPTURED_AT or v_checked>systimestamp then raise_application_error(-20886,'DAY_INSPECTION_SOURCE_CLOCK_REQUIRED');end if;
  select count(*)into v_n from RRL_DAY_INSPECTION where REVIEW_OPERATION_ID=v_review and INSPECTION_ROLE=v_role;
  if v_n!=0 then raise_application_error(-20886,'DAY_INSPECTION_ROLE_ALREADY_RECORDED');end if;
  select count(*)into v_n from RRL_DAY_INSPECTION where REVIEW_OPERATION_ID=v_review and ACTOR=p_actor;
  if v_n!=0 then raise_application_error(-20886,'DAY_INSPECTION_INDEPENDENT_ACTORS_REQUIRED');end if;
  result.put('operation_id',p_operation);result.put('review_operation_id',v_review);result.put('inspection_role',v_role);result.put('actor',p_actor);
  result.put('observed_empty',v_observed);result.put('note',v_note);result.put('source_hash',v_source);result.put('state','DECLARATION_RECORDED');
  result.put('source_checked_at',to_char(v_checked,'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'));result.put('day_closed',false);result.put('stock_changed',false);result.put('external_obligations_closed',false);
  p_result:=result.to_clob;v_hash:=lower(rawtohex(sys.dbms_crypto.hash(p_body,sys.dbms_crypto.hash_sh256)));
  g_tx:=dbms_transaction.local_transaction_id;g_operation:=p_operation;g_actor:=p_actor;
  insert into RRL_DAY_INSPECTION(OPERATION_ID,REVIEW_OPERATION_ID,INSPECTION_ROLE,ACTOR,OBSERVED_EMPTY,NOTE,REQUEST_JSON,REQUEST_HASH,SOURCE_HASH,SOURCE_CHECKED_AT,RESULT_JSON)
  values(p_operation,v_review,v_role,p_actor,v_empty,v_note,p_body,v_hash,v_source,v_checked,p_result);
  g_tx:=null;g_operation:=null;g_actor:=null;RRL_STOCK_LOCK_API.clear_plan;
 exception when others then
  g_tx:=null;g_operation:=null;g_actor:=null;if v_saved then rollback to RRL_DAY_INSPECT692;end if;
  if v_lock then RRL_STOCK_LOCK_API.clear_plan;end if;raise;
 end;
end;
/
create or replace trigger RRL_DAY_INSPECT_GUARD before insert or update or delete on RRL_DAY_INSPECTION for each row
begin
 if not inserting then raise_application_error(-20863,'DAY_INSPECTION_IMMUTABLE');end if;
 if RRL_DAY_INSPECT_API.write_allowed(:new.OPERATION_ID,:new.ACTOR)!=1 then raise_application_error(-20863,'DAY_INSPECTION_API_REQUIRED');end if;
end;
/
