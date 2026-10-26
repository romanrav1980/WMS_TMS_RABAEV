whenever sqlerror exit failure rollback
@@000_preflight.sql
@@001_event_spec.sql
@@002_event_body.sql
@@003_depart.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-26-trade-shipment-events' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Freeze actual departing TRADECASE codes in independent SAP and SKM outbox events in the native departure transaction',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
