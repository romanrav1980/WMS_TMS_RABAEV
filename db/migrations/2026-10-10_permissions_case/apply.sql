@@001_rights.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin select count(*) into n from USER_OBJECTS where OBJECT_NAME='RRL_HAS_WRIGHT' and OBJECT_TYPE='FUNCTION' and STATUS='VALID';
if n!=1 then raise_application_error(-20808,'RIGHTS_CASE_CONTRACT_INVALID');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-10-084-rights-case-contract' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing rights helper accepts admin upper-case grants and canonical lower-case API keys; active unique RUSERS actor and GLOBAL_ADMIN semantics retained',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
