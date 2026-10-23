whenever sqlerror exit failure rollback
@@000_preflight.sql
@@001_schema.sql
@@002_unit_core_spec.sql
@@003_unit_core_body.sql
@@004_inventory_cmd_body.sql
begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;
/
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-inventory-found-units' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Inventory loss journal and restoration of the same marked units via INVENTORY_COUNT',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
