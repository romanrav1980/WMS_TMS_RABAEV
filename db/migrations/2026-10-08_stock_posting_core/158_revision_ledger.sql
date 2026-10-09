declare n number;v varchar2(20);begin
 select STATE into v from RRL_STOCK_RELEASE where RELEASE_ID=1;
 if v!='PREPARED' then raise_application_error(-20808,'DORMANT_LEDGER_REQUIRES_PREPARED');end if;
 select count(*) into n from USER_OBJECTS where STATUS!='VALID' and OBJECT_NAME in('REVIZION','REVIZION_SP_OLD','RRL_STOCK_REVISION_ENTRY','RRL_STOCK_INVENTORY_CMD','RRL_STOCK_INVENTORY_BIRTH');
 if n>0 then raise_application_error(-20808,'REVISION_COMPONENT_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-057-revision-count' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Revision count entrypoint, dormant installation',sysdate,user,'153_revision_count_apply.sql','153_revision_count_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-058-revision-row-projection' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Single-lot revision observation and row projection in posting transaction',sysdate,user,'154_revision_row_projection_apply.sql','154_revision_row_projection_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-059-revision-birth' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Explicit inventory pallet with weight packaging and defect facts',sysdate,user,'155_revision_birth_apply.sql','155_revision_birth_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-060-revision-native' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Existing REVIZION physical writers redirected to posting or measured lot UI',sysdate,user,'156_revision_native_apply.sql','156_revision_native_rollback.sql','APPLIED');
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-061-revision-distinct-pallets' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
 when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'Distinct explicitly identified pallets within same inventory document; rejects unrelated positive stock',sysdate,user,'157_revision_distinct_pallets_apply.sql','157_revision_distinct_pallets_rollback.sql','APPLIED');
commit;
