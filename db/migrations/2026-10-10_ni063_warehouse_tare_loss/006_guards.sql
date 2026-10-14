create or replace procedure RRL_TARE_ASSERT_WRITE(p_table varchar2,p_key varchar2,p_kind varchar2) authid definer is
 op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);v_state varchar2(20);
begin
 if op is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID') is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false) then raise_application_error(-20863,'TARE_ROOT_TRANSACTION_REQUIRED');end if;
 select COMMAND_TYPE,STATE into v_kind,v_state from RRL_STOCK_OPERATION where OPERATION_ID=op;
 if v_state!='IN_FLIGHT' or(v_kind!=p_kind and not(p_kind='COUNT_OR_ACCEPT' and v_kind in('TARE_COUNT','TARE_ACCEPT','TARE_DAMAGE','TARE_WRITE_OFF','TARE_BOOK','TARE_BOOK_CANCEL','TARE_LOSS_REPORT','TARE_LOSS_DECIDE')))then raise_application_error(-20863,'TARE_ROOT_COMMAND_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW',p_table,p_key));
end;
/
create or replace trigger RRL_TARE_BALANCE_GUARD before insert or update or delete on RRL_TARE_BALANCE for each row
begin
 if deleting then raise_application_error(-20863,'TARE_BALANCE_DELETE_DENIED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_BALANCE',rawtohex(:new.BALANCE_KEY),'COUNT_OR_ACCEPT');
 if :new.BALANCE_KEY!=RRL_TARE_BALANCE_KEY(:new.OWNER_WARE_ID,:new.PALLET_TYPE_ID,:new.CONDITION_CODE,:new.CUSTODIAN_KIND,:new.CUSTODIAN_ID) or :new.LAST_OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_BALANCE_IDENTITY_CONFLICT');end if;
 if inserting and :new.BALANCE_VERSION!=1 then raise_application_error(-20863,'TARE_INITIAL_VERSION_REQUIRED');end if;
 if updating and(:new.BALANCE_KEY!=:old.BALANCE_KEY or :new.OWNER_WARE_ID!=:old.OWNER_WARE_ID or :new.PALLET_TYPE_ID!=:old.PALLET_TYPE_ID or :new.CONDITION_CODE!=:old.CONDITION_CODE or :new.CUSTODIAN_KIND!=:old.CUSTODIAN_KIND or :new.CUSTODIAN_ID!=:old.CUSTODIAN_ID or :new.BALANCE_VERSION!=:old.BALANCE_VERSION+1)then raise_application_error(-20863,'TARE_BALANCE_IDENTITY_VERSION_IMMUTABLE');end if;
end;
/
create or replace trigger RRL_TARE_OFFER_GUARD before insert or update or delete on RRL_TARE_OFFER for each row
begin
 if not inserting then raise_application_error(-20863,'TARE_HISTORY_IMMUTABLE');end if;
 if :new.OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_ROOT_OPERATION_REQUIRED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_OFFER',:new.OPERATION_ID,'TARE_OFFER');
end;
/
create or replace trigger RRL_TARE_ACCEPT_GUARD before insert or update or delete on RRL_TARE_ACCEPT for each row
begin
 if not inserting then raise_application_error(-20863,'TARE_HISTORY_IMMUTABLE');end if;
 if :new.OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_ROOT_OPERATION_REQUIRED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_ACCEPT',:new.OPERATION_ID,'TARE_ACCEPT');
end;
/
create or replace trigger RRL_TARE_JOURNAL_GUARD before insert or update or delete on RRL_TARE_JOURNAL for each row
begin
 if not inserting then raise_application_error(-20863,'TARE_HISTORY_IMMUTABLE');end if;
 if :new.OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_ROOT_OPERATION_REQUIRED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_JOURNAL',:new.OPERATION_ID,'COUNT_OR_ACCEPT');
end;
/
create or replace trigger RRL_TARE_RESOLUTION_GUARD before insert or update or delete on RRL_TARE_RESOLUTION for each row
declare v_kind varchar2(80);
begin
 if not inserting then raise_application_error(-20863,'TARE_RESOLUTION_HISTORY_IMMUTABLE');end if;
 if :new.OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')then raise_application_error(-20863,'TARE_ROOT_OPERATION_REQUIRED');end if;
 v_kind:=case when :new.RESOLUTION_KIND='DAMAGE' then 'TARE_DAMAGE' else 'TARE_WRITE_OFF' end;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_RESOLUTION',:new.OPERATION_ID,v_kind);
end;
/

create or replace trigger RRL_TARE_LOSS_CLAIM_GUARD before insert or update or delete on RRL_TARE_LOSS_CLAIM for each row
begin
 if not inserting then raise_application_error(-20863,'TARE_LOSS_HISTORY_IMMUTABLE');end if;
 if :new.OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'TARE_LOSS_ROOT_REQUIRED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_LOSS_CLAIM',:new.OPERATION_ID,'TARE_LOSS_REPORT');
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_BALANCE',rawtohex(:new.BALANCE_KEY)));
end;
/
create or replace trigger RRL_TARE_LOSS_DEC_GUARD before insert or update or delete on RRL_TARE_LOSS_DECISION for each row
declare original_actor nvarchar2(50);v_key raw(32);
begin
 if not inserting then raise_application_error(-20863,'TARE_LOSS_HISTORY_IMMUTABLE');end if;
 if :new.OPERATION_ID!=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID')or :new.ACTOR!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')then raise_application_error(-20863,'TARE_LOSS_ROOT_REQUIRED');end if;
 RRL_TARE_ASSERT_WRITE('RRL_TARE_LOSS_DECISION',:new.OPERATION_ID,'TARE_LOSS_DECIDE');
 select ACTOR,BALANCE_KEY into original_actor,v_key from RRL_TARE_LOSS_CLAIM where OPERATION_ID=:new.CLAIM_OPERATION_ID;
 if original_actor=:new.ACTOR then raise_application_error(-20882,'TARE_INDEPENDENT_LOSS_DECISION_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_LOSS_CLAIM',:new.CLAIM_OPERATION_ID));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_TARE_BALANCE',rawtohex(v_key)));
end;
/
