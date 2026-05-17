prompt [migration 2026-05-17-018] smoke

declare
  v_customer_id number;
  v_order_id number;
  v_row_id number;
  v_articul varchar2(40);
  v_ware_id number;
  v_pick_plan_id number;
  v_pick_wave_id number;
  v_wave_status varchar2(30);
  v_plan_status varchar2(30);
  v_soft_before number;
  v_hard_after_launch number;
  v_soft_after_cancel number;
  v_wave_res_count number;
  v_wave_line_count number;
  v_wave_demand_count number;
  v_wave_task_count number;
  v_audit_count number;
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

  select RRL_CUSTOMER_SQ.nextval into v_customer_id from dual;
  insert into RRL_CUSTOMER (
    CUSTOMER_ID, CUSTOMER_CODE, CUSTOMER_NAME, CUSTOMER_TYPE, ACTIVE, CREATED_AT, CREATED_BY
  ) values (
    v_customer_id, 'SMOKE-018-CUSTOMER', 'SMOKE 018 CUSTOMER', 'STORE', 1, sysdate, 'SMOKE_018'
  );

  select RRL_CUSTOMER_ORDER_SQ.nextval into v_order_id from dual;
  insert into RRL_CUSTOMER_ORDER (
    CUSTOMER_ORDER_ID, ORDER_NO, CUSTOMER_ID, WARE_ID, ORDER_DATE, SHIPMENT_DATE,
    STATUS, SOURCE_SYSTEM, CREATED_AT, CREATED_BY
  ) values (
    v_order_id, 'SMOKE-018-ORDER', v_customer_id, v_ware_id, sysdate, trunc(sysdate),
    'OPEN', 'SMOKE', sysdate, 'SMOKE_018'
  );

  select RRL_CUSTOMER_ORDER_ROW_SQ.nextval into v_row_id from dual;
  insert into RRL_CUSTOMER_ORDER_ROW (
    CUSTOMER_ORDER_ROW_ID, CUSTOMER_ORDER_ID, LINE_NO, ARTICUL,
    PRODUCT_NAME, UNIT_CODE, ORDER_QTY, STATUS, CREATED_AT, CREATED_BY
  ) values (
    v_row_id, v_order_id, 10, v_articul,
    'SMOKE 018 PRODUCT', 'PCS', 1, 'OPEN', sysdate, 'SMOKE_018'
  );

  v_pick_plan_id := RRL_PICKING_API.create_plan(
    p_customer_order_id => v_order_id,
    p_plan_strategy => 'FEFO',
    p_created_by => 'SMOKE_018'
  );

  select count(*)
    into v_soft_before
    from RRL_PICK_RESERVATION
   where PICK_PLAN_ID = v_pick_plan_id
     and RESERVATION_STATUS = 'ACTIVE'
     and RESERVATION_LEVEL = 'SOFT';

  if v_soft_before = 0 then
    raise_application_error(-20030, '018 smoke failed: picking plan did not create soft reservations');
  end if;

  v_pick_wave_id := RRL_PICK_WAVE_API.create_wave(
    p_wave_code => 'SMOKE-018-WAVE',
    p_wave_name => 'SMOKE 018 WAVE',
    p_ware_id => v_ware_id,
    p_max_customers => 30,
    p_created_by => 'SMOKE_018'
  );

  RRL_PICK_WAVE_API.add_plan(
    p_pick_wave_id => v_pick_wave_id,
    p_pick_plan_id => v_pick_plan_id,
    p_created_by => 'SMOKE_018'
  );

  RRL_PICK_WAVE_API.preview_wave(
    p_pick_wave_id => v_pick_wave_id,
    p_updated_by => 'SMOKE_018'
  );

  select STATUS
    into v_wave_status
    from RRL_PICK_WAVE
   where PICK_WAVE_ID = v_pick_wave_id;

  select count(*) into v_wave_line_count from RRL_PICK_WAVE_LINE where PICK_WAVE_ID = v_pick_wave_id;
  select count(*) into v_wave_demand_count from RRL_PICK_WAVE_DEMAND where PICK_WAVE_ID = v_pick_wave_id;

  if v_wave_status <> 'PREVIEW' or v_wave_line_count = 0 or v_wave_demand_count = 0 then
    raise_application_error(-20031, '018 smoke failed: preview did not build wave demand');
  end if;

  RRL_PICK_WAVE_API.launch_wave(
    p_pick_wave_id => v_pick_wave_id,
    p_launched_by => 'SMOKE_018'
  );

  select STATUS into v_wave_status from RRL_PICK_WAVE where PICK_WAVE_ID = v_pick_wave_id;
  select STATUS into v_plan_status from RRL_PICK_PLAN where PICK_PLAN_ID = v_pick_plan_id;

  select count(*)
    into v_hard_after_launch
    from RRL_PICK_RESERVATION
   where PICK_PLAN_ID = v_pick_plan_id
     and RESERVATION_STATUS = 'ACTIVE'
     and RESERVATION_LEVEL = 'HARD';

  select count(*) into v_wave_res_count from RRL_PICK_WAVE_RESERVATION where PICK_WAVE_ID = v_pick_wave_id and RESERVATION_STATUS = 'HARD';
  select count(*) into v_wave_task_count from RRL_PICK_WAVE_TASK where PICK_WAVE_ID = v_pick_wave_id;

  if v_wave_status <> 'LAUNCHED'
     or v_plan_status <> 'RELEASED'
     or v_hard_after_launch <> v_soft_before
     or v_wave_res_count <> v_soft_before
     or v_wave_task_count = 0 then
    raise_application_error(-20032, '018 smoke failed: launch did not create hard wave reservations and tasks');
  end if;

  RRL_PICK_WAVE_API.cancel_wave(
    p_pick_wave_id => v_pick_wave_id,
    p_reason => 'SMOKE 018 CANCEL',
    p_updated_by => 'SMOKE_018'
  );

  select STATUS into v_wave_status from RRL_PICK_WAVE where PICK_WAVE_ID = v_pick_wave_id;

  select count(*)
    into v_soft_after_cancel
    from RRL_PICK_RESERVATION
   where PICK_PLAN_ID = v_pick_plan_id
     and RESERVATION_STATUS = 'ACTIVE'
     and RESERVATION_LEVEL = 'SOFT';

  select count(*)
    into v_audit_count
    from RRL_PICK_WAVE_AUDIT
   where PICK_WAVE_ID = v_pick_wave_id;

  if v_wave_status <> 'CANCELLED' or v_soft_after_cancel <> v_soft_before or v_audit_count < 4 then
    raise_application_error(-20033, '018 smoke failed: cancel did not release hard reservations');
  end if;
end;
/

select w.PICK_WAVE_ID,
       w.WAVE_CODE,
       w.STATUS,
       w.CUSTOMER_COUNT,
       w.PLAN_COUNT,
       w.TASK_COUNT,
       w.HARD_RESERVE_QTY,
       w.CREATED_BY
  from RRL_PICK_WAVE w
 where w.CREATED_BY = 'SMOKE_018'
 order by w.PICK_WAVE_ID;

select wr.PICK_WAVE_ID,
       wr.RESERVATION_STATUS,
       count(*) CNT,
       sum(wr.RESERVED_QTY) QTY
  from RRL_PICK_WAVE_RESERVATION wr
 where wr.CREATED_BY = 'SMOKE_018'
 group by wr.PICK_WAVE_ID, wr.RESERVATION_STATUS
 order by wr.PICK_WAVE_ID, wr.RESERVATION_STATUS;

prompt [migration 2026-05-17-018] smoke invalid objects
select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;
