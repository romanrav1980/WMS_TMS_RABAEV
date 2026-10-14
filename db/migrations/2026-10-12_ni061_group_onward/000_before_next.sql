create or replace package body RRL_STOCK_INTERWARE_NEXT as   
 function describe_source(p_st number,p_ware number) return json_object_t is   
 bind RRL_INTERWARE_ONWARD_BIND%rowtype;receipt RRL_INTERWARE_RECEIPT%rowtype;placed RRL_INTERWARE_PLACEMENT%rowtype;v_p number;v_h number;v_uom varchar2(20);v_ver number;v_policy number;n number;unit_count number;unit_total number;unit_distinct number;unit_wire clob;unit_snapshot clob;receipt_wire clob;receipt_domain json_object_t;subset_wire json_object_t;j json_object_t:=json_object_t();   
 begin   
 begin select *into bind from RRL_INTERWARE_ONWARD_BIND where ST_ID=p_st;exception when no_data_found then return RRL_STOCK_IW_RECOVERY_NEXT.describe_source(p_st,p_ware);end;   
 select *into receipt from RRL_INTERWARE_RECEIPT where OPERATION_ID=bind.RECEIPT_OPERATION_ID;   
 select *into placed from RRL_INTERWARE_PLACEMENT where RECEIPT_OPERATION_ID=receipt.OPERATION_ID;   
 if p_ware!=receipt.WARE_ID or bind.WARE_ID!=p_ware or bind.ROOT_UID!=receipt.ROOT_UID or placed.TARGET_CELL!=bind.SOURCE_CELL then raise_application_error(-20886,'INTERWARE_ONWARD_ORIGINAL_SOURCE_REQUIRED');end if;   
 select count(*)into n from RRL_INTERWARE_CUSTODY_PROOF where RECEIPT_OPERATION_ID=receipt.OPERATION_ID;if n!=1 then raise_application_error(-20886,'INTERWARE_FIRST_LEG_CUSTODY_REQUIRED');end if;   
 select count(*)into n from RRL_INTERWARE_ONWARD_DISPATCH where BIND_OPERATION_ID=bind.OPERATION_ID;if n!=0 then raise_application_error(-20886,'INTERWARE_ONWARD_ALREADY_DISPATCHED');end if;   
 select REMAIN,HARD_RESERVED_BASE,BASE_UOM,STOCK_VERSION into v_p,v_h,v_uom,v_ver from RRL_REMAINS where UID_POLETA=receipt.ROOT_UID and CELL=bind.SOURCE_CELL;   
 if v_p!=receipt.BASE_QTY or v_h!=0 or v_uom!=receipt.BASE_UOM or v_ver!=bind.STOCK_VERSION then raise_application_error(-20886,'INTERWARE_ONWARD_WHOLE_STOCK_VERSION_REQUIRED');end if;   
 select count(*)into n from RRL_REMAINS where UID_POLETA=receipt.ROOT_UID and CELL!=bind.SOURCE_CELL and(REMAIN!=0 or HARD_RESERVED_BASE!=0);if n!=0 then raise_application_error(-20886,'INTERWARE_ONWARD_ONE_PHYSICAL_CELL_REQUIRED');end if;   
 select count(*)into n from dual where exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=receipt.ARTICLE)or exists(select 1 from RRL_SKU_RECEIPT_POLICY where ARTICUL=receipt.ARTICLE and MARKING_REQUIRED=1)or exists(select 1 from RRL_FINISHED_GOODS_SKU where ARTICUL=receipt.ARTICLE and CRPT_REQUIRED=1);   
 select count(*)into unit_count from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=receipt.ROOT_UID;   
 if n>0 or unit_count>0 then   
  if receipt.ORIGINAL_ROOT_UID is not null then  
   select RESOLVED_PLAN_JSON into receipt_wire from RRL_STOCK_OPERATION where OPERATION_ID=receipt.OPERATION_ID and STATE='APPLIED'and COMMAND_TYPE='INTERWARE_RECEIVE';  
   receipt_domain:=json_object_t.parse(receipt_wire).get_object('domain');subset_wire:=json_object_t();  
   subset_wire.put('units',receipt_domain.get_array('source_units'));subset_wire.put('physical_unit_count',receipt_domain.get_array('source_units').get_size);unit_wire:=subset_wire.to_clob;  
  else  
  select MANIFEST_JSON into unit_wire from RRL_INTERWARE_UNIT_MANIFEST where PLAN_OPERATION_ID=receipt.PLAN_OPERATION_ID;  
  end if;   
  select count(*),sum(u.BASE_QTY),count(distinct u.PHYSICAL_UNIT_KEY),   
   json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION)order by u.PHYSICAL_UNIT_KEY returning clob)   
   into n,unit_total,unit_distinct,unit_snapshot   
   from RRL_WMS_RECEIPT_UNIT u join json_table(unit_wire,'$.units[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom'))j on j.K=u.PHYSICAL_UNIT_KEY   
   where u.CURRENT_UID=receipt.ROOT_UID and u.CURRENT_CELL=bind.SOURCE_CELL and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null and u.BASE_QTY=RRL_STOCK_MATH.quantity(j.Q)and u.BASE_UOM=j.B and u.BASE_UOM=receipt.BASE_UOM;   
  if unit_count<1 or unit_count>10000 or n!=unit_count or unit_distinct!=unit_count or unit_total!=receipt.BASE_QTY or json_object_t.parse(unit_wire).get_number('physical_unit_count')!=unit_count then raise_application_error(-20884,'INTERWARE_ONWARD_ORIGINAL_UNITS_REQUIRED');end if;   
  j.put('physical_units',json_array_t.parse(unit_snapshot));   
 end if;   
 select max(POLICY_VERSION)into v_policy from RRL_STOCK_UOM_CONVERSION where ARTICUL=receipt.ARTICLE and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=DENOMINATOR;   
 if v_policy is null then raise_application_error(-20886,'INTERWARE_ONWARD_BASE_UOM_REQUIRED');end if;   
 select count(*)into n from RRL_SBORKA_PALLETS where ID=p_st and WARE_ID=p_ware and ADDR=bind.FINAL_ADDRESS and RETURN_SUPPLIER_ID is null and nvl(CONDITION,0)<2 and(TRANSTASK_ID is null or TRANSTASK_ID=bind.TARGET_TT_ID);   
 if n!=1 then raise_application_error(-20886,'INTERWARE_ONWARD_ST_SOURCE_CHANGED');end if;   
 j.put('binding_operation_id',bind.OPERATION_ID);j.put('receipt_operation_id',receipt.OPERATION_ID);j.put('source_load_operation_id',bind.SOURCE_LOAD_OPERATION_ID);j.put('source_st_id',bind.SOURCE_ST_ID);j.put('st_id',p_st);j.put('target_trip_id',bind.TARGET_TT_ID);j.put('warehouse_id',p_ware);   
 j.put('uid',receipt.ROOT_UID);j.put('cell',bind.SOURCE_CELL);j.put('article',receipt.ARTICLE);j.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_p));j.put('base_uom',v_uom);j.put('stock_version',v_ver);j.put('uom_version',v_policy);return j;   
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_ONWARD_PLACED_SOURCE_REQUIRED');   
 end;   
 procedure declare_source(p_source json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t) is   
 begin 
 if p_source.has('recovery_operation_id')then RRL_STOCK_IW_RECOVERY_NEXT.declare_source(p_source,p_operation,p_resources);return;end if;   
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_INTERWARE_ONWARD_BIND',p_source.get_string('binding_operation_id'));   
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_INTERWARE_RECEIPT',p_source.get_string('receipt_operation_id'));   
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_INTERWARE_ONWARD_DISPATCH',p_operation);   
 end;   
 procedure validate_load(p_source json_object_t,p_actor varchar2) is   
 op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;v_kind varchar2(80);v_binding varchar2(100):=p_source.get_string('binding_operation_id');v_current json_object_t;trip_id number:=p_source.get_number('target_trip_id');st_id number:=p_source.get_number('st_id');v_warehouse number:=p_source.get_number('warehouse_id');   
 begin 
 if p_source.has('recovery_operation_id')then RRL_STOCK_IW_RECOVERY_NEXT.validate_load(p_source,p_actor);return;end if;   
 select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=op and STATE='IN_FLIGHT';   
 if v_kind='HU_SHIP'then
 select count(*)into n from RRL_STOCK_OPERATION root_op
 where root_op.OPERATION_ID=op and root_op.STATE='IN_FLIGHT'
 and json_value(root_op.RESOLVED_PLAN_JSON,'$.domain.loading.trip'returning number)=trip_id
 and exists(select 1 from json_table(root_op.RESOLVED_PLAN_JSON,'$.domain.shipments[*]'columns(
  BINDING_ID varchar2(100)path '$.domain.interwarehouse_onward_source.binding_operation_id',
  ST_NO number path '$.domain.interwarehouse_onward_source.st_id'))resolved
  where resolved.BINDING_ID=v_binding and resolved.ST_NO=st_id);
 if n!=1 then raise_application_error(-20886,'INTERWARE_NESTED_ACTUAL_TARGET_LOADING_REQUIRED');end if;
 elsif v_kind!='LOAD_SHIPMENT'then raise_application_error(-20886,'INTERWARE_ONWARD_ACTUAL_LOADING_REQUIRED');end if;   
 select count(*)into n from RUSERS u where ID=p_actor and nvl(DELETED,0)=0 and(WARE_ID=v_warehouse or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(u.ID,'stock_posting_shipping')=1;if n!=1 then raise_application_error(-20882,'INTERWARE_ONWARD_CURRENT_WARE_ACTOR_REQUIRED');end if;   
 v_current:=describe_source(st_id,v_warehouse);if v_current is null or dbms_lob.compare(v_current.to_clob,p_source.to_clob)!=0 then raise_application_error(-20886,'INTERWARE_ONWARD_LOAD_SOURCE_CHANGED');end if;   
 select count(*)into n from RRL_SBORKA_PALLETS where ID=st_id and TRANSTASK_ID=trip_id;if n!=1 then raise_application_error(-20886,'INTERWARE_ONWARD_ORIGINAL_TARGET_TRIP_REQUIRED');end if;   
 end;   
 procedure dispatched(p_source json_object_t,p_actor varchar2) is   
 op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_bind varchar2(100):=p_source.get_string('binding_operation_id');v_receipt varchar2(100):=p_source.get_string('receipt_operation_id');v_source varchar2(100):=p_source.get_string('source_load_operation_id');v_st number:=p_source.get_number('st_id');v_uid varchar2(200):=p_source.get_string('uid');v_qty number:=RRL_STOCK_MATH.quantity(p_source.get_string('quantity'));v_uom varchar2(20):=p_source.get_string('base_uom');payload json_object_t:=json_object_t();v_body clob;   
 begin 
 if p_source.has('recovery_operation_id')then RRL_STOCK_IW_RECOVERY_NEXT.dispatched(p_source,p_actor);return;end if;   
 insert into RRL_INTERWARE_ONWARD_DISPATCH(OPERATION_ID,BIND_OPERATION_ID,RECEIPT_OPERATION_ID,SOURCE_LOAD_OPERATION_ID,ST_ID,ROOT_UID,BASE_QTY,BASE_UOM,ACTOR)values(op,v_bind,v_receipt,v_source,v_st,v_uid,v_qty,v_uom,p_actor);   
 payload.put('operation_id',op);payload.put('receipt_operation_id',v_receipt);payload.put('source_load_operation_id',v_source);payload.put('source_st_id',p_source.get_number('source_st_id'));payload.put('st_id',v_st);payload.put('warehouse_id',p_source.get_number('warehouse_id'));payload.put('pallet_identifier',v_uid);payload.put('quantity',p_source.get_string('quantity'));payload.put('base_uom',v_uom);payload.put('customer_fulfillment_repeated',false);payload.put('external_sap_ack',false);v_body:=payload.to_clob;   
 insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values('IW.ONWARD:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(op||':'||RRL_STOCK_PLAN_HELPER.decimal_text(v_st),'AL32UTF8'),sys.dbms_crypto.hash_sh256)),'INTERWARE_ONWARD_DISPATCHED',v_body);   
 end;   
end;
/
