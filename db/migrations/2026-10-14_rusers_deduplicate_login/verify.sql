select count(*) USER_COUNT from RUSERS;
select count(*) DUPLICATE_LOGINS from(select lower(trim(ID)) from RUSERS group by lower(trim(ID)) having count(*)>1);
select count(*) BACKUP_ROWS from RRL_RUSERS_DEDUP_BAK;
select ID,nvl(DELETED,0) DELETED_FLAG from RUSERS where lower(trim(ID))='klad_uzenaliev';
select index_name,status,uniqueness from user_indexes where index_name='RUSERS_LOGIN_UK';
select count(*) INVALID_COUNT from user_objects where status='INVALID';
