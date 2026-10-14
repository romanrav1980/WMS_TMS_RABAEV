@@001_schema.sql
@@002_archive.sql
@@003_guards.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME='RRL_STORE_EVIDENCE_API' and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
if n!=2 then raise_application_error(-20808,'STORE_PHOTO_ARCHIVE_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-085-store-photo-archive' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Immutable original photo BLOB/hash/source/store/receiver association and bounded recovery, separate from stock transaction',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
