@@001_schema.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_CASE_PICK_SHORT' and COLUMN_NAME='CREATED_AT_INSTANT' and DATA_TYPE='TIMESTAMP(6) WITH TIME ZONE';
 if n!=1 then raise_application_error(-20808,'INCIDENT_INSTANT_COLUMN_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-037-incident-instants' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Capture new shortage report instants for archive windows; retain unqualified historical times without backfill',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
