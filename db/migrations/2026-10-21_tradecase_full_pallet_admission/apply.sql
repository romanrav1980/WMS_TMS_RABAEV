whenever sqlerror exit failure rollback
@@001_body.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-21-tradecase-full-pallet-admission' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Bound full pallet picking movement and shipment binding; native owner/MRC/expiry/buyout checks retained',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
