prompt [migration 2026-05-17-015] smoke

declare
  v_legacy_order_id number;
  v_customer_order_id number;
  v_customer_id number;
  v_vehicle_type_id number;
  v_part_count number;
begin
  select ID
    into v_legacy_order_id
    from (
      select ID
        from RRL_ORDERS
       where ADDR is not null
       order by ID
    )
   where rownum = 1;

  v_customer_order_id := RRL_CUSTOMER_ORDER_API.import_legacy_order(
    p_legacy_order_id => v_legacy_order_id,
    p_created_by => 'SMOKE_015'
  );

  select CUSTOMER_ID
    into v_customer_id
    from RRL_CUSTOMER_ORDER
   where CUSTOMER_ORDER_ID = v_customer_order_id;

  select VEHICLE_TYPE_ID
    into v_vehicle_type_id
    from RRL_VEHICLE_TYPE
   where VEHICLE_TYPE_CODE = 'TRUCK_33';

  insert into RRL_CUSTOMER_SHELF_LIFE_RULE (
    SHELF_LIFE_RULE_ID, CUSTOMER_ID, ARTICUL, MIN_SHELF_LIFE_DAYS,
    RULE_PRIORITY, ACTIVE, VALID_FROM, CREATED_AT, CREATED_BY
  ) values (
    RRL_CSL_RULE_SQ.nextval, v_customer_id, 'SMOKE-ART-015', 30,
    10, 1, trunc(sysdate), sysdate, 'SMOKE_015'
  );

  insert into RRL_CUSTOMER_PRODUCT_STACK_RULE (
    STACK_RULE_ID, CUSTOMER_ID, ARTICUL, PALLET_CASE_QTY,
    ALLOW_TOP_STACKING, MUST_BE_SEPARATE_PALLET, RULE_PRIORITY,
    ACTIVE, VALID_FROM, CREATED_AT, CREATED_BY
  ) values (
    RRL_CPS_RULE_SQ.nextval, v_customer_id, 'SMOKE-ART-015', 60,
    1, 0, 10, 1, trunc(sysdate), sysdate, 'SMOKE_015'
  );

  insert into RRL_CUSTOMER_VEHICLE_RULE (
    CUSTOMER_VEHICLE_RULE_ID, CUSTOMER_ID, VEHICLE_TYPE_ID,
    MAX_PALLET_COUNT, SPLIT_ORDER_BY_CAPACITY, RULE_PRIORITY,
    ACTIVE, VALID_FROM, CREATED_AT, CREATED_BY
  ) values (
    RRL_CVR_SQ.nextval, v_customer_id, v_vehicle_type_id,
    33, 1, 10, 1, trunc(sysdate), sysdate, 'SMOKE_015'
  );

  v_part_count := RRL_CUSTOMER_RULE_API.split_order_by_pallet_capacity(
    p_customer_order_id => v_customer_order_id,
    p_total_pallet_count => 80,
    p_vehicle_type_id => v_vehicle_type_id,
    p_created_by => 'SMOKE_015'
  );
end;
/

select count(*) SHIPMENT_PART_COUNT,
       min(PLANNED_PALLET_COUNT) MIN_PALLETS,
       max(PLANNED_PALLET_COUNT) MAX_PALLETS,
       sum(PLANNED_PALLET_COUNT) TOTAL_PALLETS
  from RRL_SHIPMENT_PART
 where CREATED_BY = 'SMOKE_015';

prompt [migration 2026-05-17-015] smoke invalid objects
select object_type, object_name, status
  from user_objects
 where status <> 'VALID'
 order by object_type, object_name;
