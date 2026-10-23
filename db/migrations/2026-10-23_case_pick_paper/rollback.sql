whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;
/
-- No data is created by this migration; restore the owner first (it references the paper package), then drop the package.
@@before_rrl_stock_case_pick_cmd.sql
drop package RRL_CASE_PICK_PAPER;
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-case-pick-paper' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'CASE pick paper sheet line version checked by CASE_PICK_CONFIRM',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
