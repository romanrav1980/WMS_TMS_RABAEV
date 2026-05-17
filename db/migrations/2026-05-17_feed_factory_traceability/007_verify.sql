-- 2026-05-17-007-backfill-user-group-reference verification

select 'USER_GROUP_ROWS' check_name,
       count(*) rows_found
  from USER_GROUP;

select 'MISSING_USER_GROUP_ROWS' check_name,
       count(*) missing_rows
  from (
    select USER_GROUP ID from RUSERS where USER_GROUP is not null
    union
    select USER_GROUP ID from RIGHTS where USER_GROUP is not null
  ) src
 where not exists (
   select 1
     from USER_GROUP g
    where g.ID = src.ID
 );

select object_type, status, count(*) cnt
  from user_objects
 where status <> 'VALID'
   and object_name not like 'BIN$%'
 group by object_type, status
 order by object_type, status;
