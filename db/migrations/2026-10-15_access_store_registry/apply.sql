-- MIGRATION_ID: 2026-10-15-access-store-registry
-- Source store key is legacy ADDR, not an invented numeric ID. ASCII scope identity is SHA256(UTF8(ADDR)).
insert into RRL_ACCESS_OBJECT(KIND,OBJECT_ID,TITLE,ACTIVE,VERSION_NO)
 select 'REGION',lower(rawtohex(standard_hash(utl_i18n.string_to_raw(REGION,'AL32UTF8'),'SHA256'))),to_nchar(substr(REGION,1,200)),1,1
 from(select distinct REGION from RRL_ADDR where nvl(DELETED3,0)=0 and REGION is not null) a
 where not exists(select 1 from RRL_ACCESS_OBJECT o where o.KIND='REGION' and o.OBJECT_ID=lower(rawtohex(standard_hash(utl_i18n.string_to_raw(a.REGION,'AL32UTF8'),'SHA256'))));
insert into RRL_ACCESS_OBJECT(KIND,OBJECT_ID,TITLE,PARENT_KIND,PARENT_ID,ACTIVE,VERSION_NO)
 select 'STORE',lower(rawtohex(standard_hash(utl_i18n.string_to_raw(a.ADDR,'AL32UTF8'),'SHA256'))),to_nchar(substr(a.ADDR,1,200)),
 case when a.REGION is not null then 'REGION' end,
 case when a.REGION is not null then lower(rawtohex(standard_hash(utl_i18n.string_to_raw(a.REGION,'AL32UTF8'),'SHA256')))end,1,1
 from RRL_ADDR a where nvl(a.DELETED3,0)=0 and a.ADDR is not null
 and not exists(select 1 from RRL_ACCESS_OBJECT o where o.KIND='STORE' and o.OBJECT_ID=lower(rawtohex(standard_hash(utl_i18n.string_to_raw(a.ADDR,'AL32UTF8'),'SHA256'))));
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-access-store-registry' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Store and region scope references from existing ADDR identity; no user assignments',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
