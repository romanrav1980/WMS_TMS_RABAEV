create or replace package RRL_INTERWARE_THERMAL authid definer as
 function mode_json(p_plan varchar2)return clob;
 procedure assert_release(p_plan varchar2);
 procedure assert_cell(p_mode clob,p_ware number,p_cell varchar2);
 procedure record_decision(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_INTERWARE_THERMAL as
 procedure sku_range(p_plan RRL_INTERWARE_PLAN%rowtype,p_lo out number,p_hi out number)is article varchar2(160);
 begin
  select ARTICUL into article from RRL_PALLETS where UID_PALLET=p_plan.ROOT_UID;
  begin select TEMP_MIN,TEMP_MAX into p_lo,p_hi from RRL_RECEIPT_SKU_RULE where WARE_ID=p_plan.TARGET_WARE_ID and ARTICUL=article;exception when no_data_found then p_lo:=null;p_hi:=null;end;
  if (p_lo is null and p_hi is not null)or(p_lo is not null and p_hi is null)or p_lo>p_hi then raise_application_error(-20886,'INTERWARE_SKU_TEMPERATURE_RANGE_INVALID');end if;
 end;
 function mode_json(p_plan varchar2)return clob is original RRL_INTERWARE_PLAN%rowtype;fact RRL_INTERWARE_THERMAL_FACT%rowtype;lo number;hi number;j json_object_t:=json_object_t();
 begin
  select *into original from RRL_INTERWARE_PLAN where OPERATION_ID=p_plan;sku_range(original,lo,hi);
  j.put('revision',0);j.put('decision_kind','NONE');j.put_null('decision_operation_id');j.put('task_temp_min',lo);j.put('task_temp_max',hi);j.put('sku_temp_min',lo);j.put('sku_temp_max',hi);j.put('observation_basis','ADMIN_MANUAL');
  begin
   select *into fact from RRL_INTERWARE_THERMAL_FACT where PLAN_OPERATION_ID=p_plan order by REVISION_NO desc fetch first 1 row only;
   j.put('revision',fact.REVISION_NO);j.put('decision_kind',fact.DECISION_KIND);j.put('decision_operation_id',fact.OPERATION_ID);j.put('task_temp_min',fact.TASK_TEMP_MIN);j.put('task_temp_max',fact.TASK_TEMP_MAX);j.put('observed_c',fact.OBSERVED_C);j.put('observation_reference',fact.OBSERVATION_REFERENCE);
   if fact.DECISION_KIND='PROCEED'and((lo is not null and(fact.TASK_TEMP_MIN is null or fact.TASK_TEMP_MIN<lo))or(hi is not null and(fact.TASK_TEMP_MAX is null or fact.TASK_TEMP_MAX>hi)))then raise_application_error(-20886,'INTERWARE_TEMPERATURE_SKU_POLICY_CHANGED');end if;
  exception when no_data_found then null;end;
  return j.to_clob;
 end;
 procedure assert_release(p_plan varchar2)is j json_object_t:=json_object_t.parse(mode_json(p_plan));
 begin if j.get_string('decision_kind')='HOLD'then raise_application_error(-20886,'INTERWARE_TEMPERATURE_DISPATCHER_HOLD');end if;end;
 procedure assert_cell(p_mode clob,p_ware number,p_cell varchar2)is j json_object_t:=json_object_t.parse(p_mode);lo number:=j.get_number('task_temp_min');hi number:=j.get_number('task_temp_max');clo number;chi number;
 begin
  if lo is null and hi is null then return;end if;
  begin select TEMP_MIN,TEMP_MAX into clo,chi from RRL_RECEIPT_CELL_RULE where WARE_ID=p_ware and CELL=p_cell;exception when no_data_found then clo:=null;chi:=null;end;
  if lo is null or hi is null or clo is null or chi is null or clo>chi or clo<lo or chi>hi then raise_application_error(-20886,'INTERWARE_TASK_CELL_TEMPERATURE_INCOMPATIBLE');end if;
 end;
 procedure record_decision(p_request clob,p_actor varchar2,p_result out clob)is
  d json_object_t:=json_object_t.parse(p_request);original RRL_INTERWARE_PLAN%rowtype;j json_object_t:=json_object_t();op varchar2(100):=d.get_string('operation_id');plan_id varchar2(100):=d.get_string('plan_operation_id');kind varchar2(10):=d.get_string('decision_kind');rev number;n number;lo number;hi number;tlo number:=d.get_number('task_temp_min');thi number:=d.get_number('task_temp_max');observed number:=d.get_number('observed_c');old_hash raw(32);hash_value raw(32):=sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256);trip number;locked_trip number;observation nvarchar2(200):=d.get_string('observation_reference');reason nvarchar2(500):=d.get_string('reason');reference varchar2(60):=d.get_string('decision_reference');
  procedure scope_check is begin
   select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'transport_dispatch_edit')=1 and(WARE_ID=original.TARGET_WARE_ID or upper(trim(USER_GROUP))='GLOBAL_ADMIN');if n!=1 then raise_application_error(-20882,'INTERWARE_CURRENT_TARGET_DISPATCHER_REQUIRED');end if;
  end;
 begin
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
  select *into original from RRL_INTERWARE_PLAN where OPERATION_ID=plan_id;scope_check;
  begin select PAYLOAD_HASH,RESULT_JSON into old_hash,p_result from RRL_INTERWARE_THERMAL_FACT where OPERATION_ID=op;if old_hash!=hash_value then raise_application_error(-20871,'INTERWARE_THERMAL_PAYLOAD_CONFLICT');end if;return;exception when no_data_found then null;end;
  select *into original from RRL_INTERWARE_PLAN where OPERATION_ID=plan_id for update;
  select nvl(max(REVISION_NO),0)into rev from RRL_INTERWARE_THERMAL_FACT where PLAN_OPERATION_ID=plan_id;
  if d.get_number('expected_revision')is null or d.get_number('expected_revision')!=rev then raise_application_error(-20890,'CLOSURE_CHANGED: interwarehouse thermal revision');end if;
  if op is null or kind is null or kind not in('HOLD','PROCEED')or observed is null or observed<-100 or observed>100 or observed!=round(observed,3) or trim(d.get_string('observation_reference'))is null or trim(d.get_string('reason'))is null or trim(d.get_string('decision_reference'))is null then raise_application_error(-20871,'INTERWARE_MANUAL_TEMPERATURE_DECISION_REQUIRED');end if;
  sku_range(original,lo,hi);
  if(tlo is null and thi is not null)or(tlo is not null and thi is null)or tlo>thi or tlo<-100 or thi>100 or tlo!=round(tlo,3) or thi!=round(thi,3) then raise_application_error(-20886,'INTERWARE_TASK_TEMPERATURE_RANGE_INVALID');end if;
  if kind='PROCEED'and((lo is not null and(tlo is null or tlo<lo))or(hi is not null and(thi is null or thi>hi)))then raise_application_error(-20886,'INTERWARE_TASK_TEMPERATURE_SKU_INCOMPATIBLE');end if;
  trip:=RRL_INTERWARE_ROUTING.target_trip(plan_id);
  select ID into locked_trip from RRL_TRANSPORT_TASK where ID=trip and CONDITION='Спланирован'and nvl(DELETED,0)=0 for update;scope_check;
  j.put('operation_id',op);j.put('plan_operation_id',plan_id);j.put('revision',rev+1);j.put('decision_kind',kind);j.put('observed_c',observed);j.put('task_temp_min',tlo);j.put('task_temp_max',thi);j.put('sku_temp_min',lo);j.put('sku_temp_max',hi);j.put('observation_basis','ADMIN_MANUAL');j.put('stock_changed',false);j.put('sensor_verified',false);p_result:=j.to_clob;
  insert into RRL_INTERWARE_THERMAL_FACT(OPERATION_ID,PLAN_OPERATION_ID,REVISION_NO,DECISION_KIND,OBSERVED_C,OBSERVATION_REFERENCE,TASK_TEMP_MIN,TASK_TEMP_MAX,SKU_TEMP_MIN,SKU_TEMP_MAX,REASON_TEXT,DECISION_REFERENCE,ACTOR,PAYLOAD_HASH,CANONICAL_REQUEST,RESULT_JSON)
   values(op,plan_id,rev+1,kind,observed,observation,tlo,thi,lo,hi,reason,reference,p_actor,hash_value,p_request,p_result);
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_THERMAL_EXISTING_PLANNED_TRIP_REQUIRED');
 end;
end;
/
