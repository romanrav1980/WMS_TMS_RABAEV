whenever sqlerror exit failure rollback
@@000_preflight.sql
@@001_schema.sql
@@002_adopt.sql
@@003_reserve_core.sql
@@004_picking.sql
@@005_wave_launch.sql
@@006_pick_context.sql
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-trade-topup-wave-adoption' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Atomic take-over of a top-up HARD hold by its own SAP order wave; planning sees only its own hold',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
