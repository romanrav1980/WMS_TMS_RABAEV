-- Export adopted metadata first. Only remove unused initial references.
delete from RRL_ACCESS_OBJECT o where KIND='STORE' and VERSION_NO=1 and not exists(select 1 from RRL_ACCESS_ASSIGNMENT a where a.SCOPE_KIND='STORE' and a.SCOPE_ID=o.OBJECT_ID)
 and not exists(select 1 from RRL_ACCESS_GROUP_MEMBER m where m.KIND=o.KIND and m.OBJECT_ID=o.OBJECT_ID)
 and not exists(select 1 from RRL_ACCESS_BRANCH_MEMBER b where b.KIND=o.KIND and b.OBJECT_ID=o.OBJECT_ID);
delete from RRL_ACCESS_OBJECT o where KIND='REGION' and VERSION_NO=1 and not exists(select 1 from RRL_ACCESS_OBJECT c where c.PARENT_KIND='REGION' and c.PARENT_ID=o.OBJECT_ID)
 and not exists(select 1 from RRL_ACCESS_ASSIGNMENT a where a.SCOPE_KIND='REGION' and a.SCOPE_ID=o.OBJECT_ID)
 and not exists(select 1 from RRL_ACCESS_GROUP_MEMBER m where m.KIND=o.KIND and m.OBJECT_ID=o.OBJECT_ID)
 and not exists(select 1 from RRL_ACCESS_BRANCH_MEMBER b where b.KIND=o.KIND and b.OBJECT_ID=o.OBJECT_ID);
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-15-access-store-registry';
commit;
