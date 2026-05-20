prompt [migration 2026-05-20-039] topology gate distance matrix - verify

select table_name
  from user_tables
 where table_name in ('RRL_TOPOLOGY_GATE', 'RRL_TOPOLOGY_CELL_GATE_DIST')
 order by table_name;

select sequence_name
  from user_sequences
 where sequence_name in ('RRL_TOPOLOGY_GATE_SQ', 'RRL_TOPO_CELL_GATE_DIST_SQ')
 order by sequence_name;

select column_name
  from user_tab_columns
 where table_name = 'RRL_TOPOLOGY_CELL_GATE_DIST'
   and column_name in ('TOPOLOGY_CELL_ID', 'TOPOLOGY_GATE_ID', 'FLOW_KIND', 'DISTANCE_M', 'TRAVEL_TIME_SEC')
 order by column_name;

select MIGRATION_ID, SCRIPT_NAME
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-20-039-topology-gate-distance-matrix';

prompt [migration 2026-05-20-039] verify done
