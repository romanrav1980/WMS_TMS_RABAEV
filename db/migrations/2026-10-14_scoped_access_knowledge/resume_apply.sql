-- MIGRATION_ID: 2026-10-14-scoped-access-knowledge
begin if user!='RABAEV' then raise_application_error(-20801,'RABAEV_ONLY');end if;end;
/
@@resume_tables.sql
@@002_access_spec.sql
@@003_access_body.sql
@@004_knowledge.sql
@@005_seed.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-14-scoped-access-knowledge' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Additive scoped access and local knowledge; legacy users unchanged',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
