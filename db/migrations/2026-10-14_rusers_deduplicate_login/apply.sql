-- MIGRATION_ID: 2026-10-14-rusers-deduplicate-login
-- Explicit owner request: remove duplicate; preserve the active account and backup the exact deleted row.
begin if user!='RABAEV' then raise_application_error(-20801,'RABAEV_ONLY');end if;end;
/
create table RRL_RUSERS_DEDUP_BAK as select * from RUSERS where 1=0;
lock table RUSERS in exclusive mode wait 5;
declare n number;begin
 select count(*)into n from RUSERS where ID=N'KLAD_UZENALIEV' and nvl(DELETED,0)=0;
 if n!=1 then raise_application_error(-20861,'SURVIVOR_NOT_UNIQUE');end if;
 select count(*)into n from RUSERS where ID=N'KLAD_Uzenaliev' and nvl(DELETED,0)=1;
 if n!=1 then raise_application_error(-20861,'DUPLICATE_CHANGED');end if;
 select count(*)into n from RRL_ACCESS_ASSIGNMENT where USERNAME=N'KLAD_Uzenaliev';
 if n!=0 then raise_application_error(-20861,'DUPLICATE_REFERENCED');end if;
 insert into RRL_RUSERS_DEDUP_BAK select * from RUSERS where ID=N'KLAD_Uzenaliev' and nvl(DELETED,0)=1;
 delete from RUSERS where ID=N'KLAD_Uzenaliev' and nvl(DELETED,0)=1;
 if sql%rowcount!=1 then raise_application_error(-20861,'DELETE_COUNT_MISMATCH');end if;
end;
/
commit;
create unique index RUSERS_LOGIN_UK on RUSERS(lower(trim(ID)));
drop index RUSERS_ACTIVE_LOGIN_UK;
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-14-rusers-deduplicate-login' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Remove one deleted case duplicate; backup row retained; enforce normalized login uniqueness',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
