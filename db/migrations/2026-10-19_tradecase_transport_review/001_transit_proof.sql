create or replace package RRL_TRADE_TRANSIT_PROOF authid definer as
 procedure assert_load(p_load varchar2,p_ware number);
end;
/
create or replace package body RRL_TRADE_TRANSIT_PROOF as
 procedure assert_load(p_load varchar2,p_ware number)is
  manifest clob;plan clob;kind varchar2(80);original_op varchar2(100);v_sig varchar2(64);v_epoch number;v_n number;v_total number;v_seen number:=0;v_count number:=0;
  a json_array_t;x json_object_t;j json_object_t;
 begin
  select COMPOSITION_JSON into manifest from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=p_load and WARE_ID=p_ware and STATUS='DEPARTED'and CUSTODY_RELEASED_AT is null;
  if json_value(manifest,'$.warehouse'returning number)<>p_ware then raise_application_error(-20886,'TRADE_TRANSIT_WAREHOUSE_PROOF_REQUIRED');end if;
  select RESOLVED_PLAN_JSON,COMMAND_TYPE into plan,kind from RRL_STOCK_OPERATION where OPERATION_ID=p_load and STATE='APPLIED';
  if kind='RECONCILE_HU_LOAD'then
   original_op:=json_value(plan,'$.domain.original_operation');
   select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=original_op and COMMAND_TYPE='HU_SHIP'and STATE='APPLIED';
  elsif kind not in('LOAD_SHIPMENT','HU_SHIP')then raise_application_error(-20886,'TRADE_TRANSIT_LOAD_PROOF_REQUIRED');end if;
  for leaf in(select UID_VALUE,CELL_VALUE,QUANTITY from json_table(manifest,'$.nodes[*]'columns(UID_VALUE varchar2(200)path'$.uid',CELL_VALUE varchar2(60)path'$.cell',KIND_VALUE varchar2(20)path'$.kind',QUANTITY number path'$.quantity'))where KIND_VALUE='STOCK')loop
   v_seen:=v_seen+1;if v_seen>200 then raise_application_error(-20886,'TRADE_TRANSIT_LEAF_BOUND_200');end if;
   select count(*)into v_n from RRL_CELLS where CELL=leaf.CELL_VALUE and WARE_ID=p_ware;
   if v_n<>1 then raise_application_error(-20886,'TRADE_TRANSIT_ORIGINAL_CELL_REQUIRED');end if;
   select count(*),max(SIG_VALUE),max(VERSION_VALUE)into v_n,v_sig,v_epoch from json_table(plan,'$.physical_before[*]'columns(UID_VALUE varchar2(200)path'$.uid',SIG_VALUE varchar2(64)path'$.unit_signature',VERSION_VALUE number path'$.version'))where UID_VALUE=leaf.UID_VALUE;
   if v_n<>1 or v_sig is null then raise_application_error(-20886,'TRADE_TRANSIT_ORIGINAL_UNIT_PROOF_REQUIRED');end if;
   select count(*)into v_n from RRL_PALLETS where UID_PALLET=leaf.UID_VALUE and STOCK_COMPOSITION_VERSION=v_epoch+1;
   if v_n<>1 then raise_application_error(-20886,'TRADE_TRANSIT_PHYSICAL_EPOCH_CHANGED');end if;
   a:=json_array_t();v_total:=0;
   for u in(select PHYSICAL_UNIT_KEY,BASE_QTY,BASE_UOM,STOCK_STATUS,CURRENT_CELL,HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=leaf.UID_VALUE order by PHYSICAL_UNIT_KEY fetch first 10001 rows only)loop
    v_count:=v_count+1;if a.get_size>=10000 or v_count>20000 then raise_application_error(-20886,'TRADE_TRANSIT_UNIT_BOUND');end if;
    if u.STOCK_STATUS<>'ISSUED'or u.CURRENT_CELL<>leaf.CELL_VALUE or u.HARD_RESERVATION_ID is not null or u.PHYSICAL_UNIT_KEY is null or u.BASE_QTY<=0 or u.BASE_UOM is null then raise_application_error(-20886,'TRADE_TRANSIT_EXACT_ISSUED_SET_REQUIRED');end if;
    x:=json_object_t();x.put('key',u.PHYSICAL_UNIT_KEY);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY));x.put('base_uom',u.BASE_UOM);a.append(x);v_total:=v_total+u.BASE_QTY;
   end loop;
   j:=json_object_t();j.put('units',a);
   if a.get_size=0 or v_total<>leaf.QUANTITY or rawtohex(sys.dbms_crypto.hash(j.to_clob,sys.dbms_crypto.hash_sh256))<>v_sig then raise_application_error(-20886,'TRADE_TRANSIT_ORIGINAL_UNIT_FINGERPRINT_CONFLICT');end if;
  end loop;
  if v_seen=0 then raise_application_error(-20886,'TRADE_TRANSIT_STOCK_LEAF_REQUIRED');end if;
 exception when no_data_found then raise_application_error(-20886,'TRADE_TRANSIT_ORIGINAL_LOAD_REQUIRED');
 end;
end;
/
