whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;
/
-- Package spec/bodies only, no data. Proposals saved meanwhile carry the new basis and must be recalculated under the old one.
@@before_cmd_body.sql
@@before_api_body.sql
@@before_read_spec.sql
@@before_read_body.sql
@@recompile.sql
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-topup-after-load' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Top-up allowed with main cargo loaded; refused after departure; confirm serialized with LOAD/DEPART',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
