prompt [migration 2026-05-20-040] linear pick route order invariants - verify

select column_name, data_type, data_precision, data_scale,
       case
         when data_type = 'NUMBER' then 'OK'
         else 'CHECK'
       end decimal_rank_ready
  from user_tab_columns
 where table_name = 'RRL_PICK_ROUTE_CELL'
   and column_name = 'PICK_SEQUENCE';

select index_name, uniqueness
  from user_indexes
 where index_name in (
   'RRL_PICK_ROUTE_UX_ACTIVE_TOPO',
   'RRL_PICK_ROUTE_CELL_UX_SEQ',
   'RRL_PICK_ROUTE_CELL_UX_CELL'
 )
 order by index_name;

select count(*) ACTIVE_ROUTE_TOPOLOGY_VIOLATIONS
  from (
    select TOPOLOGY_ID
      from RRL_PICK_ROUTE
     where TOPOLOGY_ID is not null
       and ROUTE_KIND = 'PICK'
       and ACTIVE = 1
       and STATUS <> 'ARCHIVED'
     group by TOPOLOGY_ID
    having count(*) > 1
  );

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

select MIGRATION_ID, SCRIPT_NAME
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-20-040-linear-pick-route-order';

prompt [migration 2026-05-20-040] verify done
