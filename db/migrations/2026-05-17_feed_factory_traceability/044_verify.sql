prompt [migration 2026-05-23-044] ban zero warehouse id - verify

select 'zero_wares' check_name, count(*) violation_count
  from RRL_WARES
 where ID = 0;

select 'zero_canvas' check_name, count(*) violation_count
  from RRL_WAREHOUSE_MAP_CANVAS
 where WARE_ID = 0;

select 'zero_camera' check_name, count(*) violation_count
  from RRL_WAREHOUSE_MAP_CAMERA
 where WARE_ID = 0;

select 'zero_topology' check_name, count(*) violation_count
  from RRL_WAREHOUSE_TOPOLOGY
 where WARE_ID = 0;

select 'zero_topology_cell' check_name, count(*) violation_count
  from RRL_TOPOLOGY_CELL
 where WARE_ID = 0;

select 'zero_pick_route' check_name, count(*) violation_count
  from RRL_PICK_ROUTE
 where WARE_ID = 0;

select 'zero_pick_route_cell' check_name, count(*) violation_count
  from RRL_PICK_ROUTE_CELL
 where WARE_ID = 0;

select 'positive_constraints' check_name, count(*) present_count
  from user_constraints
 where constraint_name in (
   'RRL_WARES_CK_ID_POS',
   'RRL_WH_MAP_CANVAS_CK_WARE_POS',
   'RRL_WH_MAP_CAMERA_CK_WARE_POS',
   'RRL_WH_TOPOLOGY_CK_WARE_POS',
   'RRL_TOPO_CELL_CK_WARE_POS',
   'RRL_TOPO_GATE_CK_WARE_POS',
   'RRL_TOPO_REC_CK_WARE_POS',
   'RRL_PICK_ROUTE_CK_WARE_POS',
   'RRL_PICK_ROUTE_CELL_CK_WARE_POS'
 )
   and status = 'ENABLED';

select 'migration_registered' check_name, count(*) present_count
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-23-044-ban-zero-warehouse-id';

prompt [migration 2026-05-23-044] verify done
