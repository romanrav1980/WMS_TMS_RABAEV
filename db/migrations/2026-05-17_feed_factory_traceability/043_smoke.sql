prompt [migration 2026-05-23-043] warehouse map operation idempotency keys - smoke

delete from RRL_PICK_ROUTE where CREATED_BY = 'SMOKE_043';
delete from RRL_WAREHOUSE_MAP_CANVAS where CREATED_BY = 'SMOKE_043';
delete from RRL_WAREHOUSE_TOPOLOGY where CREATED_BY = 'SMOKE_043';
commit;

declare
  v_topology_id number;
  v_canvas_id number;
  v_route_id number;
begin
  v_topology_id := RRL_WH_TOPOLOGY_SQ.nextval;
  insert into RRL_WAREHOUSE_TOPOLOGY (
    TOPOLOGY_ID, WARE_ID, TOPOLOGY_CODE, TOPOLOGY_NAME, VERSION_NO,
    STATUS, IDEMPOTENCY_KEY, CREATED_BY, UPDATED_BY
  ) values (
    v_topology_id, -43043, 'SMOKE-043-TOPO', 'Smoke 043 topology', 1,
    'DRAFT', 'SMOKE-043-PROJECTION', 'SMOKE_043', 'SMOKE_043'
  );

  v_canvas_id := RRL_WH_MAP_CANVAS_SQ.nextval;
  insert into RRL_WAREHOUSE_MAP_CANVAS (
    CANVAS_ID, WARE_ID, TOPOLOGY_ID, CANVAS_CODE, CANVAS_NAME, VERSION_NO,
    STATUS, RENDERER_KIND, UNIT_CODE, GRID_CELL_WIDTH_M, GRID_CELL_DEPTH_M, LEVELS,
    IDEMPOTENCY_KEY, PUBLISH_IDEMPOTENCY_KEY, CREATED_BY, UPDATED_BY
  ) values (
    v_canvas_id, -43043, v_topology_id, 'SMOKE-043-CANVAS', 'Smoke 043 canvas', 1,
    'PUBLISHED', 'CANVAS_2D', 'METER', 1.2, 0.8, 1,
    'SMOKE-043-CANVAS-SAVE', 'SMOKE-043-PUBLISH', 'SMOKE_043', 'SMOKE_043'
  );

  v_route_id := RRL_PICK_ROUTE_SQ.nextval;
  insert into RRL_PICK_ROUTE (
    PICK_ROUTE_ID, TOPOLOGY_ID, ROUTE_CODE, ROUTE_NAME, WARE_ID,
    ROUTE_KIND, ROUTE_PATTERN, STRICT_SEQUENCE, STATUS, ACTIVE,
    IDEMPOTENCY_KEY, CREATED_BY, UPDATED_BY
  ) values (
    v_route_id, v_topology_id, 'SMOKE-043-ROUTE', 'Smoke 043 route', -43043,
    'PICK', 'MANUAL', 1, 'DRAFT', 1,
    'SMOKE-043-ROUTE-SAVE', 'SMOKE_043', 'SMOKE_043'
  );
end;
/

select count(*) SMOKE_CANVAS_BY_IDEMP
  from RRL_WAREHOUSE_MAP_CANVAS
 where WARE_ID = -43043
   and upper(IDEMPOTENCY_KEY) = 'SMOKE-043-CANVAS-SAVE'
   and ACTIVE = 1;

select count(*) SMOKE_TOPOLOGY_BY_IDEMP
  from RRL_WAREHOUSE_TOPOLOGY
 where WARE_ID = -43043
   and upper(IDEMPOTENCY_KEY) = 'SMOKE-043-PROJECTION'
   and STATUS <> 'ARCHIVED';

select count(*) SMOKE_ROUTE_BY_IDEMP
  from RRL_PICK_ROUTE
 where WARE_ID = -43043
   and upper(IDEMPOTENCY_KEY) = 'SMOKE-043-ROUTE-SAVE'
   and ACTIVE = 1
   and STATUS <> 'ARCHIVED';

commit;

prompt [migration 2026-05-23-043] smoke done
