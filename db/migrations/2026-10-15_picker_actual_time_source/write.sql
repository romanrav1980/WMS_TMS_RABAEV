create or replace package RRL_PICKER_TIME_WRITE authid definer accessible by(package RRL_PICKER_TIME_API) as
 procedure apply_transition(p_actor varchar2,p_action varchar2,p_operation varchar2,p_session number,p_ware number,p_resource number,
  p_kind varchar2,p_id number,p_reason nvarchar2,p_at timestamp with time zone,p_state in out RRL_PICKER_TIME_STREAM%rowtype);
end;
/
create or replace package body RRL_PICKER_TIME_WRITE as
 procedure closed_span(p_kind varchar2,p_start timestamp with time zone,p_finish timestamp with time zone,p_start_op varchar2,p_finish_op varchar2,
  s RRL_PICKER_TIME_STREAM%rowtype)is source_kind varchar2(24):=s.SOURCE_KIND;source_id number:=s.SOURCE_ID;begin
  if p_start is null or p_finish<p_start then raise_application_error(-20886,'PICKER_TIME_CLOCK_REGRESSION');end if;
  if p_finish=p_start then return;end if;
  if p_kind='ACTUAL_SHIFT'then source_kind:='RESOURCE_SESSION';source_id:=s.RESOURCE_SESSION_ID;end if;
  insert into RRL_PICKER_TIME_SPAN(SPAN_ID,OPERATOR_ID,KIND,WARE_ID,RESOURCE_SESSION_ID,SOURCE_KIND,SOURCE_ID,START_AT,FINISH_AT,START_OPERATION_ID,FINISH_OPERATION_ID,SOURCE_MODE)
   values(p_finish_op||':'||p_kind,s.OPERATOR_ID,p_kind,s.WARE_ID,s.RESOURCE_SESSION_ID,source_kind,source_id,p_start,p_finish,p_start_op,p_finish_op,'MANUAL_CONFIRMED');
 end;
 procedure apply_transition(p_actor varchar2,p_action varchar2,p_operation varchar2,p_session number,p_ware number,p_resource number,
  p_kind varchar2,p_id number,p_reason nvarchar2,p_at timestamp with time zone,p_state in out RRL_PICKER_TIME_STREAM%rowtype)is
  old_state RRL_PICKER_TIME_STREAM%rowtype:=p_state;
 begin
  if p_state.LAST_EVENT_AT is not null and p_at<p_state.LAST_EVENT_AT then raise_application_error(-20886,'PICKER_TIME_CLOCK_REGRESSION');end if;
  if p_action='ACTUAL_SHIFT_START'then
   if p_state.SHIFT_STATE!='OFF'or p_state.WORK_STATE!='IDLE'then raise_application_error(-20886,'PICKER_TIME_TRANSITION_NOT_ALLOWED');end if;
   p_state.SHIFT_STATE:='OPEN';p_state.SHIFT_START_AT:=p_at;p_state.SHIFT_START_OP:=p_operation;
   p_state.WARE_ID:=p_ware;p_state.RESOURCE_SESSION_ID:=p_session;p_state.RESOURCE_ID:=p_resource;
  else
   if p_state.SHIFT_STATE!='OPEN'then raise_application_error(-20886,'PICKER_TIME_ACTUAL_SHIFT_NOT_OPEN');end if;
   if p_state.RESOURCE_SESSION_ID is null or p_state.RESOURCE_SESSION_ID!=p_session or p_state.WARE_ID is null or p_state.WARE_ID!=p_ware
    or p_state.RESOURCE_ID is null or p_state.RESOURCE_ID!=p_resource then raise_application_error(-20886,'PICKER_TIME_SESSION_CHANGED');end if;
   if p_action='WORK_START'then
    if p_state.WORK_STATE!='IDLE'then raise_application_error(-20886,'PICKER_TIME_TRANSITION_NOT_ALLOWED');end if;
    p_state.WORK_STATE:='WORK';p_state.WORK_START_AT:=p_at;p_state.WORK_START_OP:=p_operation;p_state.SOURCE_KIND:=p_kind;p_state.SOURCE_ID:=p_id;
   elsif p_action='ACTUAL_SHIFT_FINISH'then
    if p_state.WORK_STATE!='IDLE'then raise_application_error(-20886,'PICKER_TIME_WORK_FINISH_REQUIRED');end if;
    p_state.SHIFT_STATE:='OFF';p_state.SHIFT_START_AT:=null;p_state.SHIFT_START_OP:=null;
    p_state.WARE_ID:=null;p_state.RESOURCE_SESSION_ID:=null;p_state.RESOURCE_ID:=null;
   else
    if p_state.SOURCE_KIND is null or p_state.SOURCE_KIND!=p_kind or p_state.SOURCE_ID is null or p_state.SOURCE_ID!=p_id then raise_application_error(-20886,'PICKER_TIME_SOURCE_CHANGED');end if;
    if p_action='PAUSE'and p_state.WORK_STATE='WORK'then
     p_state.WORK_STATE:='PAUSED';p_state.PAUSE_START_AT:=p_at;p_state.PAUSE_START_OP:=p_operation;
    elsif p_action='RESUME'and p_state.WORK_STATE='PAUSED'then
     p_state.WORK_STATE:='WORK';p_state.PAUSE_START_AT:=null;p_state.PAUSE_START_OP:=null;
    elsif p_action='WORK_FINISH'and p_state.WORK_STATE in('WORK','PAUSED')then
     p_state.WORK_STATE:='IDLE';p_state.WORK_START_AT:=null;p_state.WORK_START_OP:=null;p_state.PAUSE_START_AT:=null;p_state.PAUSE_START_OP:=null;p_state.SOURCE_KIND:=null;p_state.SOURCE_ID:=null;
    else raise_application_error(-20886,'PICKER_TIME_TRANSITION_NOT_ALLOWED');end if;
   end if;
  end if;
  p_state.STREAM_VERSION:=old_state.STREAM_VERSION+1;p_state.LAST_EVENT_AT:=p_at;
  if old_state.STREAM_VERSION=0 then insert into RRL_PICKER_TIME_STREAM values p_state;end if;
  insert into RRL_PICKER_TIME_EVENT(OPERATION_ID,OPERATOR_ID,WARE_ID,RESOURCE_SESSION_ID,RESOURCE_ID,ACTOR_ID,ACTION,EFFECTIVE_AT,BEFORE_VERSION,AFTER_VERSION,SOURCE_KIND,SOURCE_ID,SOURCE_MODE,REASON)
   values(p_operation,p_actor,p_ware,p_session,p_resource,p_actor,p_action,p_at,old_state.STREAM_VERSION,p_state.STREAM_VERSION,p_kind,p_id,'MANUAL_CONFIRMED',p_reason);
  if p_action='ACTUAL_SHIFT_FINISH'then closed_span('ACTUAL_SHIFT',old_state.SHIFT_START_AT,p_at,old_state.SHIFT_START_OP,p_operation,old_state);
  elsif p_action='RESUME'then closed_span('PAUSE',old_state.PAUSE_START_AT,p_at,old_state.PAUSE_START_OP,p_operation,old_state);
  elsif p_action='WORK_FINISH'then
   if old_state.WORK_STATE='PAUSED'then closed_span('PAUSE',old_state.PAUSE_START_AT,p_at,old_state.PAUSE_START_OP,p_operation,old_state);end if;
   closed_span('WORK',old_state.WORK_START_AT,p_at,old_state.WORK_START_OP,p_operation,old_state);
  end if;
  if old_state.STREAM_VERSION>0 then update RRL_PICKER_TIME_STREAM set row=p_state where OPERATOR_ID=p_actor;end if;
 end;
end;
/
