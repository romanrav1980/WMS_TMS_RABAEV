prompt [migration 2026-05-23-043] warehouse map operation idempotency keys - verify

select table_name, column_name, data_type, data_length
  from user_tab_columns
 where (table_name, column_name) in (
   ('RRL_WAREHOUSE_MAP_CANVAS', 'IDEMPOTENCY_KEY'),
   ('RRL_WAREHOUSE_MAP_CANVAS', 'PUBLISH_IDEMPOTENCY_KEY'),
   ('RRL_WAREHOUSE_TOPOLOGY', 'IDEMPOTENCY_KEY'),
   ('RRL_PICK_ROUTE', 'IDEMPOTENCY_KEY')
 )
 order by table_name, column_name;

select index_name, uniqueness
  from user_indexes
 where index_name in (
   'RRL_WH_MAP_CANVAS_UX_IDEMP',
   'RRL_WH_MAP_CANVAS_UX_PUBIDEMP',
   'RRL_WH_TOPOLOGY_UX_IDEMP',
   'RRL_PICK_ROUTE_UX_IDEMP'
 )
 order by index_name;

select count(*) CANVAS_IDEMP_DUPLICATES
  from (
    select WARE_ID, upper(IDEMPOTENCY_KEY) IDEMPOTENCY_KEY
      from RRL_WAREHOUSE_MAP_CANVAS
     where ACTIVE = 1
       and IDEMPOTENCY_KEY is not null
     group by WARE_ID, upper(IDEMPOTENCY_KEY)
    having count(*) > 1
  );

select count(*) TOPOLOGY_IDEMP_DUPLICATES
  from (
    select WARE_ID, upper(IDEMPOTENCY_KEY) IDEMPOTENCY_KEY
      from RRL_WAREHOUSE_TOPOLOGY
     where STATUS <> 'ARCHIVED'
       and IDEMPOTENCY_KEY is not null
     group by WARE_ID, upper(IDEMPOTENCY_KEY)
    having count(*) > 1
  );

select count(*) ROUTE_IDEMP_DUPLICATES
  from (
    select TOPOLOGY_ID, upper(IDEMPOTENCY_KEY) IDEMPOTENCY_KEY
      from RRL_PICK_ROUTE
     where ACTIVE = 1
       and STATUS <> 'ARCHIVED'
       and IDEMPOTENCY_KEY is not null
     group by TOPOLOGY_ID, upper(IDEMPOTENCY_KEY)
    having count(*) > 1
  );

select MIGRATION_ID, SCRIPT_NAME
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-23-043-warehouse-map-operation-idempotency';

prompt [migration 2026-05-23-043] verify done
