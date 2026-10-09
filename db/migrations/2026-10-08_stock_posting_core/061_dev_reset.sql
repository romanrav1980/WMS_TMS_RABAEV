-- Explicit owner authorization: dedicated test ORCL; remove stock and movement history.
-- No VM/database copy, no quantity reconstruction. Keep pallets and business documents.
declare v_state varchar2(20);v_n number;v_stock number;v_events number;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20808,'WRONG_DEV_RESET_TARGET');end if;
 select STATE into v_state from RRL_STOCK_RELEASE where RELEASE_ID=1 for update;
 if v_state!='PREPARED' then raise_application_error(-20808,'DEV_RESET_REQUIRES_PREPARED');end if;
 select count(*) into v_n from RRL_STOCK_OPERATION;
 if v_n!=0 then raise_application_error(-20808,'POSTED_OPERATIONS_REQUIRE_EXPLICIT_FULL_RESET');end if;
 select count(*) into v_n from RRL_WMS_RECEIPT_UNIT;
 if v_n!=0 then raise_application_error(-20808,'UNIT_RESET_SCOPE_REQUIRED');end if;
 select count(*) into v_n from RRL_STOCK_RESERVATION where RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING');
 if v_n!=0 then raise_application_error(-20808,'HARD_RESET_SCOPE_REQUIRED');end if;
 execute immediate 'lock table RRL_EVENTS in exclusive mode wait 3';
 execute immediate 'lock table RRL_REMAINS in exclusive mode wait 3';
 select count(*) into v_stock from RRL_REMAINS;
 select count(*) into v_events from RRL_EVENTS;
 delete from RRL_EVENTS;
 delete from RRL_REMAINS;
 insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values('2026-10-08-024-dev-stock-movement-reset',
  'Owner-authorized test reset; deleted stock rows='||v_stock||', journal rows='||v_events||'; irreversible after commit',
  sysdate,user,'061_dev_reset.sql','061_dev_reset_rollback.sql','APPLIED');
end;
/
commit;
