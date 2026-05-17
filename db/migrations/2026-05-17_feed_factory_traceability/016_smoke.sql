prompt [migration 2026-05-17-016] smoke

declare
  v_customer_id number;
  v_order_id number;
  v_row_id number;
  v_articul varchar2(40);
  v_pick_plan_id number;
  v_status varchar2(30);
  v_planned_qty number;
  v_reservation_count number;
begin
  select upper(substr(p.ARTICUL, 1, 40))
    into v_articul
    from (
      select p.ARTICUL, sum(r.REMAIN) QTY
        from RRL_REMAINS r
        join RRL_PALLETS p
          on p.UID_PALLET = r.UID_POLETA
       where r.REMAIN > 0
         and p.ARTICUL is not null
       group by p.ARTICUL
       order by sum(r.REMAIN) desc
    ) p
   where rownum = 1;

  select RRL_CUSTOMER_SQ.nextval into v_customer_id from dual;
  insert into RRL_CUSTOMER (
    CUSTOMER_ID, CUSTOMER_CODE, CUSTOMER_NAME, CUSTOMER_TYPE, ACTIVE, CREATED_AT, CREATED_BY
  ) values (
    v_customer_id, 'SMOKE-016-CUSTOMER', 'SMOKE 016 CUSTOMER', 'STORE', 1, sysdate, 'SMOKE_016'
  );

  select RRL_CUSTOMER_ORDER_SQ.nextval into v_order_id from dual;
  insert into RRL_CUSTOMER_ORDER (
    CUSTOMER_ORDER_ID, ORDER_NO, CUSTOMER_ID, WARE_ID, ORDER_DATE, SHIPMENT_DATE,
    STATUS, SOURCE_SYSTEM, CREATED_AT, CREATED_BY
  ) values (
    v_order_id, 'SMOKE-016-ORDER', v_customer_id, null, sysdate, trunc(sysdate),
    'OPEN', 'SMOKE', sysdate, 'SMOKE_016'
  );

  select RRL_CUSTOMER_ORDER_ROW_SQ.nextval into v_row_id from dual;
  insert into RRL_CUSTOMER_ORDER_ROW (
    CUSTOMER_ORDER_ROW_ID, CUSTOMER_ORDER_ID, LINE_NO, ARTICUL,
    PRODUCT_NAME, UNIT_CODE, ORDER_QTY, STATUS, CREATED_AT, CREATED_BY
  ) values (
    v_row_id, v_order_id, 10, v_articul,
    'SMOKE 016 PRODUCT', 'PCS', 10, 'OPEN', sysdate, 'SMOKE_016'
  );

  v_pick_plan_id := RRL_PICKING_API.create_plan(
    p_customer_order_id => v_order_id,
    p_plan_strategy => 'FEFO',
    p_created_by => 'SMOKE_016'
  );

  select STATUS, TOTAL_PLANNED_QTY
    into v_status, v_planned_qty
    from RRL_PICK_PLAN
   where PICK_PLAN_ID = v_pick_plan_id;

  select count(*)
    into v_reservation_count
    from RRL_PICK_RESERVATION
   where PICK_PLAN_ID = v_pick_plan_id
     and RESERVATION_STATUS = 'ACTIVE';

  if v_status not in ('PLANNED_FULL', 'PLANNED_PARTIAL') then
    raise_application_error(-20001, '016 smoke failed: unexpected plan status ' || v_status);
  end if;

  if nvl(v_planned_qty, 0) <= 0 or v_reservation_count <= 0 then
    raise_application_error(-20002, '016 smoke failed: plan did not create active reservations');
  end if;
end;
/

select p.PICK_PLAN_ID,
       p.STATUS,
       p.TOTAL_ORDER_QTY,
       p.TOTAL_PLANNED_QTY,
       p.TOTAL_SHORTAGE_QTY,
       count(distinct r.PICK_RESERVATION_ID) RESERVATIONS,
       count(distinct t.PICK_TASK_ID) TASKS
  from RRL_PICK_PLAN p
  left join RRL_PICK_RESERVATION r
    on r.PICK_PLAN_ID = p.PICK_PLAN_ID
  left join RRL_PICK_TASK t
    on t.PICK_PLAN_ID = p.PICK_PLAN_ID
 where p.CREATED_BY = 'SMOKE_016'
 group by p.PICK_PLAN_ID, p.STATUS, p.TOTAL_ORDER_QTY, p.TOTAL_PLANNED_QTY, p.TOTAL_SHORTAGE_QTY
 order by p.PICK_PLAN_ID;

prompt [migration 2026-05-17-016] smoke invalid objects
select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;
