prompt [migration 2026-05-23-044] ban zero warehouse id - apply

declare
  procedure drop_constraint_if_exists(p_table varchar2, p_constraint varchar2) is
    n number;
  begin
    select count(*) into n
      from user_constraints
     where table_name = upper(p_table)
       and constraint_name = upper(p_constraint);
    if n > 0 then
      execute immediate 'alter table ' || p_table || ' drop constraint ' || p_constraint;
    end if;
  end;

  procedure ensure_positive_constraint(p_table varchar2, p_column varchar2, p_constraint varchar2) is
    n number;
  begin
    select count(*) into n
      from user_constraints
     where table_name = upper(p_table)
       and constraint_name = upper(p_constraint);
    if n = 0 then
      execute immediate
        'alter table ' || p_table ||
        ' add constraint ' || p_constraint ||
        ' check (' || p_column || ' > 0)';
    end if;
  end;
begin
  delete from RRL_WAREHOUSE_MAP_CAMERA_LINK
   where CANVAS_ID in (select CANVAS_ID from RRL_WAREHOUSE_MAP_CANVAS where WARE_ID = 0)
      or FROM_CAMERA_ID in (select CAMERA_ID from RRL_WAREHOUSE_MAP_CAMERA where WARE_ID = 0)
      or TO_CAMERA_ID in (select CAMERA_ID from RRL_WAREHOUSE_MAP_CAMERA where WARE_ID = 0);

  delete from RRL_WAREHOUSE_MAP_OBJECT
   where CANVAS_ID in (select CANVAS_ID from RRL_WAREHOUSE_MAP_CANVAS where WARE_ID = 0)
      or CAMERA_ID in (select CAMERA_ID from RRL_WAREHOUSE_MAP_CAMERA where WARE_ID = 0)
      or TOPOLOGY_CELL_ID in (select TOPOLOGY_CELL_ID from RRL_TOPOLOGY_CELL where WARE_ID = 0);

  delete from RRL_WAREHOUSE_MAP_PASSAGE
   where CANVAS_ID in (select CANVAS_ID from RRL_WAREHOUSE_MAP_CANVAS where WARE_ID = 0)
      or CAMERA_ID in (select CAMERA_ID from RRL_WAREHOUSE_MAP_CAMERA where WARE_ID = 0);

  delete from RRL_PICK_ROUTE_CELL
   where WARE_ID = 0
      or PICK_ROUTE_ID in (select PICK_ROUTE_ID from RRL_PICK_ROUTE where WARE_ID = 0);

  delete from RRL_PICK_FACE
   where WARE_ID = 0
      or PICK_ROUTE_ID in (select PICK_ROUTE_ID from RRL_PICK_ROUTE where WARE_ID = 0);

  delete from RRL_PICK_ROUTE
   where WARE_ID = 0;

  delete from RRL_TOPOLOGY_CELL_GATE_DIST
   where TOPOLOGY_ID in (select TOPOLOGY_ID from RRL_WAREHOUSE_TOPOLOGY where WARE_ID = 0)
      or TOPOLOGY_CELL_ID in (select TOPOLOGY_CELL_ID from RRL_TOPOLOGY_CELL where WARE_ID = 0);

  delete from RRL_TOPOLOGY_CELL_SLOT
   where TOPOLOGY_ID in (select TOPOLOGY_ID from RRL_WAREHOUSE_TOPOLOGY where WARE_ID = 0)
      or TOPOLOGY_CELL_ID in (select TOPOLOGY_CELL_ID from RRL_TOPOLOGY_CELL where WARE_ID = 0);

  delete from RRL_TOPOLOGY_GATE
   where WARE_ID = 0
      or TOPOLOGY_ID in (select TOPOLOGY_ID from RRL_WAREHOUSE_TOPOLOGY where WARE_ID = 0);

  delete from RRL_TOPOLOGY_AISLE
   where TOPOLOGY_ID in (select TOPOLOGY_ID from RRL_WAREHOUSE_TOPOLOGY where WARE_ID = 0);

  delete from RRL_TOPOLOGY_ZONE
   where TOPOLOGY_ID in (select TOPOLOGY_ID from RRL_WAREHOUSE_TOPOLOGY where WARE_ID = 0);

  delete from RRL_TOPOLOGY_RECOMMENDATION
   where WARE_ID = 0
      or TOPOLOGY_ID in (select TOPOLOGY_ID from RRL_WAREHOUSE_TOPOLOGY where WARE_ID = 0);

  delete from RRL_TOPOLOGY_CELL
   where WARE_ID = 0;

  delete from RRL_WAREHOUSE_MAP_CAMERA
   where WARE_ID = 0;

  update RRL_WAREHOUSE_MAP_CANVAS
     set SOURCE_CANVAS_ID = null
   where SOURCE_CANVAS_ID in (select CANVAS_ID from RRL_WAREHOUSE_MAP_CANVAS where WARE_ID = 0);

  delete from RRL_WAREHOUSE_MAP_CANVAS
   where WARE_ID = 0;

  delete from RRL_WAREHOUSE_TOPOLOGY
   where WARE_ID = 0;

  delete from RRL_WARES
   where ID = 0;

  drop_constraint_if_exists('RRL_WARES', 'RRL_WARES_CK_ID_POS');
  drop_constraint_if_exists('RRL_WAREHOUSE_MAP_CANVAS', 'RRL_WH_MAP_CANVAS_CK_WARE_POS');
  drop_constraint_if_exists('RRL_WAREHOUSE_MAP_CAMERA', 'RRL_WH_MAP_CAMERA_CK_WARE_POS');
  drop_constraint_if_exists('RRL_WAREHOUSE_TOPOLOGY', 'RRL_WH_TOPOLOGY_CK_WARE_POS');
  drop_constraint_if_exists('RRL_TOPOLOGY_CELL', 'RRL_TOPO_CELL_CK_WARE_POS');
  drop_constraint_if_exists('RRL_TOPOLOGY_GATE', 'RRL_TOPO_GATE_CK_WARE_POS');
  drop_constraint_if_exists('RRL_TOPOLOGY_RECOMMENDATION', 'RRL_TOPO_REC_CK_WARE_POS');
  drop_constraint_if_exists('RRL_PICK_ROUTE', 'RRL_PICK_ROUTE_CK_WARE_POS');
  drop_constraint_if_exists('RRL_PICK_ROUTE_CELL', 'RRL_PICK_ROUTE_CELL_CK_WARE_POS');

  ensure_positive_constraint('RRL_WARES', 'ID', 'RRL_WARES_CK_ID_POS');
  ensure_positive_constraint('RRL_WAREHOUSE_MAP_CANVAS', 'WARE_ID', 'RRL_WH_MAP_CANVAS_CK_WARE_POS');
  ensure_positive_constraint('RRL_WAREHOUSE_MAP_CAMERA', 'WARE_ID', 'RRL_WH_MAP_CAMERA_CK_WARE_POS');
  ensure_positive_constraint('RRL_WAREHOUSE_TOPOLOGY', 'WARE_ID', 'RRL_WH_TOPOLOGY_CK_WARE_POS');
  ensure_positive_constraint('RRL_TOPOLOGY_CELL', 'WARE_ID', 'RRL_TOPO_CELL_CK_WARE_POS');
  ensure_positive_constraint('RRL_TOPOLOGY_GATE', 'WARE_ID', 'RRL_TOPO_GATE_CK_WARE_POS');
  ensure_positive_constraint('RRL_TOPOLOGY_RECOMMENDATION', 'WARE_ID', 'RRL_TOPO_REC_CK_WARE_POS');
  ensure_positive_constraint('RRL_PICK_ROUTE', 'WARE_ID', 'RRL_PICK_ROUTE_CK_WARE_POS');
  ensure_positive_constraint('RRL_PICK_ROUTE_CELL', 'WARE_ID', 'RRL_PICK_ROUTE_CELL_CK_WARE_POS');
end;
/

merge into RRL_SCHEMA_MIGRATIONS d
using (
  select '2026-05-23-044-ban-zero-warehouse-id' migration_id,
         'Delete fixture warehouse ID 0 data and enforce positive warehouse identifiers for warehouse map/topology/route tables' description,
         '044_apply.sql' script_name,
         '044_rollback.sql' rollback_script
    from dual
) s
on (d.MIGRATION_ID = s.MIGRATION_ID)
when matched then update set
  d.DESCRIPTION = s.DESCRIPTION,
  d.SCRIPT_NAME = s.SCRIPT_NAME,
  d.ROLLBACK_SCRIPT = s.ROLLBACK_SCRIPT,
  d.APPLIED_AT = sysdate,
  d.APPLIED_BY = user
when not matched then insert (
  MIGRATION_ID, DESCRIPTION, SCRIPT_NAME, ROLLBACK_SCRIPT, APPLIED_AT, APPLIED_BY
) values (
  s.MIGRATION_ID, s.DESCRIPTION, s.SCRIPT_NAME, s.ROLLBACK_SCRIPT, sysdate, user
);

commit;

prompt [migration 2026-05-23-044] apply done
