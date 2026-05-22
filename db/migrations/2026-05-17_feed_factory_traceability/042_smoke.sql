prompt [migration 2026-05-22-042] warehouse map draft publish API - smoke

delete from RRL_PICK_ROUTE_CELL where CREATED_BY = 'SMOKE_042';
delete from RRL_PICK_ROUTE where CREATED_BY = 'SMOKE_042';
delete from RRL_TOPOLOGY_CELL_SLOT where CREATED_BY = 'SMOKE_042';
delete from RRL_TOPOLOGY_CELL where CREATED_BY = 'SMOKE_042';
delete from RRL_WAREHOUSE_TOPOLOGY where CREATED_BY = 'SMOKE_042';
delete from RRL_WAREHOUSE_MAP_CAMERA where CREATED_BY = 'SMOKE_042';
delete from RRL_WAREHOUSE_MAP_CANVAS where CREATED_BY = 'SMOKE_042';
commit;

declare
  v_canvas_id number;
  v_camera_id number;
  v_topology_id number;
  v_route_id number;
  v_pick_cell_id number;
  v_storage_cell_id number;
  v_pick_slot_id number;
  v_storage_slot_id number;
  v_validation clob;
  v_publish_failed number := 0;
begin
  v_canvas_id := RRL_WH_MAP_CANVAS_SQ.nextval;
  insert into RRL_WAREHOUSE_MAP_CANVAS (
    CANVAS_ID, WARE_ID, CANVAS_CODE, CANVAS_NAME, VERSION_NO, STATUS,
    GRID_CELL_WIDTH_M, GRID_CELL_DEPTH_M, LEVELS, CREATED_BY, UPDATED_BY
  ) values (
    v_canvas_id, -41042, 'SMOKE-042-CANVAS', 'Smoke canvas 042', 1, 'DRAFT',
    1.2, 0.8, 6, 'SMOKE_042', 'SMOKE_042'
  );

  v_camera_id := RRL_WH_MAP_CAMERA_SQ.nextval;
  insert into RRL_WAREHOUSE_MAP_CAMERA (
    CAMERA_ID, CANVAS_ID, WARE_ID, CAMERA_CODE, CAMERA_NAME, CAMERA_KIND,
    WIDTH_M, DEPTH_M, HEIGHT_M, GRID_CELL_WIDTH_M, GRID_CELL_DEPTH_M, LEVELS,
    DEFAULT_PASSAGE_WIDTH_M, CREATED_BY, UPDATED_BY
  ) values (
    v_camera_id, v_canvas_id, -41042, 'CAM-042', 'Smoke camera 042', 'DRY',
    20, 20, 8, 1.2, 0.8, 6, 3, 'SMOKE_042', 'SMOKE_042'
  );

  v_topology_id := RRL_WH_TOPOLOGY_SQ.nextval;
  insert into RRL_WAREHOUSE_TOPOLOGY (
    TOPOLOGY_ID, WARE_ID, TOPOLOGY_CODE, TOPOLOGY_NAME, VERSION_NO, STATUS,
    CREATED_BY, UPDATED_BY
  ) values (
    v_topology_id, -41042, 'SMOKE-042-TOPO', 'Smoke topology 042', 1, 'DRAFT',
    'SMOKE_042', 'SMOKE_042'
  );

  v_pick_cell_id := RRL_TOPOLOGY_CELL_SQ.nextval;
  insert into RRL_TOPOLOGY_CELL (
    TOPOLOGY_CELL_ID, TOPOLOGY_ID, WARE_ID, CELL_CODE, CELL_KIND, SIDE_CODE,
    X, Y, Z, WIDTH, DEPTH, HEIGHT, SLOT_LAYER_KIND, WAREHOUSE_MAP_CAMERA_ID,
    CREATED_BY, UPDATED_BY
  ) values (
    v_pick_cell_id, v_topology_id, -41042, 'SMOKE-042-PICK', 'PICK_FACE', 'CENTER',
    0, 0, 0, 1.2, 0.8, 1, 'PICK_FACE_SLOT', v_camera_id,
    'SMOKE_042', 'SMOKE_042'
  );

  v_storage_cell_id := RRL_TOPOLOGY_CELL_SQ.nextval;
  insert into RRL_TOPOLOGY_CELL (
    TOPOLOGY_CELL_ID, TOPOLOGY_ID, WARE_ID, CELL_CODE, CELL_KIND, SIDE_CODE,
    X, Y, Z, WIDTH, DEPTH, HEIGHT, SLOT_LAYER_KIND, WAREHOUSE_MAP_CAMERA_ID,
    CREATED_BY, UPDATED_BY
  ) values (
    v_storage_cell_id, v_topology_id, -41042, 'SMOKE-042-STOR', 'STORAGE', 'CENTER',
    2, 0, 0, 1.2, 0.8, 1, 'STORAGE_SLOT', v_camera_id,
    'SMOKE_042', 'SMOKE_042'
  );

  v_pick_slot_id := RRL_TOPO_CELL_SLOT_SQ.nextval;
  insert into RRL_TOPOLOGY_CELL_SLOT (
    CELL_SLOT_ID, TOPOLOGY_ID, TOPOLOGY_CELL_ID, PARENT_SLOT_LAYER_KIND,
    SLOT_KIND, SLOT_CODE, FRACTION_COUNT, FRACTION_INDEX, SUB_LEVEL_NO,
    SUB_COLUMN_NO, PICK_ORDER, CREATED_BY, UPDATED_BY
  ) values (
    v_pick_slot_id, v_topology_id, v_pick_cell_id, 'PICK_FACE_SLOT',
    'PICK_FACE_SLOT', 'SMOKE-042-PICK-A', 2, 1, 1, 1, 1,
    'SMOKE_042', 'SMOKE_042'
  );

  v_storage_slot_id := RRL_TOPO_CELL_SLOT_SQ.nextval;
  insert into RRL_TOPOLOGY_CELL_SLOT (
    CELL_SLOT_ID, TOPOLOGY_ID, TOPOLOGY_CELL_ID, PARENT_SLOT_LAYER_KIND,
    SLOT_KIND, SLOT_CODE, FRACTION_COUNT, FRACTION_INDEX, SUB_LEVEL_NO,
    SUB_COLUMN_NO, STORAGE_ORDER, CREATED_BY, UPDATED_BY
  ) values (
    v_storage_slot_id, v_topology_id, v_storage_cell_id, 'STORAGE_SLOT',
    'STORAGE_SLOT', 'SMOKE-042-STOR-A', 2, 1, 1, 1, 1,
    'SMOKE_042', 'SMOKE_042'
  );

  v_route_id := RRL_PICK_ROUTE_SQ.nextval;
  insert into RRL_PICK_ROUTE (
    PICK_ROUTE_ID, ROUTE_CODE, ROUTE_NAME, WARE_ID, TOPOLOGY_ID, ROUTE_KIND,
    ROUTE_PATTERN, STATUS, ACTIVE, CREATED_BY, UPDATED_BY
  ) values (
    v_route_id, 'SMOKE-042-ROUTE', 'Smoke route 042', -41042, v_topology_id, 'PICK',
    'LINEAR', 'DRAFT', 1, 'SMOKE_042', 'SMOKE_042'
  );

  insert into RRL_PICK_ROUTE_CELL (
    PICK_ROUTE_CELL_ID, PICK_ROUTE_ID, WARE_ID, CELL_CODE, PICK_SEQUENCE,
    TOPOLOGY_CELL_ID, CELL_SLOT_ID, ACTIVE, CREATED_BY, UPDATED_BY
  ) values (
    RRL_PICK_ROUTE_CELL_SQ.nextval, v_route_id, -41042, 'SMOKE-042-PICK-A', 1,
    v_pick_cell_id, v_pick_slot_id, 1, 'SMOKE_042', 'SMOKE_042'
  );

  insert into RRL_PICK_ROUTE_CELL (
    PICK_ROUTE_CELL_ID, PICK_ROUTE_ID, WARE_ID, CELL_CODE, PICK_SEQUENCE,
    TOPOLOGY_CELL_ID, CELL_SLOT_ID, ACTIVE, CREATED_BY, UPDATED_BY
  ) values (
    RRL_PICK_ROUTE_CELL_SQ.nextval, v_route_id, -41042, 'SMOKE-042-STOR-A', 2,
    v_storage_cell_id, v_storage_slot_id, 1, 'SMOKE_042', 'SMOKE_042'
  );

  v_validation := RRL_WAREHOUSE_MAP_API.VALIDATE_DRAFT(v_canvas_id, v_route_id);
  if instr(v_validation, '"valid":false') = 0 then
    raise_application_error(-20430, 'storage route row was not rejected: ' || dbms_lob.substr(v_validation, 1000, 1));
  end if;

  begin
    RRL_WAREHOUSE_MAP_API.PUBLISH_DRAFT(v_canvas_id, v_route_id, 'SMOKE_042');
  exception
    when others then
      v_publish_failed := 1;
  end;
  if v_publish_failed = 0 then
    raise_application_error(-20431, 'invalid route publish did not fail');
  end if;

  update RRL_PICK_ROUTE_CELL
     set ACTIVE = 0,
         UPDATED_BY = 'SMOKE_042',
         UPDATED_AT = sysdate
   where PICK_ROUTE_ID = v_route_id
     and CELL_SLOT_ID = v_storage_slot_id;

  v_validation := RRL_WAREHOUSE_MAP_API.VALIDATE_DRAFT(v_canvas_id, v_route_id);
  if instr(v_validation, '"valid":true') = 0 then
    raise_application_error(-20432, 'fixed route was not valid: ' || dbms_lob.substr(v_validation, 1000, 1));
  end if;

  RRL_WAREHOUSE_MAP_API.PUBLISH_DRAFT(v_canvas_id, v_route_id, 'SMOKE_042');
end;
/

select CANVAS_CODE, STATUS, PUBLISHED_BY
  from RRL_WAREHOUSE_MAP_CANVAS
 where CREATED_BY = 'SMOKE_042';

select ROUTE_CODE, STATUS, ACTIVE
  from RRL_PICK_ROUTE
 where CREATED_BY = 'SMOKE_042';

commit;

prompt [migration 2026-05-22-042] smoke done
