prompt [migration 2026-05-17-017] smoke

declare
  v_articul varchar2(40);
  v_ware_id number;
  v_cell1 varchar2(60);
  v_cell2 varchar2(60);
  v_route_id number;
  v_route_cell1_id number;
  v_route_cell2_id number;
  v_pick_face1_id number;
  v_pick_face2_id number;
  v_customer_id number;
  v_order_id number;
  v_row_id number;
  v_pick_plan_id number;
  v_dummy_id number;
  v_case_task_count number;
  v_selected_count number;
  v_two_faces_count number;
begin
  select ARTICUL, WARE_ID
    into v_articul, v_ware_id
    from (
      select upper(substr(p.ARTICUL, 1, 40)) ARTICUL,
             c.WARE_ID,
             max(r.REMAIN) MAX_REMAIN
        from RRL_REMAINS r
        join RRL_PALLETS p
          on p.UID_PALLET = r.UID_POLETA
        join RRL_CELLS c
          on c.CELL = r.CELL
       where r.REMAIN > 1
         and p.ARTICUL is not null
         and c.WARE_ID is not null
       group by p.ARTICUL, c.WARE_ID
       order by max(r.REMAIN) desc
    )
   where rownum = 1;

  select min(CELL)
    into v_cell1
    from RRL_CELLS
   where WARE_ID = v_ware_id
     and nvl(OTBOR, 0) = 1;

  if v_cell1 is null then
    select min(CELL)
      into v_cell1
      from RRL_CELLS
     where WARE_ID = v_ware_id;
  end if;

  select min(CELL)
    into v_cell2
    from RRL_CELLS
   where WARE_ID = v_ware_id
     and CELL > v_cell1;

  if v_cell2 is null then
    v_cell2 := v_cell1 || '-ALT';
  end if;

  v_route_id := RRL_PICK_TOPOLOGY_API.upsert_route(
    p_route_code => 'SMOKE-017-ROUTE',
    p_route_name => 'SMOKE 017 ROUTE',
    p_ware_id => v_ware_id,
    p_route_kind => 'PICK',
    p_active => 1,
    p_updated_by => 'SMOKE_017'
  );

  v_route_cell1_id := RRL_PICK_TOPOLOGY_API.upsert_route_cell(
    p_pick_route_id => v_route_id,
    p_cell_code => v_cell1,
    p_pick_sequence => 10,
    p_zone_code => 'SMOKE',
    p_active => 1,
    p_updated_by => 'SMOKE_017'
  );

  v_route_cell2_id := RRL_PICK_TOPOLOGY_API.upsert_route_cell(
    p_pick_route_id => v_route_id,
    p_cell_code => v_cell2,
    p_pick_sequence => 20,
    p_zone_code => 'SMOKE',
    p_active => 1,
    p_updated_by => 'SMOKE_017'
  );

  v_pick_face1_id := RRL_PICK_TOPOLOGY_API.upsert_pick_face(
    p_ware_id => v_ware_id,
    p_cell_code => v_cell1,
    p_pick_face_code => 'SMOKE-017-PF-1',
    p_pick_face_type => 'REGULAR',
    p_pick_route_id => v_route_id,
    p_pick_route_cell_id => v_route_cell1_id,
    p_min_case_qty => 0,
    p_max_case_qty => 100,
    p_replenishment_trigger_qty => 10,
    p_active => 1,
    p_updated_by => 'SMOKE_017'
  );

  v_pick_face2_id := RRL_PICK_TOPOLOGY_API.upsert_pick_face(
    p_ware_id => v_ware_id,
    p_cell_code => v_cell2,
    p_pick_face_code => 'SMOKE-017-PF-2',
    p_pick_face_type => 'REGULAR',
    p_pick_route_id => v_route_id,
    p_pick_route_cell_id => v_route_cell2_id,
    p_min_case_qty => 0,
    p_max_case_qty => 100,
    p_replenishment_trigger_qty => 10,
    p_active => 1,
    p_updated_by => 'SMOKE_017'
  );

  v_dummy_id := RRL_PICK_TOPOLOGY_API.assign_articul(
    p_pick_face_id => v_pick_face1_id,
    p_articul => v_articul,
    p_priority => 10,
    p_case_pick_enabled => 1,
    p_active => 1,
    p_updated_by => 'SMOKE_017'
  );

  v_dummy_id := RRL_PICK_TOPOLOGY_API.assign_articul(
    p_pick_face_id => v_pick_face2_id,
    p_articul => v_articul,
    p_priority => 20,
    p_case_pick_enabled => 1,
    p_active => 1,
    p_updated_by => 'SMOKE_017'
  );

  select count(*)
    into v_two_faces_count
    from RRL_PICK_FACE_ARTICUL
   where upper(ARTICUL) = upper(v_articul)
     and CREATED_BY = 'SMOKE_017';

  if v_two_faces_count < 2 then
    raise_application_error(-20011, '017 smoke failed: two pick faces were not assigned');
  end if;

  select RRL_CUSTOMER_SQ.nextval into v_customer_id from dual;
  insert into RRL_CUSTOMER (
    CUSTOMER_ID, CUSTOMER_CODE, CUSTOMER_NAME, CUSTOMER_TYPE, ACTIVE, CREATED_AT, CREATED_BY
  ) values (
    v_customer_id, 'SMOKE-017-CUSTOMER', 'SMOKE 017 CUSTOMER', 'STORE', 1, sysdate, 'SMOKE_017'
  );

  select RRL_CUSTOMER_ORDER_SQ.nextval into v_order_id from dual;
  insert into RRL_CUSTOMER_ORDER (
    CUSTOMER_ORDER_ID, ORDER_NO, CUSTOMER_ID, WARE_ID, ORDER_DATE, SHIPMENT_DATE,
    STATUS, SOURCE_SYSTEM, CREATED_AT, CREATED_BY
  ) values (
    v_order_id, 'SMOKE-017-ORDER', v_customer_id, v_ware_id, sysdate, trunc(sysdate),
    'OPEN', 'SMOKE', sysdate, 'SMOKE_017'
  );

  select RRL_CUSTOMER_ORDER_ROW_SQ.nextval into v_row_id from dual;
  insert into RRL_CUSTOMER_ORDER_ROW (
    CUSTOMER_ORDER_ROW_ID, CUSTOMER_ORDER_ID, LINE_NO, ARTICUL,
    PRODUCT_NAME, UNIT_CODE, ORDER_QTY, STATUS, CREATED_AT, CREATED_BY
  ) values (
    v_row_id, v_order_id, 10, v_articul,
    'SMOKE 017 PRODUCT', 'PCS', 1, 'OPEN', sysdate, 'SMOKE_017'
  );

  v_pick_plan_id := RRL_PICKING_API.create_plan(
    p_customer_order_id => v_order_id,
    p_plan_strategy => 'FEFO',
    p_created_by => 'SMOKE_017'
  );

  select count(*)
    into v_case_task_count
    from RRL_PICK_TASK
   where PICK_PLAN_ID = v_pick_plan_id
     and TASK_TYPE = 'CASE_PICK';

  select count(*)
    into v_selected_count
    from RRL_PICK_TASK
   where PICK_PLAN_ID = v_pick_plan_id
     and TASK_TYPE = 'CASE_PICK'
     and TARGET_CELL_CODE = v_cell1
     and PICK_SEQUENCE = 10
     and PICK_FACE_ID = v_pick_face1_id
     and PICK_ROUTE_CELL_ID = v_route_cell1_id;

  if v_case_task_count = 0 or v_selected_count = 0 then
    raise_application_error(-20012, '017 smoke failed: case task did not use primary pick face');
  end if;
end;
/

select t.PICK_TASK_ID,
       t.TASK_TYPE,
       t.ARTICUL,
       t.SOURCE_CELL_CODE,
       t.TARGET_CELL_CODE,
       t.PICK_SEQUENCE,
       t.PICK_FACE_ID,
       t.PICK_ROUTE_CELL_ID
  from RRL_PICK_TASK t
 where t.CREATED_BY = 'SMOKE_017'
 order by t.PICK_SEQUENCE nulls last, t.PICK_TASK_ID;

prompt [migration 2026-05-17-017] smoke invalid objects
select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;
