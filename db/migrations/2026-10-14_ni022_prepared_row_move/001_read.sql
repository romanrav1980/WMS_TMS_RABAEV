create or replace package RRL_ST_LAYOUT_READ as
 function scope_order(p_order number,p_actor varchar2,p_permission varchar2 default 'customer_order_view')return number;
 function snapshot(p_order number,p_row number,p_target number,p_actor varchar2)return clob;
end;
/
create or replace package body RRL_ST_LAYOUT_READ as
 function scope_order(p_order number,p_actor varchar2,p_permission varchar2 default 'customer_order_view')return number is w number;n number;
 begin
  if p_permission not in('customer_order_view','outgoing_pallet_edit')or p_permission is null then raise_application_error(-20882,'ST_LAYOUT_PERMISSION_REQUIRED');end if;
  select WARE_ID into w from RRL_CUSTOMER_ORDER where CUSTOMER_ORDER_ID=p_order;
  select count(*)into n from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,p_permission)=1
   and(u.WARE_ID=w or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'ST_LAYOUT_CURRENT_WAREHOUSE_REQUIRED');end if;
  return w;
 exception when no_data_found then raise_application_error(-20887,'ST_LAYOUT_ORDER_NOT_FOUND');
 end;
 function snapshot(p_order number,p_row number,p_target number,p_actor varchar2)return clob is
  w number;n number;source_count number:=0;target_count number:=0;merge_id number;
  source_row RRL_SBORKA_PALLET_ROWS%rowtype;dest_row RRL_SBORKA_PALLET_ROWS%rowtype;
  src RRL_SBORKA_PALLETS%rowtype;dst RRL_SBORKA_PALLETS%rowtype;
  j json_object_t:=json_object_t();x json_object_t;before_rows json_array_t:=json_array_t();after_rows json_array_t:=json_array_t();
  members json_array_t:=json_array_t();trip RRL_TRANSPORT_TASK%rowtype;
  function row_json(r RRL_SBORKA_PALLET_ROWS%rowtype)return json_object_t is v json_object_t:=json_object_t();
  begin
   v.put('id',r.ID);v.put('pallet',r.PALLET_UID);v.put('article',r.ARTICUL);v.put('unit',r.EI);
   v.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(r.QUANTITY));
   v.put('weight',RRL_STOCK_PLAN_HELPER.decimal_text(r.ORDER_WEIGHT));
   v.put('packs',RRL_STOCK_PLAN_HELPER.decimal_text(r.PACK_COUNT));
   v.put('tare_weight',r.TAREWEIGHT);v.put('tare_size',r.TARESIZE);
   v.put('original_quantity',r.ORIGINAL_QUANTITY);v.put('original_weight',r.ORIGINAL_ORDER_WEIGHT);
   v.put('warehouse',r.WARE_ID);v.put('batch',r.PROD_BATCH_ID);v.put('sscc',r.SSCC);
   v.put('expiry',to_char(r.EXPIRY_DATE,'YYYY-MM-DD HH24:MI:SS'));v.put('trace_mode',r.CRPT_TRANSFER_MODE);
   return v;
  end;
 begin
  w:=scope_order(p_order,p_actor);
  select *into source_row from RRL_SBORKA_PALLET_ROWS where ID=p_row;
  select *into src from RRL_SBORKA_PALLETS where PALLET_UID=source_row.PALLET_UID;
  select *into dst from RRL_SBORKA_PALLETS where ID=p_target;
  if src.ID=dst.ID or src.WARE_ID!=w or dst.WARE_ID!=w or src.WARE_ID is null or dst.WARE_ID is null
   or src.ST_NUMBER is null or src.ST_NUMBER!=dst.ST_NUMBER or nvl(src.ADDR,chr(0))!=nvl(dst.ADDR,chr(0))
   or nvl(src.TRANSTASK_ID,0)!=nvl(dst.TRANSTASK_ID,0) then raise_application_error(-20886,'ST_LAYOUT_SAME_ORDER_TRIP_REQUIRED');end if;
  if nvl(src.CONDITION,0)>=2 or nvl(dst.CONDITION,0)>=2 or src.RETURN_SUPPLIER_ID is not null or dst.RETURN_SUPPLIER_ID is not null then
   raise_application_error(-20886,'ST_LAYOUT_UNSHIPPED_CUSTOMER_ST_REQUIRED');end if;
  for f in(select *from RRL_CUSTOMER_ORDER_FULFILLMENT where LEGACY_SBORKA_PALLET_ID in(src.ID,dst.ID)order by FULFILLMENT_ID)loop
   if f.CUSTOMER_ORDER_ID!=p_order or f.STATUS!='PLANNED'or f.STATUS is null or nvl(f.FACT_QTY,0)!=0
    or f.PICKED_CASE_TASK_ID is not null or f.PICKED_PALLET_UID is not null or f.PICKED_WAREHOUSE_TASK_ID is not null
    or f.PICKED_OPERATION_ID is not null or f.SHIPPED_OPERATION_ID is not null then raise_application_error(-20886,'ST_LAYOUT_UNBOUND_PLANNED_ONLY');end if;
   x:=json_object_t();x.put('id',f.FULFILLMENT_ID);x.put('shipment_id',f.LEGACY_SBORKA_PALLET_ID);x.put('pallet',f.PALLET_UID);members.append(x);
  end loop;
  if members.get_size!=2 then raise_application_error(-20886,'ST_LAYOUT_EXACT_FULFILLMENT_REQUIRED');end if;
  if nvl(src.TRANSTASK_ID,0)>0 then
   select *into trip from RRL_TRANSPORT_TASK where ID=src.TRANSTASK_ID;
   if nvl(trip.DELETED,0)!=0 or nvl(trip.PAY_ORDER_ID,0)!=0 or trip.CONDITION='Отгружен' then raise_application_error(-20886,'ST_LAYOUT_TRIP_CLOSED');end if;
   select count(*)into n from RRL_TT_HU_LOAD_FACT where TT_ID=src.TRANSTASK_ID and STATUS='DEPARTED';
   if n>0 then raise_application_error(-20886,'ST_LAYOUT_TRIP_DEPARTED');end if;
   j.put('trip_state',trip.CONDITION);j.put('trip_vehicle',trip.TRANSPORT);
  end if;
  select count(*)into n from RRL_TT_HU_LOAD_ST where SBORKA_PALLET_ID in(src.ID,dst.ID)and ACTIVE_FLAG=1;
  if n>0 then raise_application_error(-20886,'ST_LAYOUT_LOADED_PLACE');end if;
  select count(*),max(ID)into n,merge_id from RRL_SBORKA_PALLET_ROWS where PALLET_UID=dst.PALLET_UID and ARTICUL=source_row.ARTICUL;
  if n>1 then raise_application_error(-20887,'ST_LAYOUT_AMBIGUOUS_TARGET_ARTICLE');end if;
  if merge_id is not null then
   select *into dest_row from RRL_SBORKA_PALLET_ROWS where ID=merge_id;
   if nvl(dest_row.EI,chr(0))!=nvl(source_row.EI,chr(0))or nvl(dest_row.TAREWEIGHT,-1)!=nvl(source_row.TAREWEIGHT,-1)
    or nvl(dest_row.TARESIZE,-1)!=nvl(source_row.TARESIZE,-1)or nvl(dest_row.PROD_BATCH_ID,-1)!=nvl(source_row.PROD_BATCH_ID,-1)
    or nvl(dest_row.SSCC,chr(0))!=nvl(source_row.SSCC,chr(0))or nvl(dest_row.CRPT_TRANSFER_MODE,chr(0))!=nvl(source_row.CRPT_TRANSFER_MODE,chr(0))
    or nvl(dest_row.EXPIRY_DATE,date '1900-01-01')!=nvl(source_row.EXPIRY_DATE,date '1900-01-01')then
    raise_application_error(-20886,'ST_LAYOUT_ROW_METADATA_MISMATCH');end if;
  end if;
  for r in(select *from RRL_SBORKA_PALLET_ROWS where PALLET_UID in(src.PALLET_UID,dst.PALLET_UID)order by ID fetch first 201 rows only)loop
   if before_rows.get_size>=200 then raise_application_error(-20881,'ST_LAYOUT_ROW_BOUND_200');end if;
   if r.QUANTITY is null or r.QUANTITY<=0 or r.EI is null or r.ORDER_WEIGHT is null or r.ORDER_WEIGHT<=0
    or r.PACK_COUNT is null or r.PACK_COUNT<=0 or r.PACK_COUNT!=trunc(r.PACK_COUNT)or r.WARE_ID is null or r.WARE_ID!=w
    or nvl(r.SOBRANO,0)!=0 or r.PRIHOD_PALLET_UID is not null or r.TIME_OF_CHECKING is not null then
    raise_application_error(-20886,'ST_LAYOUT_UNEXECUTED_EXACT_ROWS_REQUIRED');end if;
   if r.PALLET_UID=src.PALLET_UID then source_count:=source_count+1;else target_count:=target_count+1;end if;
   x:=row_json(r);before_rows.append(x);
   if r.ID=p_row then
    if merge_id is null then x.put('pallet',dst.PALLET_UID);after_rows.append(x);end if;
   else
    if r.ID=merge_id then
     x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(r.QUANTITY+source_row.QUANTITY));
     x.put('weight',RRL_STOCK_PLAN_HELPER.decimal_text(r.ORDER_WEIGHT+source_row.ORDER_WEIGHT));
     x.put('packs',RRL_STOCK_PLAN_HELPER.decimal_text(r.PACK_COUNT+source_row.PACK_COUNT));
     x.put('original_quantity',nvl(r.ORIGINAL_QUANTITY,0)+nvl(source_row.ORIGINAL_QUANTITY,0));
     x.put('original_weight',nvl(r.ORIGINAL_ORDER_WEIGHT,0)+nvl(source_row.ORIGINAL_ORDER_WEIGHT,0));
    end if;
    after_rows.append(x);
   end if;
  end loop;
  if source_count<2 or target_count<1 then raise_application_error(-20886,'ST_LAYOUT_KEEP_EXISTING_NONEMPTY_PLACES');end if;
  j.put('order_id',p_order);j.put('warehouse',w);j.put('row_id',p_row);j.put('target_shipment_id',dst.ID);
  j.put('source_shipment_id',src.ID);j.put('source_pallet',src.PALLET_UID);j.put('target_pallet',dst.PALLET_UID);
  j.put('st_number',src.ST_NUMBER);j.put('trip_id',src.TRANSTASK_ID);j.put('merge_row_id',merge_id);
  j.put('fulfillments',members);j.put('before',before_rows);j.put('after',after_rows);j.put('stock_changed',false);
  j.put('signature',rawtohex(sys.dbms_crypto.hash(j.to_clob,sys.dbms_crypto.hash_sh256)));
  return j.to_clob;
 exception when no_data_found then raise_application_error(-20887,'ST_LAYOUT_IDENTITY_MISSING');
  when too_many_rows then raise_application_error(-20887,'ST_LAYOUT_IDENTITY_AMBIGUOUS');
 end;
end;
/
