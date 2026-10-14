@@001_schema.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_CCTV_VIEWPOINT';
 if n!=1 then raise_application_error(-20808,'CCTV_CONFIGURATION_MISSING');end if;
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_CASE_PICK_SHORT' and COLUMN_NAME in('INVESTIGATION_VERSION','INVESTIGATION_STATUS');
 if n!=2 then raise_application_error(-20808,'SHORT_INVESTIGATION_COLUMNS_MISSING');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-028-short-investigation' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'CCTV archive links and versioned review journal for existing shortage incidents; no stock effects',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
