-- Source-stage rollback only. Never erase committed identities or switch an ACTIVE writer.
declare n number;
begin
 select count(*) into n from RRL_STOCK_RELEASE where RELEASE_ID=1 and STATE='PREPARED' and BASELINE_ID is null;
 if n!=1 then raise_application_error(-20808,'RUNTIME_ROLLBACK_REQUIRES_PREPARED_NO_BASELINE'); end if;
 select count(*) into n from RRL_STOCK_OPERATION;
 if n!=0 then raise_application_error(-20808,'PRESERVE_POSTED_OPERATIONS'); end if;
end;
/
drop package RRL_STOCK_POSTING_API;
drop package RRL_STOCK_MOVE_CORE;
drop package RRL_STOCK_COMMAND_PLAN;
drop package RRL_STOCK_LOCATION_CORE;
drop package RRL_STOCK_RESERVE_CORE;
drop package RRL_STOCK_OPERATION_CORE;
drop package RRL_STOCK_BALANCE_CORE;
drop context RRL_STOCK_WRITE_CTX;
drop package RRL_STOCK_CTX_API;
drop package RRL_STOCK_LOCK_API;
alter table RRL_STOCK_OPERATION drop column RESOLVED_PLAN_JSON;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-08-016-stock-command-runtime';
commit;
