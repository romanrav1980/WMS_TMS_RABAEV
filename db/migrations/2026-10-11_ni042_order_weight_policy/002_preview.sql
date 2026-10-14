create or replace package RRL_ORDER_WEIGHT_READ authid definer as
 function snapshot_json(p_task number,p_line number,p_actor varchar2)return clob;
end;
/
create or replace package body RRL_ORDER_WEIGHT_READ as
 function snapshot_json(p_task number,p_line number,p_actor varchar2)return clob is
  t RRL_CASE_PICK_TASK%rowtype;l RRL_CASE_PICK_LINE%rowtype;
  order_id number;article varchar2(160);pct number;version number;requested number:=0;actual number:=0;
  row_json json_object_t;result_json json_object_t:=json_object_t();rows_json json_array_t:=json_array_t();
  lower_qty number;upper_qty number;n number;
 begin
  RRL_CASE_TASK_ACCESS.assert_scope(p_task,p_actor,'case_pick_execute');
  select *into t from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=p_task;
  select *into l from RRL_CASE_PICK_LINE where CASE_PICK_TASK_ID=p_task and CASE_PICK_LINE_ID=p_line;
  order_id:=l.CUSTOMER_ORDER_ID;
  article:=l.ARTICUL;
  select count(*)into n from RRL_ARTICULS where ACTICUL=article and TYPE_W in(2,3,5,6,7);
  if n!=1 then raise_application_error(-20886,'ORDER_WEIGHT_CURRENT_WEIGHTED_SKU_REQUIRED');end if;
  select nvl(max(ORDER_WEIGHT_TOLERANCE_PCT),15),nvl(max(POLICY_VERSION),0)into pct,version from RRL_SKU_RECEIPT_POLICY where ARTICUL=article;
  for o in(select CUSTOMER_ORDER_ROW_ID from RRL_CUSTOMER_ORDER_ROW where CUSTOMER_ORDER_ID=order_id and ARTICUL=article
   and STATUS not in('CANCELLED','REJECTED') order by CUSTOMER_ORDER_ROW_ID fetch first 201 rows only)loop
   if rows_json.get_size=200 then raise_application_error(-20881,'ORDER_WEIGHT_ROWS_BOUND_200');end if;
   row_json:=json_object_t.parse(RRL_STOCK_POOL_READ.line_snapshot_json(o.CUSTOMER_ORDER_ROW_ID));
   if row_json.get_string('unit')!='KG' or row_json.get_number('warehouse')!=t.WARE_ID then raise_application_error(-20886,'ORDER_WEIGHT_ORIGINAL_KG_WARE_REQUIRED');end if;
   requested:=requested+RRL_STOCK_MATH.quantity(row_json.get_string('requested_base_quantity'));
   if row_json.get_string('picked_quantity')!='0'then actual:=actual+RRL_STOCK_MATH.quantity(row_json.get_string('picked_quantity'));end if;
   rows_json.append(row_json);
  end loop;
  if requested<=0 then raise_application_error(-20886,'ORDER_WEIGHT_ORIGINAL_DEMAND_REQUIRED');end if;
  lower_qty:=requested*(1-pct/100);upper_qty:=requested*(1+pct/100);
  result_json.put('customer_order_id',order_id);result_json.put('article',article);result_json.put('warehouse_id',t.WARE_ID);
  result_json.put('case_pick_task_id',p_task);result_json.put('case_pick_line_id',p_line);result_json.put('content_version',t.CONTENT_VERSION);
  result_json.put('policy_version',version);result_json.put('tolerance_pct',RRL_STOCK_PLAN_HELPER.decimal_text(pct));
  result_json.put('unit','KG');result_json.put('requested_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(requested));
  result_json.put('picked_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(actual));
  result_json.put('lower_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(lower_qty));result_json.put('upper_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(upper_qty));
  result_json.put('within_tolerance',actual>0 and actual>=lower_qty and actual<=upper_qty);
  result_json.put('allows_close',false);result_json.put('needs_explicit_decision',true);result_json.put('rows',rows_json);
  return result_json.to_clob;
 end;
end;
/
