-- Откат только до первой записи профиля: после фактов изменения история сохраняется, исправление — вперёд.
declare n number;begin
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_STORE_PROFILE_CHANGE';
 if n=1 then execute immediate 'select count(*) from RRL_STORE_PROFILE_CHANGE' into n;
  if n>0 then raise_application_error(-20809,'STORE_PROFILE_HISTORY_EXISTS_FORWARD_FIX_REQUIRED');end if;end if;
 for t in(select TABLE_NAME from USER_TABLES where TABLE_NAME in('RRL_STORE_RECEIVING_WINDOW','RRL_STORE_PROFILE','RRL_STORE_PROFILE_CHANGE')
          order by case TABLE_NAME when 'RRL_STORE_RECEIVING_WINDOW' then 1 when 'RRL_STORE_PROFILE' then 2 else 3 end)loop
  execute immediate 'drop table '||t.TABLE_NAME;
 end loop;
 update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-14-1490-ni051-store-profile';
 commit;
end;
/
