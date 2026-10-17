select constraint_name,constraint_type,status,validated from user_constraints where constraint_name in('RUSERS_ID_UK','RRL_ACCESS_ASSIGN_USER_FK');
select index_name,status,uniqueness from user_indexes where table_name='RUSERS';
select count(*) DUPLICATE_ACTIVE_LOGINS from(select lower(trim(ID)) from RUSERS where nvl(DELETED,0)=0 group by lower(trim(ID)) having count(*)>1);
select count(*) INVALID_COUNT from user_objects where status='INVALID';
