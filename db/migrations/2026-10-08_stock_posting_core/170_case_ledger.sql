declare n number;v varchar2(20);begin
 select STATE into v from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v!='PREPARED' then raise_application_error(-20808,'DORMANT_LEDGER_REQUIRES_PREPARED');end if;
 select count(*) into n from USER_OBJECTS where STATUS!='VALID' and OBJECT_NAME in('RRL_STOCK_CASE_PICK_CMD','RRL_STOCK_CASE_MOVE_CMD','RRL_CASE_CARRIER_LOT_GUARD');
 if n>0 then raise_application_error(-20808,'CASE_COMPONENT_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-062-case-carrier-schema' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant CASE extension: case-carrier-schema',sysdate,user,'159_case_carrier_schema.sql','159_case_carrier_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-063-case-pick-command' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant CASE extension: case-pick-command',sysdate,user,'161_case_pick_core_apply.sql','161_case_pick_core_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-064-case-scanned-sources' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant CASE extension: case-scanned-sources',sysdate,user,'162_case_scanned_sources_apply.sql','162_case_scanned_sources_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-065-case-short-metadata' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant CASE extension: case-short-metadata',sysdate,user,'163_case_short_metadata_apply.sql','163_case_short_metadata_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-066-case-unit-batches' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant CASE extension: case-unit-batches',sysdate,user,'164_case_unit_batches_apply.sql','164_case_unit_batches_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-067-case-transit-cells' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant CASE extension: case-transit-cells',sysdate,user,'165_case_transit_cells.sql','165_case_transit_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-068-case-transit-movement' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant CASE extension: case-transit-movement',sysdate,user,'166_case_transit_apply.sql','166_case_transit_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-069-case-carrier-move' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant CASE extension: case-carrier-move',sysdate,user,'168_case_carrier_move_apply.sql','168_case_carrier_move_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-070-case-lot-facts' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant CASE extension: case-lot-facts',sysdate,user,'169_case_lot_facts_apply.sql','169_case_lot_facts_rollback.sql','APPLIED');
commit;
