create or replace package RRL_WEIGHT_BOX_PLANNING_READ authid definer as
 function snapshot_json(p_row number,p_actor varchar2)return clob;
end;
/
create or replace package body RRL_WEIGHT_BOX_PLANNING_READ as
 function snapshot_json(p_row number,p_actor varchar2)return clob is
  o RRL_CUSTOMER_ORDER_ROW%rowtype;ware number;version number;pct number;marked number;serial_flag number;
  demand json_object_t;part json_object_t;result_json json_object_t:=json_object_t();item json_object_t;
  boxes json_array_t:=json_array_t();requested number:=0;actual number:=0;remaining number;soft_qty number;projected number;
  lower_qty number;upper_qty number;rows_count number:=0;stocks_count number:=0;more_boxes boolean:=false;state_value varchar2(20);
 begin
  if p_row is null or p_row<1 or p_row!=trunc(p_row)then raise_application_error(-20881,'WEIGHT_BOX_ORDER_ROW_REQUIRED');end if;
  select *into o from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ROW_ID=p_row;
  RRL_PICK_PLAN_ACCESS.assert_scope(o.CUSTOMER_ORDER_ID,p_actor);
  select WARE_ID into ware from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=o.CUSTOMER_ORDER_ID;
  select STATE into state_value from RRL_STOCK_RELEASE where RELEASE_ID=1;
  if state_value is null or state_value!='ACTIVE'then raise_application_error(-20860,'WEIGHT_BOX_PLANNING_ACTIVE_REQUIRED');end if;
  select POLICY_VERSION,ORDER_WEIGHT_TOLERANCE_PCT,MARKING_REQUIRED,SERIALIZED_WEIGHT_BOXES into version,pct,marked,serial_flag
   from RRL_SKU_RECEIPT_POLICY where ARTICUL=o.ARTICUL;
  if serial_flag!=1 then raise_application_error(-20886,'WEIGHT_BOX_PLANNING_SERIALIZED_SKU_REQUIRED');end if;
  RRL_WEIGHT_BOX_READ.assert_sku(o.ARTICUL,null);
  demand:=json_object_t.parse(RRL_STOCK_POOL_READ.line_snapshot_json(p_row));
  if not demand.get_boolean('open')or demand.get_string('unit')!='KG' or demand.get_number('warehouse')!=ware then raise_application_error(-20886,'WEIGHT_BOX_OPEN_CURRENT_KG_ORDER_REQUIRED');end if;
  remaining:=case when demand.get_string('quantity')='0'then 0 else RRL_STOCK_MATH.quantity(demand.get_string('quantity'))end;
  select nvl(sum(pr.RESERVED_QTY),0)into soft_qty from RRL_PICK_RESERVATION pr
   join RRL_PICK_PLAN_LINE pl on pl.PICK_PLAN_LINE_ID=pr.PICK_PLAN_LINE_ID join RRL_PICK_PLAN pp on pp.PICK_PLAN_ID=pl.PICK_PLAN_ID
   where pl.CUSTOMER_ORDER_ROW_ID=p_row and pr.RESERVATION_STATUS='ACTIVE'and pr.RESERVATION_LEVEL='SOFT'
    and pp.STATUS in('DRAFT','PLANNED_FULL','PLANNED_PARTIAL');
  remaining:=greatest(remaining-soft_qty,0);
  for cr in(select CUSTOMER_ORDER_ROW_ID from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=o.CUSTOMER_ORDER_ID and ARTICUL=o.ARTICUL
   and STATUS not in('CANCELLED','REJECTED')order by CUSTOMER_ORDER_ROW_ID fetch first 201 rows only)loop
   rows_count:=rows_count+1;if rows_count>200 then raise_application_error(-20881,'WEIGHT_BOX_ORDER_ROWS_BOUND');end if;
   part:=json_object_t.parse(RRL_STOCK_POOL_READ.line_snapshot_json(cr.CUSTOMER_ORDER_ROW_ID));
   if part.get_string('unit')!='KG'or part.get_number('warehouse')!=ware then raise_application_error(-20886,'WEIGHT_BOX_ORDER_SKU_KG_SOURCE_REQUIRED');end if;
   requested:=requested+RRL_STOCK_MATH.quantity(part.get_string('requested_base_quantity'));
   if part.get_string('picked_quantity')!='0'then actual:=actual+RRL_STOCK_MATH.quantity(part.get_string('picked_quantity'));end if;
  end loop;
  lower_qty:=requested*(1-pct/100);upper_qty:=requested*(1+pct/100);
  if remaining>0 then
   for lot in(select r.UID_POLETA,r.CELL,r.REMAIN,r.HARD_RESERVED_BASE,r.STOCK_VERSION,p.EXPIRY_DATE
    from RRL_REMAINS r join RRL_PALLETS p on p.UID_PALLET=r.UID_POLETA join RRL_CELLS c on c.CELL=r.CELL
    where p.ARTICUL=o.ARTICUL and c.WARE_ID=ware and r.BASE_UOM='KG'and r.REMAIN-r.HARD_RESERVED_BASE>0
     and RRL_STOCK_ELIGIBILITY.reason(r.UID_POLETA,r.CELL,ware,0,null,null,'ALLOCATE',null,o.ARTICUL)is null
    order by p.EXPIRY_DATE nulls last,r.UID_POLETA,r.CELL fetch first 201 rows only)loop
    stocks_count:=stocks_count+1;if stocks_count>200 then more_boxes:=true;exit;end if;
    for unit_row in(select PHYSICAL_UNIT_KEY,BASE_QTY,GROSS_WEIGHT_KG,BOX_VOLUME_M3,MEASUREMENT_REFERENCE,WEIGHT_LABEL_SCAN,UNIT_ID
     from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=lot.UID_POLETA and CURRENT_CELL=lot.CELL
      and STOCK_STATUS='AVAILABLE'and HARD_RESERVATION_ID is null and BASE_UOM='KG'and BASE_QTY>0
      and BASE_QTY<=lot.REMAIN-lot.HARD_RESERVED_BASE
     order by PHYSICAL_UNIT_KEY fetch first 101 rows only)loop
     if boxes.get_size=100 then more_boxes:=true;exit;end if;
     projected:=actual+unit_row.BASE_QTY;
     item:=json_object_t();item.put('physical_unit_key',unit_row.PHYSICAL_UNIT_KEY);item.put('unit_id',unit_row.UNIT_ID);
     item.put('pallet_identifier',lot.UID_POLETA);item.put('source_cell',lot.CELL);item.put('stock_version',lot.STOCK_VERSION);
     item.put('net_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(unit_row.BASE_QTY));
     item.put('gross_weight_kg',case when unit_row.GROSS_WEIGHT_KG is null then null else RRL_STOCK_PLAN_HELPER.decimal_text(unit_row.GROSS_WEIGHT_KG)end);
     item.put('volume_m3',case when unit_row.BOX_VOLUME_M3 is null then null else RRL_STOCK_PLAN_HELPER.decimal_text(unit_row.BOX_VOLUME_M3)end);
     item.put('weighted_box_barcode',unit_row.WEIGHT_LABEL_SCAN);item.put('measurement_reference',unit_row.MEASUREMENT_REFERENCE);
     item.put('projected_order_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(projected));
     item.put('within_tolerance',projected>=lower_qty and projected<=upper_qty);
     item.put('exception_required',projected<lower_qty or projected>upper_qty);
     item.put('measurements_ready',unit_row.GROSS_WEIGHT_KG is not null and unit_row.GROSS_WEIGHT_KG>=unit_row.BASE_QTY
      and unit_row.BOX_VOLUME_M3 is not null and unit_row.BOX_VOLUME_M3>0 and unit_row.MEASUREMENT_REFERENCE is not null and unit_row.WEIGHT_LABEL_SCAN is not null);
     boxes.append(item);
    end loop;
    exit when more_boxes;
   end loop;
  end if;
  result_json.put('customer_order_row_id',p_row);result_json.put('customer_order_id',o.CUSTOMER_ORDER_ID);
  result_json.put('article',o.ARTICUL);result_json.put('warehouse_id',ware);result_json.put('policy_version',version);
  result_json.put('tolerance_pct',RRL_STOCK_PLAN_HELPER.decimal_text(pct));result_json.put('unit','KG');
  result_json.put('requested_order_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(requested));result_json.put('picked_order_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(actual));
  result_json.put('remaining_row_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(remaining));result_json.put('active_soft_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(soft_qty));
  result_json.put('marking_required',marked=1);result_json.put('no_split',true);result_json.put('boxes',boxes);result_json.put('has_more',more_boxes);
  result_json.put('choice_saved',false);result_json.put('approval_required',true);
  result_json.put('source_signature',rawtohex(sys.dbms_crypto.hash(result_json.to_clob,sys.dbms_crypto.hash_sh256)));
  return result_json.to_clob;
 exception when no_data_found or too_many_rows then raise_application_error(-20886,'WEIGHT_BOX_CURRENT_ORDER_OR_POLICY_NOT_UNIQUE');
 end;
end;
/
