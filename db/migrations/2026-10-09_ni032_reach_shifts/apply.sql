@@001_schema.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_RESOURCE_SHIFT' and COLUMN_NAME in('BASE_SHIFT_ID','REACH_SHIFT_ROLE','EXPECTED_DRIVERS');
 if n!=3 then raise_application_error(-20808,'REACH_SHIFT_METADATA_MISSING');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-026-reach-shifts' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Main reachtruck shift offsets and one/two duty drivers linked to existing warehouse shift',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
