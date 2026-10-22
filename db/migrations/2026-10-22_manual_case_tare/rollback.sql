whenever sqlerror exit failure rollback
declare n number;begin select count(*)into n from RRL_CASE_MANUAL_TARE;if n<>0 then raise_application_error(-20999,'MANUAL_TARE_EVIDENCE_PREVENTS_DESTRUCTIVE_ROLLBACK');end if;end;
/
@@rrl_case_scale_admission_before.sql
@@rrl_wh_final_scale_admission_before.sql
drop trigger RRL_CASE_MANUAL_TARE_GUARD;
drop context RRL_MANUAL_TARE_CTX;
drop package RRL_CASE_MANUAL_TARE_API;
drop table RRL_CASE_MANUAL_TARE;
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-manual-case-tare' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Explicit manual empty tare, native append-only evidence and CASE weight admission',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
