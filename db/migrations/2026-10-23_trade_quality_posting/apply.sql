whenever sqlerror exit failure rollback
@@000_preflight.sql
@@001_schema.sql
@@003_quality_case_api.sql
@@002_effect_core_spec.sql
@@004_quality_writeoff.sql
@@002_effect_core.sql
@@006_regulatory_stock_outbox.sql
@@005_trade_stock_guard.sql
@@007_stock_posting_api.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-trade-quality-posting' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'TRADECASE quality write-off posting kind and native quality hold enforcement',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
