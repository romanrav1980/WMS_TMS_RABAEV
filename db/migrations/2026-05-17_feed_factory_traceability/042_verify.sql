prompt [migration 2026-05-22-042] warehouse map draft publish API - verify

select object_name, object_type, status
  from user_objects
 where object_name = 'RRL_WAREHOUSE_MAP_API'
 order by object_type;

select index_name, uniqueness
  from user_indexes
 where index_name = 'RRL_PICK_ROUTE_CELL_UX_SLOT';

select count(*) ROUTE_SEQUENCE_VIOLATIONS
  from (
    select PICK_ROUTE_ID, PICK_SEQUENCE
      from RRL_PICK_ROUTE_CELL
     where ACTIVE = 1
     group by PICK_ROUTE_ID, PICK_SEQUENCE
    having count(*) > 1
  );

select count(*) ROUTE_CELL_VIOLATIONS
  from (
    select PICK_ROUTE_ID, TOPOLOGY_CELL_ID
      from RRL_PICK_ROUTE_CELL
     where ACTIVE = 1
       and TOPOLOGY_CELL_ID is not null
     group by PICK_ROUTE_ID, TOPOLOGY_CELL_ID
    having count(*) > 1
  );

select count(*) ROUTE_SLOT_VIOLATIONS
  from (
    select PICK_ROUTE_ID, CELL_SLOT_ID
      from RRL_PICK_ROUTE_CELL
     where ACTIVE = 1
       and CELL_SLOT_ID is not null
     group by PICK_ROUTE_ID, CELL_SLOT_ID
    having count(*) > 1
  );

select count(*) PICK_ROUTE_STORAGE_SLOT_VIOL
  from RRL_PICK_ROUTE_CELL rc
  join RRL_TOPOLOGY_CELL_SLOT s
    on s.CELL_SLOT_ID = rc.CELL_SLOT_ID
 where rc.ACTIVE = 1
   and s.SLOT_KIND <> 'PICK_FACE_SLOT';

select MIGRATION_ID, SCRIPT_NAME
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-22-042-warehouse-map-draft-publish-api';

prompt [migration 2026-05-22-042] verify done
