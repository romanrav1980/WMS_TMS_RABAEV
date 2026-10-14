create or replace package RRL_STOCK_SUP_RETURN authid definer accessible by(package RRL_STOCK_SHIPPING_CORE,package RRL_STOCK_EFFECT_CORE) as
 function describe_source(p_st number,p_supplier varchar2,p_ware number) return json_object_t;
 procedure declare_source(p_source json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure validate_consume(p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_quantity number,p_ware number,p_actor varchar2);
 procedure dispatched(p_source json_object_t,p_actor varchar2);
end;
/
create or replace package body RRL_STOCK_SUP_RETURN as
 function describe_source(p_st number,p_supplier varchar2,p_ware number) return json_object_t is
 binding RRL_STORE_RETURN_SUP_BIND%rowtype;receipt RRL_STORE_RETURN_RECEIPT%rowtype;placed RRL_STORE_RETURN_PLACEMENT%rowtype;j json_object_t:=json_object_t();
 v_cell varchar2(60);v_qty number;v_h number;v_version number;v_uom varchar2(20);v_policy number;n number;
 begin
 begin select * into binding from RRL_STORE_RETURN_SUP_BIND where ST_ID=p_st;exception when no_data_found then return null;end;
 select * into receipt from RRL_STORE_RETURN_RECEIPT where OPERATION_ID=binding.RECEIPT_OPERATION_ID;
 select * into placed from RRL_STORE_RETURN_PLACEMENT where RECEIPT_OPERATION_ID=receipt.OPERATION_ID;
 if receipt.DISPOSITION!='SUPPLIER' or receipt.WARE_ID!=p_ware or binding.SUPPLIER_INN!=p_supplier then raise_application_error(-20886,'SUP_RETURN_TYPED_SOURCE_CONFLICT');end if;
 select count(*)into n from RRL_SUPPLIERS where INN=p_supplier;if n!=1 then raise_application_error(-20886,'SUP_RETURN_UNIQUE_SUPPLIER_REQUIRED');end if;
 select count(*)into n from RRL_STORE_RETURN_SUP_DISPATCH where BIND_OPERATION_ID=binding.OPERATION_ID;if n!=0 then raise_application_error(-20886,'SUP_RETURN_ALREADY_DISPATCHED');end if;
 select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM,CELL into v_qty,v_h,v_version,v_uom,v_cell from RRL_REMAINS where UID_POLETA=receipt.UID_PALLET and REMAIN>0;
 if v_qty!=receipt.BASE_QTY or v_h!=0 or v_uom!=receipt.BASE_UOM or v_cell!=placed.TARGET_CELL then raise_application_error(-20886,'SUP_RETURN_WHOLE_PLACED_UNRESERVED_SOURCE_REQUIRED');end if;
 select count(*)into n from RRL_CELLS where CELL=v_cell and WARE_ID=p_ware and BLOCKED_FOR_REMAINS=1 and BLOCKED_FOR_POPOLNENIE=1;
 if n!=1 then raise_application_error(-20886,'SUP_RETURN_SEGREGATED_SOURCE_REQUIRED');end if;
 select count(*)into n from RRL_WMS_HU_LINK where ACTIVE_FLAG=1 and(CHILD_PALLET_UID=receipt.UID_PALLET or PARENT_UID=receipt.UID_PALLET);if n!=0 then raise_application_error(-20886,'SUP_RETURN_SINGLE_PHYSICAL_PLACE_REQUIRED');end if;
 select count(*)into n from dual where exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=receipt.ARTICLE)or exists(select 1 from RRL_SKU_RECEIPT_POLICY where ARTICUL=receipt.ARTICLE and MARKING_REQUIRED=1)or exists(select 1 from RRL_FINISHED_GOODS_SKU where ARTICUL=receipt.ARTICLE and CRPT_REQUIRED=1);
 if n!=0 then raise_application_error(-20886,'SUP_RETURN_MARKED_UNIT_REGULATORY_FLOW_REQUIRED');end if;
 select max(POLICY_VERSION)into v_policy from RRL_STOCK_UOM_CONVERSION where ARTICUL=receipt.ARTICLE and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=1 and DENOMINATOR=1;
 if v_policy is null then raise_application_error(-20886,'SUP_RETURN_BASE_UOM_POLICY_REQUIRED');end if;
 j.put('binding_operation_id',binding.OPERATION_ID);j.put('receipt_operation_id',receipt.OPERATION_ID);j.put('st_id',p_st);j.put('supplier_inn',p_supplier);j.put('warehouse_id',p_ware);j.put('uid',receipt.UID_PALLET);j.put('cell',v_cell);j.put('article',receipt.ARTICLE);
 j.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));j.put('base_uom',v_uom);j.put('stock_version',v_version);j.put('uom_version',v_policy);j.put('placement_task_id',placed.TASK_ID);j.put('return_document',receipt.SAP_OPERATION_ID);
 return j;
 exception when no_data_found then raise_application_error(-20886,'SUP_RETURN_PLACED_SOURCE_REQUIRED');when too_many_rows then raise_application_error(-20886,'SUP_RETURN_ONE_SOURCE_LOCATION_REQUIRED');end;
 procedure declare_source(p_source json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t) is
 begin
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_RETURN_SUP_BIND',p_source.get_string('binding_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_RETURN_RECEIPT',p_source.get_string('receipt_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_RETURN_SUP_DISPATCH',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(p_resources,70,'UNIQUE','SAP.OUTBOX:SUPPLIER_DISPATCH:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 end;
 procedure validate_consume(p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_quantity number,p_ware number,p_actor varchar2) is
 v_st number;v_supplier varchar2(255);v json_object_t;op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_kind varchar2(80);n number;
 begin
 if RRL_HAS_WRIGHT(p_actor,'warehouse_return_dispatch')!=1 then raise_application_error(-20882,'SUP_RETURN_DISPATCH_PERMISSION_REQUIRED');end if;
 select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and(WARE_ID=p_ware or upper(trim(USER_GROUP))='GLOBAL_ADMIN');if n!=1 then raise_application_error(-20882,'SUP_RETURN_CURRENT_WAREHOUSE_BINDING_REQUIRED');end if;
 select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=op and STATE='IN_FLIGHT';
 if v_kind!='LOAD_SHIPMENT' then raise_application_error(-20886,'SUP_RETURN_ACTUAL_PHYSICAL_LOADING_REQUIRED');end if;
 select ST_ID,SUPPLIER_INN into v_st,v_supplier from RRL_STORE_RETURN_SUP_BIND where RECEIPT_OPERATION_ID=p_receipt;
 v:=describe_source(v_st,v_supplier,p_ware);
 if v.get_string('uid')!=p_uid or v.get_string('cell')!=p_cell or RRL_STOCK_MATH.quantity(v.get_string('quantity'))!=p_quantity then raise_application_error(-20886,'SUP_RETURN_EXACT_ORIGINAL_PALLET_QUANTITY_REQUIRED');end if;
 end;
 procedure dispatched(p_source json_object_t,p_actor varchar2) is
 op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');v_bind varchar2(100);v_receipt varchar2(100);v_st number;v_uid varchar2(200);v_quantity number;v_unit varchar2(20);v_supplier varchar2(255);payload json_object_t:=json_object_t();v_body clob;v_event varchar2(100);
 begin
 v_bind:=p_source.get_string('binding_operation_id');v_receipt:=p_source.get_string('receipt_operation_id');v_st:=p_source.get_number('st_id');v_uid:=p_source.get_string('uid');v_quantity:=RRL_STOCK_MATH.quantity(p_source.get_string('quantity'));v_unit:=p_source.get_string('base_uom');v_supplier:=p_source.get_string('supplier_inn');
 insert into RRL_STORE_RETURN_SUP_DISPATCH(OPERATION_ID,BIND_OPERATION_ID,RECEIPT_OPERATION_ID,ST_ID,UID_PALLET,BASE_QTY,BASE_UOM,SUPPLIER_INN,ACTOR)values(op,v_bind,v_receipt,v_st,v_uid,v_quantity,v_unit,v_supplier,p_actor);
 payload.put('operation_id',op);payload.put('receipt_operation_id',v_receipt);payload.put('supplier_inn',v_supplier);payload.put('pallet_identifier',v_uid);payload.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_quantity));payload.put('base_uom',v_unit);payload.put('warehouse_exit_confirmed',true);payload.put('supplier_received',false);payload.put('external_sap_ack',false);
 v_body:=payload.to_clob;v_event:='SUPPLIER_DISPATCH:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(op,'AL32UTF8'),sys.dbms_crypto.hash_sh256));
 insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values(v_event,'SUPPLIER_RETURN_DISPATCHED',v_body);
 end;
end;
/
