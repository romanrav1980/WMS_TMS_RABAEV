create or replace package RRL_WORKLOAD_CONFIG_API authid definer as
 function write_allowed(p_operation varchar2)return number;
 procedure execute_command(p_operation varchar2,p_actor varchar2,p_action varchar2,p_body clob,p_result out clob);
end;
/
create or replace package body RRL_WORKLOAD_CONFIG_API as
 g_operation varchar2(100);g_tx varchar2(100);
 function write_allowed(p_operation varchar2)return number is begin
  if p_operation=g_operation and g_tx=dbms_transaction.local_transaction_id(false)then return 1;end if;return 0;
 end;
 procedure scoped_actor(p_ware number,p_actor varchar2)is n number;begin
  select count(*)into n from RRL_WARES where ID=p_ware;
  if n!=1 or p_ware is null or p_ware<=0 then raise_application_error(-20886,'WORKLOAD_WARE_REQUIRED');end if;
  select count(*)into n from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0
   and(u.WARE_ID=p_ware or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'resource_shift_edit')=1;
  if n!=1 then raise_application_error(-20882,'WORKLOAD_CURRENT_WARE_ACTOR_REQUIRED');end if;
 end;
 procedure store_norm(p_ware number,p_actor varchar2,b json_object_t,r in out json_object_t)is
  v_article varchar2(160):=b.get_string('article');base varchar2(20):=b.get_string('base_uom');
  site varchar2(50):=b.get_string('site_code');rate number;active_flag number;old_version number;n number;reason_text nvarchar2(500);
 begin
  rate:=RRL_STOCK_MATH.quantity(b.get_string('base_per_hour'));reason_text:=b.get_string('reason');
  if rate<=0 or length(reason_text)<3 or site is null or v_article is null or base is null then raise_application_error(-20886,'WORKLOAD_NORM_FIELDS_REQUIRED');end if;
  select count(*)into n from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article and INPUT_UOM=base and BASE_UOM=base and NUMERATOR=1 and DENOMINATOR=1
   and POLICY_VERSION=(select max(POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION where ARTICUL=v_article);
  if n!=1 then raise_application_error(-20886,'WORKLOAD_CURRENT_BASE_POLICY_REQUIRED');end if;
  select nvl(max(VERSION_NO),0)into old_version from RRL_WORKLOAD_NORM where WARE_ID=p_ware and SITE_CODE=site and ARTICLE=v_article and BASE_UOM=base;
  if nvl(b.get_number('expected_version'),-1)!=old_version then raise_application_error(-20886,'WORKLOAD_NORM_VERSION_CHANGED');end if;
  active_flag:=case when b.get_boolean('active')then 1 else 0 end;
  insert into RRL_WORKLOAD_NORM(WARE_ID,SITE_CODE,ARTICLE,BASE_UOM,VERSION_NO,BASE_PER_HOUR,ACTIVE,REASON,OPERATION_ID,CREATED_BY)
   values(p_ware,site,v_article,base,old_version+1,rate,active_flag,reason_text,g_operation,p_actor);
  r.put('version',old_version+1);r.put('article',v_article);r.put('base_uom',base);r.put('base_per_hour',to_char(rate,'TM9','NLS_NUMERIC_CHARACTERS=''.,'''));
 end;
 procedure store_attendance(p_ware number,b json_object_t,r in out json_object_t)is
  v_resource number:=b.get_number('resource_id');person nvarchar2(50);n number;
  site varchar2(50):=b.get_string('site_code');v_start timestamp with time zone;v_finish timestamp with time zone;reason_text nvarchar2(500);
 begin
  v_start:=to_timestamp_tz(b.get_string('start_at'),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');
  v_finish:=to_timestamp_tz(b.get_string('finish_at'),'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');
  reason_text:=b.get_string('reason');
  if v_finish<=v_start or v_finish>v_start+interval '24'hour or site is null or length(reason_text)<3 then raise_application_error(-20886,'WORKLOAD_ATTENDANCE_FIELDS_REQUIRED');end if;
  select u.ID into person from RRL_RESOURCE r join RUSERS u on u.ID=r.USER_ID
   join RRL_RESOURCE_TYPE t on t.RESOURCE_TYPE=r.RESOURCE_TYPE
   where r.RESOURCE_ID=v_resource and r.WARE_ID=p_ware and r.ACTIVE=1 and t.ACTIVE=1 and nvl(u.DELETED,0)=0 and u.WARE_ID=p_ware and RRL_HAS_WRIGHT(u.ID,'case_pick_execute')=1
   and instr(','||replace(t.DEFAULT_TASK_TYPES,' ','')||',',',CASE_PICK,')>0;
  select count(*)into n from RRL_RESOURCE_TASK_QUAL where RESOURCE_ID=v_resource and TASK_TYPE='CASE_PICK'and ACTIVE=1
   and VALID_FROM<=systimestamp and VALID_UNTIL is null;
  if n!=1 then raise_application_error(-20886,'WORKLOAD_CASE_QUALIFICATION_REQUIRED');end if;
  select count(*)into n from RRL_WORKLOAD_ATTENDANCE a where a.PERSON_ID=person
   and(a.WARE_ID!=p_ware or a.SITE_CODE!=site)and a.START_AT<v_finish and a.FINISH_AT>v_start
   and not exists(select 1 from RRL_WORKLOAD_ATTEND_CANCEL c where c.PLAN_OPERATION_ID=a.PLAN_OPERATION_ID);
  if n>0 then raise_application_error(-20886,'WORKLOAD_PERSON_OVERLAPPING_OTHER_SITE');end if;
  insert into RRL_WORKLOAD_ATTENDANCE values(g_operation,p_ware,site,v_resource,person,v_start,v_finish,'CASE_PICK',reason_text);
  r.put('resource_id',v_resource);r.put('person_id',person);r.put('plan_operation_id',g_operation);
 end;
 procedure cancel_attendance(p_ware number,b json_object_t,r in out json_object_t)is
  plan_id varchar2(100):=b.get_string('plan_operation_id');n number;reason_text nvarchar2(500):=b.get_string('reason');
 begin
  select count(*)into n from RRL_WORKLOAD_ATTENDANCE where PLAN_OPERATION_ID=plan_id and WARE_ID=p_ware;
  if n!=1 or length(reason_text)<3 then raise_application_error(-20886,'WORKLOAD_OWN_ATTENDANCE_REQUIRED');end if;
  select count(*)into n from RRL_WORKLOAD_ATTEND_CANCEL where PLAN_OPERATION_ID=plan_id;
  if n!=0 then raise_application_error(-20886,'WORKLOAD_ATTENDANCE_ALREADY_CANCELLED');end if;
  insert into RRL_WORKLOAD_ATTEND_CANCEL values(plan_id,g_operation,reason_text);r.put('plan_operation_id',plan_id);r.put('cancelled',true);
 end;
 procedure execute_command(p_operation varchar2,p_actor varchar2,p_action varchar2,p_body clob,p_result out clob)is
  b json_object_t;result json_object_t:=json_object_t();ware number;digest varchar2(64);old_hash varchar2(64);old_actor nvarchar2(50);old_action varchar2(20);old_result clob;entered boolean:=false;
 begin
  g_operation:=null;g_tx:=null;b:=json_object_t.parse(p_body);ware:=b.get_number('warehouse_id');scoped_actor(ware,p_actor);
  if p_operation is null or length(p_operation)not between 1 and 100 or p_action not in('NORM','ATTENDANCE','CANCEL_ATTENDANCE')then raise_application_error(-20886,'WORKLOAD_COMMAND_REQUIRED');end if;
  digest:=lower(rawtohex(sys.dbms_crypto.hash(p_body,sys.dbms_crypto.hash_sh256)));
  RRL_STOCK_METADATA_TX.begin_change(p_actor,'resource_shift_edit');entered:=true;
  begin select REQUEST_HASH,ACTOR,ACTION_KIND,RESULT_JSON into old_hash,old_actor,old_action,old_result from RRL_WORKLOAD_OPERATION where OPERATION_ID=p_operation;
   if old_hash!=digest or old_actor!=p_actor or old_action!=p_action then raise_application_error(-20886,'WORKLOAD_OPERATION_PAYLOAD_CONFLICT');end if;
   p_result:=old_result;RRL_STOCK_METADATA_TX.end_change;return;
  exception when no_data_found then null;end;
  g_operation:=p_operation;g_tx:=dbms_transaction.local_transaction_id(true);
  result.put('operation_id',p_operation);result.put('warehouse_id',ware);result.put('action',p_action);result.put('stock_changed',false);
  p_result:=result.to_clob;
  insert into RRL_WORKLOAD_OPERATION(OPERATION_ID,WARE_ID,ACTION_KIND,ACTOR,REQUEST_HASH,RESULT_JSON)values(p_operation,ware,p_action,p_actor,digest,p_result);
  if p_action='NORM'then store_norm(ware,p_actor,b,result);elsif p_action='ATTENDANCE'then store_attendance(ware,b,result);else cancel_attendance(ware,b,result);end if;
  p_result:=result.to_clob;update RRL_WORKLOAD_OPERATION set RESULT_JSON=p_result where OPERATION_ID=p_operation;
  g_operation:=null;g_tx:=null;RRL_STOCK_METADATA_TX.end_change;
 exception when others then g_operation:=null;g_tx:=null;if entered then RRL_STOCK_METADATA_TX.end_change;end if;raise;
 end;
end;
/
