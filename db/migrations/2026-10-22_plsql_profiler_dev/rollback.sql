whenever sqlerror exit failure rollback
declare n number;begin select count(*)into n from PLSQL_PROFILER_RUNS;if n<>0 then raise_application_error(-20999,'PROFILER_EVIDENCE_PREVENTS_DESTRUCTIVE_ROLLBACK');end if;end;
/
drop table PLSQL_PROFILER_DATA;
drop table PLSQL_PROFILER_UNITS;
drop table PLSQL_PROFILER_RUNS;
drop sequence PLSQL_PROFILER_RUNNUMBER;
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-plsql-profiler-dev' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Standard owner-only PL/SQL profiler storage; no business objects or privilege grants',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
