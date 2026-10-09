create or replace package RRL_STOCK_OPERATION_CORE authid definer
 accessible by(package RRL_STOCK_POSTING_API) as
 procedure begin_operation(p_request clob,p_actor varchar2,p_operation varchar2,p_kind varchar2,p_replay out clob,p_plan clob default null);
 procedure finish_operation(p_operation varchar2,p_result clob);
end;
/
create or replace package body RRL_STOCK_OPERATION_CORE as
 procedure begin_operation(p_request clob,p_actor varchar2,p_operation varchar2,p_kind varchar2,p_replay out clob,p_plan clob default null) is
  v_saved clob;v_hash varchar2(64);v_actor varchar2(50);v_state varchar2(20);v_base varchar2(100);
 begin
  p_replay:=null;
  RRL_STOCK_LOCK_API.assert_held(10,RRL_STOCK_LOCK_API.resource_key('OP',p_operation));
  if p_request is null or dbms_lob.getlength(p_request)>4194304 or p_actor is null
   or length(p_actor)>50 or p_operation is null or length(p_operation)>100 then raise_application_error(-20871,'OPERATION_CONTRACT_INVALID'); end if;
  v_hash:=rawtohex(sys.dbms_crypto.hash(p_request,sys.dbms_crypto.hash_sh256));
  begin
   select CANONICAL_REQUEST,ACTOR,STATE,RESULT_JSON into v_saved,v_actor,v_state,p_replay
    from RRL_STOCK_OPERATION where OPERATION_ID=p_operation;
   if v_actor!=p_actor or dbms_lob.getlength(v_saved)!=dbms_lob.getlength(p_request)
    or dbms_lob.compare(v_saved,p_request)!=0 then raise_application_error(-20872,'OPERATION_CONFLICT'); end if;
   if v_state!='APPLIED' then raise_application_error(-20873,'UNFINISHED_OPERATION: unexpected committed envelope'); end if;
   return;
  exception when no_data_found then p_replay:=null;
  end;
  RRL_STOCK_CTX_API.open_operation(p_operation,case when p_kind='COMPAT_MANUAL_MOVE' then 'COMPAT' else 'EXPLICIT' end);
  select BASELINE_ID into v_base from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if v_base is null then raise_application_error(-20874,'BASELINE_REQUIRED'); end if;
  insert into RRL_STOCK_OPERATION(OPERATION_ID,CONTRACT_VERSION,COMMAND_TYPE,ACTOR,REQUEST_HASH,
   CANONICAL_REQUEST,RESOLVED_PLAN_JSON,STATE,BASELINE_ID) values(p_operation,2,p_kind,p_actor,v_hash,p_request,p_plan,'IN_FLIGHT',v_base);
 end;
 procedure finish_operation(p_operation varchar2,p_result clob) is
 begin
  RRL_STOCK_LOCK_API.assert_held(10,RRL_STOCK_LOCK_API.resource_key('OP',p_operation));
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null or
   sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')!=p_operation or p_result is null then
   raise_application_error(-20863,'STOCK_WRITE_FORBIDDEN');
  end if;
  update RRL_STOCK_OPERATION set RESULT_JSON=p_result,STATE='APPLIED',APPLIED_AT=systimestamp
   where OPERATION_ID=p_operation and STATE='IN_FLIGHT';
  if sql%rowcount!=1 then raise_application_error(-20875,'OPERATION_FINISH_CONFLICT'); end if;
 end;
end;
/
