prompt [migration 2026-05-22-041] warehouse map canvas and cell slots - verify

select count(*) MISSING_TABLES
  from (
    select 'RRL_WAREHOUSE_MAP_CANVAS' object_name from dual
    union all select 'RRL_WAREHOUSE_MAP_CAMERA' from dual
    union all select 'RRL_WAREHOUSE_MAP_OBJECT' from dual
    union all select 'RRL_WAREHOUSE_MAP_PASSAGE' from dual
    union all select 'RRL_WAREHOUSE_MAP_CAMERA_LINK' from dual
    union all select 'RRL_TOPOLOGY_CELL_SLOT' from dual
    minus
    select table_name from user_tables
  );

select count(*) MISSING_SEQUENCES
  from (
    select 'RRL_WH_MAP_CANVAS_SQ' object_name from dual
    union all select 'RRL_WH_MAP_CAMERA_SQ' from dual
    union all select 'RRL_WH_MAP_OBJECT_SQ' from dual
    union all select 'RRL_WH_MAP_PASSAGE_SQ' from dual
    union all select 'RRL_WH_MAP_CAM_LINK_SQ' from dual
    union all select 'RRL_TOPO_CELL_SLOT_SQ' from dual
    minus
    select sequence_name from user_sequences
  );

select count(*) MISSING_COLUMNS
  from (
    select 'RRL_TOPOLOGY_CELL.SLOT_LAYER_KIND' object_name from dual
    union all select 'RRL_TOPOLOGY_CELL.WAREHOUSE_MAP_CAMERA_ID' from dual
    union all select 'RRL_PICK_ROUTE_CELL.CELL_SLOT_ID' from dual
    union all select 'RRL_STOCK_RESERVATION.CELL_SLOT_ID' from dual
    union all select 'RRL_WAREHOUSE_TASK.FROM_CELL_SLOT_ID' from dual
    union all select 'RRL_WAREHOUSE_TASK.TO_CELL_SLOT_ID' from dual
    minus
    select table_name || '.' || column_name
      from user_tab_columns
  );

select index_name, uniqueness
  from user_indexes
 where index_name in (
   'RRL_WH_MAP_CANVAS_UX_CODE',
   'RRL_WH_MAP_CAMERA_UX_CODE',
   'RRL_WH_MAP_PASSAGE_UX_CODE',
   'RRL_WH_MAP_LINK_UX_CODE',
   'RRL_TOPO_CELL_SLOT_UX_CODE',
   'RRL_TOPO_CELL_SLOT_UX_POS'
 )
 order by index_name;

select count(*) CAMERA_DIMENSION_VIOLATIONS
  from RRL_WAREHOUSE_MAP_CAMERA
 where ACTIVE = 1
   and (WIDTH_M <= 0 or DEPTH_M <= 0 or HEIGHT_M <= 0 or DEFAULT_PASSAGE_WIDTH_M <= 0);

select count(*) PASSAGE_WIDTH_VIOLATIONS
  from RRL_WAREHOUSE_MAP_PASSAGE
 where ACTIVE = 1
   and WIDTH_M <= 0;

select count(*) ACTIVE_CAMERA_CODE_DUPLICATES
  from (
    select CANVAS_ID, upper(CAMERA_CODE)
      from RRL_WAREHOUSE_MAP_CAMERA
     where ACTIVE = 1
     group by CANVAS_ID, upper(CAMERA_CODE)
    having count(*) > 1
  );

select count(*) ACTIVE_SLOT_CODE_DUPLICATES
  from (
    select TOPOLOGY_ID, upper(SLOT_CODE)
      from RRL_TOPOLOGY_CELL_SLOT
     where ACTIVE = 1
     group by TOPOLOGY_ID, upper(SLOT_CODE)
    having count(*) > 1
  );

select count(*) SLOT_KIND_PARENT_VIOLATIONS
  from RRL_TOPOLOGY_CELL_SLOT s
  join RRL_TOPOLOGY_CELL c
    on c.TOPOLOGY_CELL_ID = s.TOPOLOGY_CELL_ID
 where s.ACTIVE = 1
   and c.SLOT_LAYER_KIND <> 'MIXED'
   and c.SLOT_LAYER_KIND <> s.SLOT_KIND;

select count(*) MIXED_SLOT_KIND_VIOLATIONS
  from (
    select s.TOPOLOGY_CELL_ID
      from RRL_TOPOLOGY_CELL_SLOT s
      join RRL_TOPOLOGY_CELL c
        on c.TOPOLOGY_CELL_ID = s.TOPOLOGY_CELL_ID
     where s.ACTIVE = 1
       and c.SLOT_LAYER_KIND <> 'MIXED'
     group by s.TOPOLOGY_CELL_ID
    having count(distinct s.SLOT_KIND) > 1
  );

select count(*) SLOT_ORDER_KIND_VIOLATIONS
  from RRL_TOPOLOGY_CELL_SLOT
 where ACTIVE = 1
   and (
     (SLOT_KIND = 'PICK_FACE_SLOT' and STORAGE_ORDER is not null) or
     (SLOT_KIND = 'STORAGE_SLOT' and PICK_ORDER is not null)
   );

select count(*) PICK_ROUTE_STORAGE_SLOT_VIOL
  from RRL_PICK_ROUTE_CELL rc
  join RRL_TOPOLOGY_CELL_SLOT s
    on s.CELL_SLOT_ID = rc.CELL_SLOT_ID
 where rc.ACTIVE = 1
   and s.SLOT_KIND <> 'PICK_FACE_SLOT';

select MIGRATION_ID, SCRIPT_NAME
  from RRL_SCHEMA_MIGRATIONS
 where MIGRATION_ID = '2026-05-22-041-warehouse-map-canvas-slots';

prompt [migration 2026-05-22-041] verify done
