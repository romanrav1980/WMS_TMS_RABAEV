whenever sqlerror exit failure rollback
@@001_body.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-21-tradecase-case-receipt-modes' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'CASE piece selection is independent of receipt BOX/PALLET scan mode; fixed EA and one TOBACCO profile retained',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
