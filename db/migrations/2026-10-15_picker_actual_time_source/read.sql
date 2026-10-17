create or replace package RRL_PICKER_TIME_READ authid definer accessible by(package RRL_PICKER_TIME_API) as
 function stamp(p_value timestamp with time zone)return varchar2;
 procedure load_state(p_actor varchar2,p_state out RRL_PICKER_TIME_STREAM%rowtype);
 function state_json(p_state RRL_PICKER_TIME_STREAM%rowtype)return json_object_t;
 procedure current_state(p_actor varchar2,p_result out clob);
 procedure read_window(p_actor varchar2,p_start varchar2,p_finish varchar2,p_result out clob);
end;
/
create or replace package body RRL_PICKER_TIME_READ as
 function stamp(p_value timestamp with time zone)return varchar2 is begin
  return to_char(p_value at time zone 'UTC','YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');
 end;
 procedure load_state(p_actor varchar2,p_state out RRL_PICKER_TIME_STREAM%rowtype)is begin
  RRL_PICKER_TIME_AUTH.actor_required(p_actor);
  begin select *into p_state from RRL_PICKER_TIME_STREAM where OPERATOR_ID=p_actor;
  exception when no_data_found then p_state.OPERATOR_ID:=p_actor;p_state.STREAM_VERSION:=0;p_state.SHIFT_STATE:='OFF';p_state.WORK_STATE:='IDLE';end;
 end;
 function state_json(p_state RRL_PICKER_TIME_STREAM%rowtype)return json_object_t is j json_object_t:=json_object_t();begin
  j.put('operator_id',p_state.OPERATOR_ID);j.put('stream_version',p_state.STREAM_VERSION);
  j.put('shift_state',p_state.SHIFT_STATE);j.put('work_state',p_state.WORK_STATE);
  j.put('warehouse_id',p_state.WARE_ID);j.put('resource_session_id',p_state.RESOURCE_SESSION_ID);j.put('resource_id',p_state.RESOURCE_ID);
  j.put('source_kind',p_state.SOURCE_KIND);j.put('source_id',p_state.SOURCE_ID);
  j.put('shift_started_at',stamp(p_state.SHIFT_START_AT));j.put('work_started_at',stamp(p_state.WORK_START_AT));
  j.put('pause_started_at',stamp(p_state.PAUSE_START_AT));j.put('last_event_at',stamp(p_state.LAST_EVENT_AT));
  j.put('work_coverage_certified',false);j.put('source_mode','MANUAL_CONFIRMED');return j;
 end;
 procedure current_state(p_actor varchar2,p_result out clob)is s RRL_PICKER_TIME_STREAM%rowtype;begin
  load_state(p_actor,s);if s.WARE_ID is not null then RRL_PICKER_TIME_AUTH.ware_required(p_actor,s.WARE_ID);end if;
  p_result:=state_json(s).to_clob;
 end;
 procedure read_window(p_actor varchar2,p_start varchar2,p_finish varchar2,p_result out clob)is
  left_at timestamp with time zone;right_at timestamp with time zone;observed timestamp with time zone:=systimestamp;
  s RRL_PICKER_TIME_STREAM%rowtype;j json_object_t:=json_object_t();items json_array_t:=json_array_t();item json_object_t;
  type ware_set is table of boolean index by varchar2(100);checked ware_set;k varchar2(100);n number:=0;
 begin
  load_state(p_actor,s);
  left_at:=to_timestamp_tz(p_start,'FXYYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');right_at:=to_timestamp_tz(p_finish,'FXYYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM');
  if left_at is null or right_at is null or right_at<=left_at or right_at>left_at+numtodsinterval(31,'DAY')then raise_application_error(-20886,'PICKER_TIME_WINDOW_BOUND_31_DAYS');end if;
  if s.WARE_ID is not null then RRL_PICKER_TIME_AUTH.ware_required(p_actor,s.WARE_ID);checked(RRL_STOCK_PLAN_HELPER.decimal_text(s.WARE_ID)):=true;end if;
  for x in(select *from RRL_PICKER_TIME_SPAN where OPERATOR_ID=p_actor and START_AT<right_at and FINISH_AT>left_at and FINISH_AT<=observed
   order by START_AT,FINISH_AT,SPAN_ID fetch first 5001 rows only)loop
   n:=n+1;if n>5000 then raise_application_error(-20886,'PICKER_TIME_SPAN_BOUND_5000');end if;
   k:=RRL_STOCK_PLAN_HELPER.decimal_text(x.WARE_ID);
   if not checked.exists(k)then RRL_PICKER_TIME_AUTH.ware_required(p_actor,x.WARE_ID);checked(k):=true;end if;
   k:=k||':'||x.SOURCE_KIND;
   if x.SOURCE_KIND!='RESOURCE_SESSION'and not checked.exists(k)then RRL_PICKER_TIME_AUTH.source_permission(p_actor,x.SOURCE_KIND,x.WARE_ID);checked(k):=true;end if;
   item:=json_object_t();item.put('span_id',x.SPAN_ID);item.put('kind',x.KIND);item.put('operator_id',x.OPERATOR_ID);
   item.put('warehouse_id',x.WARE_ID);item.put('resource_session_id',x.RESOURCE_SESSION_ID);
   item.put('source_kind',x.SOURCE_KIND);item.put('source_id',x.SOURCE_ID);item.put('start_at',stamp(x.START_AT));item.put('finish_at',stamp(x.FINISH_AT));
   item.put('start_operation_id',x.START_OPERATION_ID);item.put('finish_operation_id',x.FINISH_OPERATION_ID);item.put('source_mode',x.SOURCE_MODE);items.append(item);
  end loop;
  j.put('operator_id',p_actor);j.put('report_start',stamp(left_at));j.put('report_finish',stamp(right_at));j.put('as_of',stamp(observed));
  j.put('state',state_json(s));j.put('spans',items);j.put('work_coverage_certified',false);
  j.put('actual_shift_coverage','CLOSED_CONFIRMED_WINDOWS_ONLY');j.put('snapshot','ORACLE_READ_ONLY');p_result:=j.to_clob;
 end;
end;
/
