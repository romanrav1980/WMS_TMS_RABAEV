declare n number;v varchar2(20);begin
 select STATE into v from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v!='PREPARED' then raise_application_error(-20808,'DORMANT_LEDGER_REQUIRES_PREPARED');end if;
 select count(*) into n from USER_OBJECTS where STATUS!='VALID' and OBJECT_NAME in('RRL_STOCK_CASE_SHORT_CMD','ARTICULS','ARTICULS_SP_OLD','RRL_CLEAR_OTBOR_CELL','RRL_STOCK_BALANCE_CORE','RRL_STOCK_PALLET_UOM','RRL_PALLET_PACK_GUARD');
 if n>0 then raise_application_error(-20808,'CURRENT_COMPONENT_INVALID');end if;
end;
/
update RRL_STOCK_WRITER_REGISTRY set STATE='RETIRED',ADAPTER_REFERENCE='db/migrations/2026-10-08_stock_posting_core/176_clear_entrypoint.sql; inventory-count.html',UPDATED_AT=systimestamp
 where WRITER_KEY='ORACLE:FUNCTION:RRL_CLEAR_OTBOR_CELL';
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-071-case-short-approval' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant posting extension: case-short-approval',sysdate,user,'172_case_short_approval_apply.sql','172_case_short_approval_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-072-article-native' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant posting extension: article-native',sysdate,user,'175_article_native_apply.sql','175_article_native_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-073-clear-retirement' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant posting extension: clear-retirement',sysdate,user,'176_clear_retirement_apply.sql','176_clear_retirement_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-074-pallet-pack-schema' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant posting extension: pallet-pack-schema',sysdate,user,'177_pallet_pack_schema.sql','177_pallet_pack_schema_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-075-pallet-pack-snapshot' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Dormant posting extension: pallet-pack-snapshot',sysdate,user,'178_pallet_pack_snapshot_apply.sql','178_pallet_pack_snapshot_rollback.sql','APPLIED');
commit;
