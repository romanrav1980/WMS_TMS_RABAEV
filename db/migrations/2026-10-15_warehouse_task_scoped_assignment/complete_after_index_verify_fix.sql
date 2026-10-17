-- Original apply stopped after successful DDL/exact16 sources at index verifier counting two LOB indexes.
-- No DDL is repeated. Preserve original apply.sql/verify.sql as failed-at-verifier evidence.
@@after_source_guard.sql
declare n number;begin select count(*)into n from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-15-warehouse-task-scoped-assignment'and STATUS!='ROLLED_BACK';if n!=0 then raise_application_error(-20886,'WTASK_COMPLETION_LEDGER_NOT_EMPTY');end if;end;
/
@@verify_index_fix.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-warehouse-task-scoped-assignment'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user where d.STATUS='ROLLED_BACK'
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Scoped ordinary STOCK ASSIGN/START metadata; trigger-derived retained version sidecar; no stock writer',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
