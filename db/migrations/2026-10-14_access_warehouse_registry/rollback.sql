-- Export changed scope metadata first. Do not delete adopted identities.
delete from RRL_ACCESS_OBJECT o where KIND='WAREHOUSE' and VERSION_NO=1 and exists(select 1 from RRL_WARES w where to_char(w.ID)=o.OBJECT_ID) and not exists(select 1 from RRL_ACCESS_ASSIGNMENT a where a.SCOPE_KIND='WAREHOUSE' and a.SCOPE_ID=o.OBJECT_ID) and not exists(select 1 from RRL_ACCESS_GROUP_MEMBER m where m.KIND=o.KIND and m.OBJECT_ID=o.OBJECT_ID) and not exists(select 1 from RRL_ACCESS_OBJECT c where c.PARENT_KIND=o.KIND and c.PARENT_ID=o.OBJECT_ID);
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-14-access-warehouse-registry';
commit;
