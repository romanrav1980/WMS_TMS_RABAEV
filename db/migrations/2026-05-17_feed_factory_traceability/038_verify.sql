prompt [migration 2026-05-20-038] warehouse topology master data - verify

select table_name
  from user_tables
 where table_name in (
   'RRL_WAREHOUSE_TOPOLOGY',
   'RRL_TOPOLOGY_ZONE',
   'RRL_TOPOLOGY_AISLE',
   'RRL_TOPOLOGY_CELL',
   'RRL_TOPOLOGY_RECOMMENDATION',
   'RRL_TOPOLOGY_CHANGE_LOG'
 )
 order by table_name;

select sequence_name
  from user_sequences
 where sequence_name in (
   'RRL_WH_TOPOLOGY_SQ',
   'RRL_TOPOLOGY_ZONE_SQ',
   'RRL_TOPOLOGY_AISLE_SQ',
   'RRL_TOPOLOGY_CELL_SQ',
   'RRL_TOPO_REC_SQ',
   'RRL_TOPO_CHANGE_LOG_SQ'
 )
 order by sequence_name;

select table_name, column_name
  from user_tab_columns
 where table_name = 'RRL_PICK_ROUTE'
   and column_name in (
     'TOPOLOGY_ID',
     'ROUTE_PATTERN',
     'START_POINT_CODE',
     'END_POINT_CODE',
     'STRICT_SEQUENCE',
     'STATUS',
     'PUBLISHED_AT',
     'PUBLISHED_BY',
     'COMMENT_TEXT',
     'ZONE_CODE'
   )
 order by column_name;

select table_name, column_name
  from user_tab_columns
 where table_name = 'RRL_PICK_ROUTE_CELL'
   and column_name in (
     'TOPOLOGY_CELL_ID',
     'SECTION_CODE',
     'BAY_NO',
     'DIRECTION_CODE',
     'VISIT_GROUP_NO',
     'PATH_SEGMENT_NO',
     'DISTANCE_FROM_PREV_M',
     'TURN_COST_SEC'
   )
 order by column_name;

select RIGHT1
  from RIGHTS
 where USER_GROUP = 'GLOBAL_ADMIN'
   and RIGHT1 in (
     'WAREHOUSE_TOPOLOGY_VIEW',
     'WAREHOUSE_TOPOLOGY_EDIT',
     'WAREHOUSE_TOPOLOGY_PUBLISH',
     'PICK_ROUTE_ADMIN_VIEW',
     'PICK_ROUTE_ADMIN_EDIT',
     'PICK_ROUTE_ADMIN_PUBLISH'
   )
 order by RIGHT1;

select MIGRATION_ID, SCRIPT_NAME
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-20-038-warehouse-topology-master-data';

prompt [migration 2026-05-20-038] verify done
