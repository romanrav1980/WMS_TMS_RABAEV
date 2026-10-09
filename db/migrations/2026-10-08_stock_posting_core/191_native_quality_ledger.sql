declare n number;v varchar2(20);begin
 select STATE into v from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v!='PREPARED' then raise_application_error(-20808,'DORMANT_LEDGER_REQUIRES_PREPARED');end if;
 select count(*) into n from USER_OBJECTS where STATUS!='VALID' and OBJECT_NAME in('RRL_STOCK_PALLET_QC_CMD','RRL_STOCK_QUALITY_ENTRY','REMAINS','RRL_STOCK_SHIPPING_CORE','RRL_STOCK_POSTING_API','RRL_SET_SCAN_PROOVE','RRL_SET_SCAN_PROOVE2','RRL_TRIAL_BY_WEIGHT','RRL_TRIAL_BY_WEIGHT2','RRL_UPDATE_PALLET_ROW2','RRL_UPDATE_PALLET_ROW3');
 if n>0 then raise_application_error(-20808,'CURRENT_COMPONENT_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-076-remains-move' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant posting extension: remains-move',sysdate,user,'181_remains_move_apply.sql','181_remains_move_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-077-internal-null-unit' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant posting extension: internal-null-unit',sysdate,user,'182_internal_null_unit_apply.sql','182_internal_null_unit_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-078-pallet-quality-core' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant posting extension: pallet-quality-core',sysdate,user,'185_pallet_quality_core_apply.sql','185_pallet_quality_core_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-079-quality-native' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant posting extension: quality-native',sysdate,user,'186_quality_native_apply.sql','186_quality_native_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-080-quality-clients' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant posting extension: quality-clients',sysdate,user,'187_quality_metadata_clients_apply.sql','187_quality_metadata_clients_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-081-terminal-quality-audit' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant posting extension: terminal-quality-audit',sysdate,user,'188_terminal_quality_audit_apply.sql','188_terminal_quality_audit_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-082-compile-replay' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant posting extension: compile-replay',sysdate,user,'189_compile_replay_apply.sql','189_compile_replay_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-083-supplier-return-source' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant posting extension: supplier-return-source',sysdate,user,'190_supplier_return_source_apply.sql','190_supplier_return_source_rollback.sql','APPLIED');
commit;
