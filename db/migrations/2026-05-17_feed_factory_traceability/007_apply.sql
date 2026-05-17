-- 2026-05-17-007-backfill-user-group-reference
-- Purpose: restore USER_GROUP reference rows from the legacy facts already present in RUSERS and RIGHTS.

insert into USER_GROUP (ID, NAME)
select src.ID, src.ID
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

commit;
