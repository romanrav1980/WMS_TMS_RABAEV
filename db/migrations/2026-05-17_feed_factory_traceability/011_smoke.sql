prompt [migration 2026-05-17-011] MES production completion - smoke

declare
  v_bom_id number;
  v_order_id number;
  v_completion_id number;
  v_prod_batch_id number;
  v_raw_move_id number;
  v_line_id number;
  v_remain number;
begin
  v_bom_id := RRL_BOM_API.create_bom(
    p_bom_code => 'MES-SMOKE-BOM-011',
    p_bom_name => 'MES smoke BOM 011',
    p_target_articul => 'MES-SMOKE-FG-011',
    p_base_qty => 100,
    p_base_unit_code => 'KG',
    p_valid_from => trunc(sysdate),
    p_created_by => 'smoke'
  );

  v_line_id := RRL_BOM_API.add_line(
    p_bom_id => v_bom_id,
    p_line_no => 10,
    p_component_type => 'RAW',
    p_component_articul => 'MES-SMOKE-RAW-011',
    p_qty_per_base => 50,
    p_unit_code => 'KG',
    p_created_by => 'smoke'
  );

  RRL_BOM_API.approve_bom(v_bom_id, 'smoke');

  v_order_id := RRL_MES_PRODUCTION_API.create_order(
    p_order_no => 'MES-SMOKE-ORDER-011',
    p_bom_id => v_bom_id,
    p_target_articul => 'MES-SMOKE-FG-011',
    p_planned_qty => 100,
    p_unit_code => 'KG',
    p_created_by => 'smoke'
  );

  v_raw_move_id := RRL_MES_PRODUCTION_API.issue_raw_to_production(
    p_production_order_id => v_order_id,
    p_uid_pallet => 'MES-SMOKE-RAW-PALLET-011',
    p_raw_articul => 'MES-SMOKE-RAW-011',
    p_quantity => 50,
    p_unit_code => 'KG',
    p_source_location => 'RAW_SMOKE',
    p_production_location => 'MES_PROD',
    p_created_by => 'smoke'
  );

  v_completion_id := RRL_MES_PRODUCTION_API.complete_order(
    p_production_order_id => v_order_id,
    p_prod_batch_no => 'MES-SMOKE-LOT-011',
    p_fact_qty => 100,
    p_unit_code => 'KG',
    p_pallets_json => '[{"uid_pallet":"MES-SMOKE-FG-PALLET-011","pallet_no":1,"quantity":100,"pack_count":10,"sscc":"000000000000000011"}]',
    p_idempotency_key => 'MES-SMOKE-COMPLETE-011',
    p_created_by => 'smoke'
  );

  RRL_MES_PRODUCTION_API.apply_mes_movements_to_wms(v_order_id, 'smoke');

  select PROD_BATCH_ID
    into v_prod_batch_id
    from RRL_PRODUCTION_ORDER
   where PRODUCTION_ORDER_ID = v_order_id;

  select nvl(sum(REMAIN), 0)
    into v_remain
    from RRL_REMAINS
   where UID_POLETA = 'MES-SMOKE-FG-PALLET-011'
     and CELL = 'MES_FG';

  dbms_output.put_line('BOM_ID=' || v_bom_id);
  dbms_output.put_line('ORDER_ID=' || v_order_id);
  dbms_output.put_line('RAW_MOVE_ID=' || v_raw_move_id);
  dbms_output.put_line('COMPLETION_ID=' || v_completion_id);
  dbms_output.put_line('PROD_BATCH_ID=' || v_prod_batch_id);
  dbms_output.put_line('FG_REMAIN=' || v_remain);
end;
/

select MOVEMENT_TYPE, STATUS, UID_PALLET, QUANTITY
  from RRL_MES_MOVEMENT
 where PRODUCTION_ORDER_ID = (
   select PRODUCTION_ORDER_ID
     from RRL_PRODUCTION_ORDER
    where ORDER_NO = 'MES-SMOKE-ORDER-011'
 )
 order by MOVEMENT_ID;

select TYPE_EVENT, CELL_FROM, CELL_TO, COUNT_EVENT, UID_POLETA
  from RRL_EVENTS
 where UID_POLETA in ('MES-SMOKE-RAW-PALLET-011', 'MES-SMOKE-FG-PALLET-011')
 order by ID_EVENT;
