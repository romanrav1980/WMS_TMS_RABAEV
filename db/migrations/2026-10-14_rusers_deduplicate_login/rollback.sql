-- Explicit approval required to restore the deleted account. Backup contains original credential fields; never dump it to logs.
drop index RUSERS_LOGIN_UK;
create unique index RUSERS_ACTIVE_LOGIN_UK on RUSERS(case when nvl(DELETED,0)=0 then lower(trim(ID))end);
insert into RUSERS select b.* from RRL_RUSERS_DEDUP_BAK b where b.ID=N'KLAD_Uzenaliev' and not exists(select 1 from RUSERS r where r.ID=b.ID);
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-14-rusers-deduplicate-login';
commit;
