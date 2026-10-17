-- MIGRATION_ID: 2026-10-14-rusers-identity-constraints
-- Existing exact-ID unique index is reused; no legacy rows renamed, merged or deleted.
begin if user!='RABAEV' then raise_application_error(-20801,'RABAEV_ONLY');end if;end;
/
declare v_index varchar2(128);begin
 select min(i.INDEX_NAME)into v_index from user_indexes i where i.TABLE_NAME='RUSERS' and i.UNIQUENESS='UNIQUE'
 and(select count(*)from user_ind_columns c where c.INDEX_NAME=i.INDEX_NAME)=1
 and exists(select 1 from user_ind_columns c where c.INDEX_NAME=i.INDEX_NAME and c.COLUMN_NAME='ID');
 if v_index is null then
  execute immediate 'alter table RUSERS add constraint RUSERS_ID_UK unique(ID) enable validate';
 else
  execute immediate 'alter table RUSERS add constraint RUSERS_ID_UK unique(ID) using index '||dbms_assert.enquote_name(v_index,false)||' enable validate';
 end if;
end;
/
create unique index RUSERS_ACTIVE_LOGIN_UK on RUSERS(case when nvl(DELETED,0)=0 then lower(trim(ID)) end);
alter table RRL_ACCESS_ASSIGNMENT add constraint RRL_ACCESS_ASSIGN_USER_FK foreign key(USERNAME) references RUSERS(ID) enable validate;
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-14-rusers-identity-constraints' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Enforce exact user identity and active case-insensitive login; preserve history',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
