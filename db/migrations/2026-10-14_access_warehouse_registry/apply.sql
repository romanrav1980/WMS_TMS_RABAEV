-- MIGRATION_ID: 2026-10-14-access-warehouse-registry
-- Only additive scope reference mappings; RRL_WARES remains the master, users unchanged.
insert into RRL_ACCESS_OBJECT(KIND,OBJECT_ID,TITLE,ACTIVE,VERSION_NO)
 select 'WAREHOUSE',to_char(w.ID),coalesce(to_nchar(w.NAME),to_nchar(to_char(w.ID))),1,1 from RRL_WARES w
 where w.ID is not null and not exists(select 1 from RRL_ACCESS_OBJECT o where o.KIND='WAREHOUSE' and o.OBJECT_ID=to_char(w.ID));
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-14-access-warehouse-registry' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Initial warehouse scope identity references; no assignments',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;

