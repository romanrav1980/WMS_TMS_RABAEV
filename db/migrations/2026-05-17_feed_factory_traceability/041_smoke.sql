prompt [migration 2026-05-22-041] warehouse map canvas and cell slots - smoke

delete from RRL_TOPOLOGY_CELL_SLOT where CREATED_BY = 'SMOKE_041';
delete from RRL_TOPOLOGY_CELL where CREATED_BY = 'SMOKE_041';
delete from RRL_WAREHOUSE_TOPOLOGY where CREATED_BY = 'SMOKE_041';
delete from RRL_WAREHOUSE_MAP_CAMERA_LINK where CREATED_BY = 'SMOKE_041';
delete from RRL_WAREHOUSE_MAP_PASSAGE where CREATED_BY = 'SMOKE_041';
delete from RRL_WAREHOUSE_MAP_OBJECT where CREATED_BY = 'SMOKE_041';
delete from RRL_WAREHOUSE_MAP_CAMERA where CREATED_BY = 'SMOKE_041';
delete from RRL_WAREHOUSE_MAP_CANVAS where CREATED_BY = 'SMOKE_041';
commit;

declare
  v_canvas_id number;
  v_camera_a number;
  v_camera_b number;
  v_topology_id number;
  v_pick_cell_id number;
  v_storage_cell_id number;
  v_failed number;
begin
  v_canvas_id := RRL_WH_MAP_CANVAS_SQ.nextval;
  insert into RRL_WAREHOUSE_MAP_CANVAS (
    CANVAS_ID, WARE_ID, CANVAS_CODE, CANVAS_NAME, VERSION_NO, STATUS,
    GRID_CELL_WIDTH_M, GRID_CELL_DEPTH_M, LEVELS, CREATED_BY, UPDATED_BY
  ) values (
    v_canvas_id, -41041, 'SMOKE-041-CANVAS', 'Smoke canvas 041', 1, 'DRAFT',
    1.2, 0.8, 6, 'SMOKE_041', 'SMOKE_041'
  );

  v_camera_a := RRL_WH_MAP_CAMERA_SQ.nextval;
  insert into RRL_WAREHOUSE_MAP_CAMERA (
    CAMERA_ID, CANVAS_ID, WARE_ID, CAMERA_CODE, CAMERA_NAME, CAMERA_KIND,
    ORIGIN_X_M, ORIGIN_Y_M, ORIGIN_Z_M, WIDTH_M, DEPTH_M, HEIGHT_M,
    GRID_CELL_WIDTH_M, GRID_CELL_DEPTH_M, LEVELS, DEFAULT_PASSAGE_WIDTH_M,
    CREATED_BY, UPDATED_BY
  ) values (
    v_camera_a, v_canvas_id, -41041, 'CAM-A', 'Smoke camera A', 'DRY',
    0, 0, 0, 80, 120, 12, 1.2, 0.8, 6, 3,
    'SMOKE_041', 'SMOKE_041'
  );

  v_camera_b := RRL_WH_MAP_CAMERA_SQ.nextval;
  insert into RRL_WAREHOUSE_MAP_CAMERA (
    CAMERA_ID, CANVAS_ID, WARE_ID, CAMERA_CODE, CAMERA_NAME, CAMERA_KIND,
    ORIGIN_X_M, ORIGIN_Y_M, ORIGIN_Z_M, WIDTH_M, DEPTH_M, HEIGHT_M,
    GRID_CELL_WIDTH_M, GRID_CELL_DEPTH_M, LEVELS, DEFAULT_PASSAGE_WIDTH_M,
    CREATED_BY, UPDATED_BY
  ) values (
    v_camera_b, v_canvas_id, -41041, 'CAM-B', 'Smoke camera B', 'COLD',
    85, 0, 0, 40, 90, 10, 1.2, 0.8, 6, 3,
    'SMOKE_041', 'SMOKE_041'
  );

  insert into RRL_WAREHOUSE_MAP_CAMERA_LINK (
    CAMERA_LINK_ID, CANVAS_ID, FROM_CAMERA_ID, TO_CAMERA_ID, LINK_CODE,
    LINK_KIND, DISTANCE_M, TRAVEL_TIME_SEC, DIRECTION_CODE, CREATED_BY, UPDATED_BY
  ) values (
    RRL_WH_MAP_CAM_LINK_SQ.nextval, v_canvas_id, v_camera_a, v_camera_b, 'A-B',
    'CORRIDOR', 5, 20, 'BOTH', 'SMOKE_041', 'SMOKE_041'
  );

  v_topology_id := RRL_WH_TOPOLOGY_SQ.nextval;
  insert into RRL_WAREHOUSE_TOPOLOGY (
    TOPOLOGY_ID, WARE_ID, TOPOLOGY_CODE, TOPOLOGY_NAME, VERSION_NO, STATUS,
    CREATED_BY, UPDATED_BY
  ) values (
    v_topology_id, -41041, 'SMOKE-041-TOPO', 'Smoke topology 041', 1, 'DRAFT',
    'SMOKE_041', 'SMOKE_041'
  );

  v_pick_cell_id := RRL_TOPOLOGY_CELL_SQ.nextval;
  insert into RRL_TOPOLOGY_CELL (
    TOPOLOGY_CELL_ID, TOPOLOGY_ID, WARE_ID, CELL_CODE, CELL_KIND, SIDE_CODE,
    X, Y, Z, WIDTH, DEPTH, HEIGHT, SLOT_LAYER_KIND, WAREHOUSE_MAP_CAMERA_ID,
    CREATED_BY, UPDATED_BY
  ) values (
    v_pick_cell_id, v_topology_id, -41041, 'SMOKE-PICK-01', 'PICK_FACE', 'CENTER',
    0, 0, 0, 1.2, 0.8, 1, 'PICK_FACE_SLOT', v_camera_a,
    'SMOKE_041', 'SMOKE_041'
  );

  v_storage_cell_id := RRL_TOPOLOGY_CELL_SQ.nextval;
  insert into RRL_TOPOLOGY_CELL (
    TOPOLOGY_CELL_ID, TOPOLOGY_ID, WARE_ID, CELL_CODE, CELL_KIND, SIDE_CODE,
    X, Y, Z, WIDTH, DEPTH, HEIGHT, SLOT_LAYER_KIND, WAREHOUSE_MAP_CAMERA_ID,
    CREATED_BY, UPDATED_BY
  ) values (
    v_storage_cell_id, v_topology_id, -41041, 'SMOKE-STOR-01', 'STORAGE', 'CENTER',
    2, 0, 0, 1.2, 0.8, 1, 'STORAGE_SLOT', v_camera_a,
    'SMOKE_041', 'SMOKE_041'
  );

  insert into RRL_TOPOLOGY_CELL_SLOT (
    CELL_SLOT_ID, TOPOLOGY_ID, TOPOLOGY_CELL_ID, PARENT_SLOT_LAYER_KIND,
    SLOT_KIND, SLOT_CODE, FRACTION_COUNT, FRACTION_INDEX, SUB_LEVEL_NO,
    SUB_COLUMN_NO, PICK_ORDER, CREATED_BY, UPDATED_BY
  ) values (
    RRL_TOPO_CELL_SLOT_SQ.nextval, v_topology_id, v_pick_cell_id, 'PICK_FACE_SLOT',
    'PICK_FACE_SLOT', 'SMOKE-PICK-01-A', 3, 1, 1, 1, 10,
    'SMOKE_041', 'SMOKE_041'
  );

  insert into RRL_TOPOLOGY_CELL_SLOT (
    CELL_SLOT_ID, TOPOLOGY_ID, TOPOLOGY_CELL_ID, PARENT_SLOT_LAYER_KIND,
    SLOT_KIND, SLOT_CODE, FRACTION_COUNT, FRACTION_INDEX, SUB_LEVEL_NO,
    SUB_COLUMN_NO, STORAGE_ORDER, CAPACITY_QTY, CREATED_BY, UPDATED_BY
  ) values (
    RRL_TOPO_CELL_SLOT_SQ.nextval, v_topology_id, v_storage_cell_id, 'STORAGE_SLOT',
    'STORAGE_SLOT', 'SMOKE-STOR-01-A', 2, 1, 1, 1, 10, 100,
    'SMOKE_041', 'SMOKE_041'
  );

  v_failed := 0;
  begin
    insert into RRL_WAREHOUSE_MAP_CAMERA (
      CAMERA_ID, CANVAS_ID, WARE_ID, CAMERA_CODE, CAMERA_NAME, CAMERA_KIND,
      WIDTH_M, DEPTH_M, HEIGHT_M, CREATED_BY, UPDATED_BY
    ) values (
      RRL_WH_MAP_CAMERA_SQ.nextval, v_canvas_id, -41041, 'CAM-A',
      'Duplicate camera code', 'DRY', 10, 10, 10, 'SMOKE_041', 'SMOKE_041'
    );
  exception
    when others then
      v_failed := 1;
  end;
  if v_failed = 0 then
    raise_application_error(-20410, 'duplicate camera_code did not fail');
  end if;

  v_failed := 0;
  begin
    insert into RRL_WAREHOUSE_MAP_CAMERA (
      CAMERA_ID, CANVAS_ID, WARE_ID, CAMERA_CODE, CAMERA_NAME, CAMERA_KIND,
      WIDTH_M, DEPTH_M, HEIGHT_M, CREATED_BY, UPDATED_BY
    ) values (
      RRL_WH_MAP_CAMERA_SQ.nextval, v_canvas_id, -41041, 'CAM-ZERO',
      'Zero camera', 'DRY', 0, 10, 10, 'SMOKE_041', 'SMOKE_041'
    );
  exception
    when others then
      v_failed := 1;
  end;
  if v_failed = 0 then
    raise_application_error(-20411, 'zero camera size did not fail');
  end if;

  v_failed := 0;
  begin
    insert into RRL_TOPOLOGY_CELL_SLOT (
      CELL_SLOT_ID, TOPOLOGY_ID, TOPOLOGY_CELL_ID, PARENT_SLOT_LAYER_KIND,
      SLOT_KIND, SLOT_CODE, CREATED_BY, UPDATED_BY
    ) values (
      RRL_TOPO_CELL_SLOT_SQ.nextval, v_topology_id, v_pick_cell_id, 'PICK_FACE_SLOT',
      'BAD_SLOT', 'SMOKE-BAD-SLOT', 'SMOKE_041', 'SMOKE_041'
    );
  exception
    when others then
      v_failed := 1;
  end;
  if v_failed = 0 then
    raise_application_error(-20412, 'invalid slot kind did not fail');
  end if;

  v_failed := 0;
  begin
    insert into RRL_TOPOLOGY_CELL_SLOT (
      CELL_SLOT_ID, TOPOLOGY_ID, TOPOLOGY_CELL_ID, PARENT_SLOT_LAYER_KIND,
      SLOT_KIND, SLOT_CODE, CREATED_BY, UPDATED_BY
    ) values (
      RRL_TOPO_CELL_SLOT_SQ.nextval, v_topology_id, v_pick_cell_id, 'STORAGE_SLOT',
      'STORAGE_SLOT', 'SMOKE-MIXED-SLOT', 'SMOKE_041', 'SMOKE_041'
    );
  exception
    when others then
      v_failed := 1;
  end;
  if v_failed = 0 then
    raise_application_error(-20413, 'mixed slot kind did not fail');
  end if;
end;
/

select 'CANVAS' object_kind, count(*) cnt
  from RRL_WAREHOUSE_MAP_CANVAS
 where CREATED_BY = 'SMOKE_041'
union all
select 'CAMERA', count(*)
  from RRL_WAREHOUSE_MAP_CAMERA
 where CREATED_BY = 'SMOKE_041'
union all
select 'CAMERA_LINK', count(*)
  from RRL_WAREHOUSE_MAP_CAMERA_LINK
 where CREATED_BY = 'SMOKE_041'
union all
select 'CELL_SLOT', count(*)
  from RRL_TOPOLOGY_CELL_SLOT
 where CREATED_BY = 'SMOKE_041';

commit;

prompt [migration 2026-05-22-041] smoke done
