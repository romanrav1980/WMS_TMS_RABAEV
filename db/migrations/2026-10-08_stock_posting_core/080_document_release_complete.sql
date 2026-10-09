declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME like 'RRL_STOCK_%' and OBJECT_TYPE in('PACKAGE','PACKAGE BODY','TRIGGER') and STATUS!='VALID';
 if n>0 then raise_application_error(-20808,'DOCUMENT_RELEASE_PACKAGES_NOT_VALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-034-document-reservation-release' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Document-scoped atomic HARD/SOFT release; document-before-reservation actual row locks; no direct status-only H changes',sysdate,user,'080_document_release_apply.sql','080_document_release_rollback.sql','APPLIED');
commit;
