create or replace package RRL_STOCK_CTX_API authid definer
 accessible by(package RRL_STOCK_SETTING_API,package RRL_STOCK_MES_CANCEL_CMD,package RRL_STOCK_MES_SUPPLY_CMD,package RRL_STOCK_DOC_RESERVE_CMD,package RRL_STOCK_BALANCE_CORE,package RRL_STOCK_RESERVE_CORE,package RRL_STOCK_RESERVATION_CMD,package RRL_STOCK_UNIT_CORE,package RRL_STOCK_TRANSFER_CORE,package RRL_STOCK_CONFIG_API,package RRL_STOCK_POSTING_API,package RRL_STOCK_OPERATION_CORE) as
 procedure open_operation(p_operation varchar2,p_mode varchar2 default 'EXPLICIT');
 procedure open_configuration(p_actor varchar2,p_permission varchar2);
 procedure begin_effect(p_kind varchar2,p_uid varchar2 default null,p_cell varchar2 default null,p_row_id number default null);
 procedure begin_staging(p_uid varchar2,p_cell varchar2);
 procedure end_effect;
 procedure clear_operation;
end;
/
create or replace package body RRL_STOCK_CTX_API as
 procedure open_operation(p_operation varchar2,p_mode varchar2 default 'EXPLICIT') is v_state varchar2(20);
 begin
  select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if v_state!='ACTIVE' then raise_application_error(-20860,'STOCK_RELEASE_NOT_ACTIVE'); end if;
  if p_mode is null or p_mode not in('EXPLICIT','COMPAT') then raise_application_error(-20861,'STOCK_CONTEXT_MODE_INVALID'); end if;
  RRL_STOCK_LOCK_API.assert_held(10,RRL_STOCK_LOCK_API.resource_key('OP',p_operation));
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then raise_application_error(-20862,'POSTING_ALREADY_ENTERED'); end if;
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','OPERATION_ID',p_operation);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','TX_ID',dbms_transaction.local_transaction_id(false));
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','MODE',p_mode);
 end;
 procedure begin_effect(p_kind varchar2,p_uid varchar2 default null,p_cell varchar2 default null,p_row_id number default null) is v_tx varchar2(100);
 begin
  v_tx:=dbms_transaction.local_transaction_id(false);
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is null or v_tx is null or
   sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=v_tx
   or p_kind is null or p_kind not in('STOCK','JOURNAL','RESERVATION','UNIT') then raise_application_error(-20863,'EFFECT_CONTEXT_FORBIDDEN');end if;
  if sys_context('RRL_STOCK_WRITE_CTX','EFFECT') is not null then raise_application_error(-20862,'NESTED_EFFECT_FORBIDDEN');end if;
  if p_uid is not null then RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_uid));end if;
  if p_kind in('STOCK','JOURNAL','UNIT') and p_uid is null then raise_application_error(-20863,'EFFECT_UID_REQUIRED');end if;
  if p_kind='RESERVATION' then
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STOCK_RESERVATION',RRL_STOCK_PLAN_HELPER.decimal_text(p_row_id)));
  end if;
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT',p_kind);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_UID',p_uid);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_CELL',p_cell);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_ROW_ID',RRL_STOCK_PLAN_HELPER.decimal_text(p_row_id));
 end;
 procedure begin_staging(p_uid varchar2,p_cell varchar2) is
 begin
  begin_effect('UNIT',p_uid,p_cell);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT','RECEIPT_CAPTURE');
 end;
 procedure end_effect is
 begin
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT',null);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_UID',null);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_CELL',null);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','EFFECT_ROW_ID',null);
 end;
 procedure open_configuration(p_actor varchar2,p_permission varchar2) is
 begin
  if sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID') is not null then raise_application_error(-20862,'POSTING_ALREADY_ENTERED');end if;
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','TX_ID',dbms_transaction.local_transaction_id(false));
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','MODE','CONFIG');
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','ACTOR',p_actor);
  dbms_session.set_context('RRL_STOCK_WRITE_CTX','CONFIG_PERMISSION',p_permission);
 end;
 procedure clear_operation is
 begin
  dbms_session.clear_context('RRL_STOCK_WRITE_CTX',null);
 end;
end;
/
create or replace context RRL_STOCK_WRITE_CTX using RRL_STOCK_CTX_API;
