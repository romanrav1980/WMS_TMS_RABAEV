whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;
/
-- Package bodies/spec only, no data. Pool reservations created meanwhile stay as they are (SOFT, recalculated by the old pool).
@@before_pool_cmd.sql
@@before_pool_read.sql
@@before_ctx_spec.sql
@@before_ctx_body.sql
@@recompile.sql
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-trade-pool-eligibility' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Trade rows get common-pool shares only from compatible physical classes',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
