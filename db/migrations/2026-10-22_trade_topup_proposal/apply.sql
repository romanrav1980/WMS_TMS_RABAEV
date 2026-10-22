whenever sqlerror exit failure rollback
@@000_preflight.sql
@@001_schema.sql
@@008_core_access.sql
@@002_read.sql
@@003_api.sql
@@004_cmd.sql
@@005_posting_api.sql
@@006_trade_guard.sql
@@007_pick_context.sql
begin dbms_utility.compile_schema(user,false);end;
/
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-trade-topup-proposal' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Durable top-up proposals, atomic hold+SAP request confirmation, own release, wave adoption gate',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
