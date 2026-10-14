create or replace package body RRL_STOCK_STORE_RETURN_REC_CMD as

 procedure assert_scope(p_pickup varchar2,p_actor varchar2)is n number;

 begin

  select count(*)into n from RRL_STORE_RETURN_PICKUP p join RRL_STORE_RETURN_HANDOVER h on h.OPERATION_ID=p.HANDOVER_OPERATION_ID join RRL_STORE_RETURN_TRANSPORT t on t.OPERATION_ID=h.TRANSPORT_OPERATION_ID join RUSERS u on u.ID=p_actor

   where p.OPERATION_ID=p_pickup and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(p_actor,'warehouse_return_receive')=1 and(u.WARE_ID=t.RECEIVING_WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');

  if n!=1 then raise_application_error(-20882,'STORE_RETURN_CURRENT_RECEIVING_WAREHOUSE_ACTOR_REQUIRED');end if;

 end;

 function actual_date(p_text varchar2) return date is

 begin

  if p_text is null or not regexp_like(p_text,'^[0-9]{4}-[0-9]{2}-[0-9]{2}$','c') then raise_application_error(-20886,'STORE_RETURN_ACTUAL_DATE_REQUIRED');end if;

  begin return to_date(p_text,'FXYYYY-MM-DD');exception when others then raise_application_error(-20886,'STORE_RETURN_ACTUAL_DATE_INVALID');end;

 end;

 procedure describe_receipt(p_request clob,p_actor varchar2,p_domain out json_object_t) is

 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v_pickup varchar2(100):=d.get_object('source').get_string('pickup_operation_id');

 pickup RRL_STORE_RETURN_PICKUP%rowtype;handed RRL_STORE_RETURN_HANDOVER%rowtype;transport RRL_STORE_RETURN_TRANSPORT%rowtype;approved RRL_STORE_RETURN_APPROVAL%rowtype;sap RRL_STORE_RETURN_SAP%rowtype;

 original RRL_PALLETS%rowtype;policy RRL_STORE_RETURN_WARE_POLICY%rowtype;

 v_cell varchar2(60);v_uid varchar2(200);v_gross number;v_net number;v_expiry date;v_batch varchar2(32767);v_original_batch varchar2(100);v_origin varchar2(200);v_batch_source varchar2(30);v_uom_version number;v_scale number;n number;v_scan_article varchar2(160);v_scan_uom varchar2(20);v_scan_code varchar2(128);v_proof json_object_t;return_proof clob;source_cell varchar2(60);source_max varchar2(60);

 begin

 if RRL_HAS_WRIGHT(p_actor,'warehouse_return_receive')!=1 then raise_application_error(-20882,'STORE_RETURN_WAREHOUSE_RECEIVE_FORBIDDEN');end if;

 select * into pickup from RRL_STORE_RETURN_PICKUP where OPERATION_ID=v_pickup;

 select * into handed from RRL_STORE_RETURN_HANDOVER where OPERATION_ID=pickup.HANDOVER_OPERATION_ID;

 select * into transport from RRL_STORE_RETURN_TRANSPORT where OPERATION_ID=handed.TRANSPORT_OPERATION_ID;

 select * into approved from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=transport.APPROVAL_OPERATION_ID;

 select * into sap from RRL_STORE_RETURN_SAP where OPERATION_ID=transport.SAP_OPERATION_ID;



 select count(*) into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and(upper(trim(USER_GROUP))='GLOBAL_ADMIN' or WARE_ID=sap.WARE_ID);

 if n!=1 then raise_application_error(-20882,'STORE_RETURN_RECEIVER_WAREHOUSE_BINDING_REQUIRED');end if;

 select * into policy from RRL_STORE_RETURN_WARE_POLICY where WARE_ID=sap.WARE_ID;

 v_cell:=case approved.DISPOSITION when 'SUPPLIER' then policy.SUPPLIER_RECEIVE_CELL when 'REUSE' then policy.REUSE_RECEIVE_CELL else policy.DISPOSAL_RECEIVE_CELL end;

 select count(*) into n from RRL_CELLS where CELL=v_cell and WARE_ID=sap.WARE_ID and nvl(BLOCKED_FOR_ACCEPT,0)=0 and BLOCKED_FOR_REMAINS=1 and BLOCKED_FOR_POPOLNENIE=1;

 if n!=1 then raise_application_error(-20886,'STORE_RETURN_SEGREGATED_RECEIVING_CELL_REQUIRED');end if;

 v_uid:=handed.PALLET_IDENTIFIER;

 if length(v_uid)>50 or lengthb(v_uid)>150 then raise_application_error(-20886,'STORE_RETURN_PALLET_LEGACY_ID_BOUND_50');end if;

 if m.get_string('scan_pallet') is null or m.get_string('scan_pallet')!=v_uid or m.get_string('scan_vehicle') is null or m.get_string('scan_vehicle')!=pickup.VEHICLE_NUMBER or m.get_string('scan_cell') is null or m.get_string('scan_cell')!=v_cell then raise_application_error(-20886,'STORE_RETURN_WAREHOUSE_PALLET_VEHICLE_CELL_SCAN_REQUIRED');end if;

 if m.get_string('article') is null or m.get_string('article')!=approved.ARTICLE or m.get_string('base_uom') is null or m.get_string('base_uom')!=approved.BASE_UOM or RRL_STOCK_MATH.quantity(m.get_string('quantity'))!=approved.BASE_QTY then raise_application_error(-20886,'STORE_RETURN_WAREHOUSE_FULL_ORIGINAL_QUANTITY_REQUIRED');end if;

 v_scan_code:=m.get_string('scan_article');RRL_STOCK_QC_ITEM.resolve_barcode(v_scan_code,v_scan_article,v_scan_uom);

 if v_scan_article!=approved.ARTICLE then raise_application_error(-20886,'STORE_RETURN_FOREIGN_ARTICLE_BARCODE');end if;

 select count(*) into n from RRL_PALLETS where UID_PALLET=v_uid;

 if n!=0 then raise_application_error(-20886,'STORE_RETURN_FRESH_PALLET_REQUIRED');end if;

 select count(*) into n from RRL_STORE_RETURN_RECEIPT where PICKUP_OPERATION_ID=v_pickup or APPROVAL_OPERATION_ID=approved.OPERATION_ID;

 if n!=0 then raise_application_error(-20886,'STORE_RETURN_PICKUP_ALREADY_RECEIVED');end if;

 select * into original from RRL_PALLETS where UID_PALLET=approved.LOT_UID;

 if original.ARTICUL is null or original.ARTICUL!=approved.ARTICLE or original.EXPIRY_DATE is null then raise_application_error(-20886,'STORE_RETURN_ORIGINAL_LOT_METADATA_REQUIRED');end if;

 v_expiry:=actual_date(m.get_string('expiry_date'));

 if v_expiry is null or v_expiry!=trunc(original.EXPIRY_DATE) then raise_application_error(-20886,'STORE_RETURN_ORIGINAL_EXPIRY_CONFLICT');end if;

 v_batch:=m.get_string('supplier_batch');

 if trim(v_batch) is null or lengthb(v_batch)>100 then raise_application_error(-20886,'STORE_RETURN_ACTUAL_BATCH_REQUIRED');end if;

 v_origin:=nvl(original.STOCK_ORIGIN_UID,original.UID_PALLET);

 select count(*),min(SUPPLIER_BATCH) into n,v_original_batch from RRL_SAP_PALLET_RECEIPT where UID_PALLET=v_origin;

 if n>1 then raise_application_error(-20886,'STORE_RETURN_ORIGINAL_BATCH_AMBIGUOUS');end if;

 if n=1 and v_original_batch is not null then

  if v_batch!=v_original_batch then raise_application_error(-20886,'STORE_RETURN_ORIGINAL_BATCH_CONFLICT');end if;v_batch_source:='ORIGINAL_SAP_VERIFIED';

 else v_batch_source:='OBSERVED_LEGACY_UNVERIFIED';end if;

 select count(*) into n from dual where exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=approved.ARTICLE)

 or exists(select 1 from RRL_SKU_RECEIPT_POLICY where ARTICUL=approved.ARTICLE and MARKING_REQUIRED=1)

 or exists(select 1 from RRL_FINISHED_GOODS_SKU where ARTICUL=approved.ARTICLE and CRPT_REQUIRED=1);

 return_proof:=RRL_STORE_RETURN_UNIT_CORE.custody_proof(approved.OPERATION_ID,m);

 if n!=0 and return_proof is null then raise_application_error(-20886,'STORE_RETURN_MARKED_EXACT_APPROVAL_REQUIRED');end if;

 if return_proof is not null then

  select min(SOURCE_CELL),max(SOURCE_CELL)into source_cell,source_max from RRL_STORE_RETURN_UNIT where APPROVAL_OPERATION_ID=approved.OPERATION_ID;

  if source_cell is null or source_cell!=source_max then raise_application_error(-20886,'STORE_RETURN_UNIT_SOURCE_CELL_REQUIRED');end if;

 end if;

 select max(POLICY_VERSION) into v_uom_version from RRL_STOCK_UOM_CONVERSION where ARTICUL=approved.ARTICLE and INPUT_UOM=approved.BASE_UOM and BASE_UOM=approved.BASE_UOM and NUMERATOR=1 and DENOMINATOR=1;

 select BASE_SCALE into v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=approved.ARTICLE and INPUT_UOM=approved.BASE_UOM and BASE_UOM=approved.BASE_UOM and POLICY_VERSION=v_uom_version and NUMERATOR=1 and DENOMINATOR=1;

 RRL_STOCK_MATH.assert_base(approved.BASE_QTY,v_scale);

 v_gross:=RRL_STOCK_MATH.quantity(m.get_string('gross_weight_kg'));v_net:=RRL_STOCK_MATH.quantity(m.get_string('net_weight_kg'));

 if v_gross!=handed.GROSS_WEIGHT_KG or v_net>v_gross then raise_application_error(-20886,'STORE_RETURN_WAREHOUSE_WEIGHT_CONFLICT');end if;

 if approved.DISPOSITION='REUSE' then RRL_STOCK_RETURN_REUSE.describe_boxes(approved,m,v_scan_uom,v_batch_source,sap.WARE_ID,v_proof);end if;

 p_domain:=json_object_t();if approved.RETURN_BASIS!='ACCEPTED'then p_domain.put('return_basis',approved.RETURN_BASIS);end if;if return_proof is not null then p_domain.put('return_unit_proof',json_object_t.parse(return_proof));p_domain.put('return_source_cell',source_cell);end if;if v_proof is not null then p_domain.put('reuse_boxes',v_proof);end if;p_domain.put('pickup_operation_id',v_pickup);p_domain.put('approval_operation_id',approved.OPERATION_ID);p_domain.put('sap_operation_id',sap.OPERATION_ID);p_domain.put('return_document',sap.RETURN_DOCUMENT);

 p_domain.put('warehouse_id',sap.WARE_ID);p_domain.put('receive_cell',v_cell);p_domain.put('policy_version',policy.POLICY_VERSION);p_domain.put('uid',v_uid);p_domain.put('original_lot_uid',approved.LOT_UID);p_domain.put('stock_origin_uid',v_origin);

 p_domain.put('article',approved.ARTICLE);p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(approved.BASE_QTY));p_domain.put('base_uom',approved.BASE_UOM);p_domain.put('uom_version',v_uom_version);p_domain.put('disposition',approved.DISPOSITION);

 p_domain.put('expiry_date',to_char(v_expiry,'YYYY-MM-DD'));p_domain.put('produced_date',to_char(original.PRODUCED_DATE,'YYYY-MM-DD'));p_domain.put('price',original.PRICE);

 p_domain.put('scan_article',v_scan_code);p_domain.put('scan_input_uom',v_scan_uom);p_domain.put('supplier_batch',v_batch);p_domain.put('batch_source',v_batch_source);p_domain.put('gross_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v_gross));p_domain.put('net_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(v_net));

 exception when no_data_found then raise_application_error(-20886,'STORE_RETURN_PICKUP_LOT_OR_WAREHOUSE_POLICY_REQUIRED');

 end;

 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is

 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();v_naklad number;

 begin

 describe_receipt(p_request,d.get_string('actor'),v);

 select RRL_PRIHOD_NAKLAD_SQ.nextval into v_naklad from dual;v.put('naklad_id',v_naklad);

 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);

 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));

 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PRIHOD_NAKLAD',RRL_STOCK_PLAN_HELPER.decimal_text(v_naklad));

 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_PICKUP',v.get_string('pickup_operation_id'));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_RECEIPT',p_operation);

 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',v.get_string('original_lot_uid'));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',v.get_string('uid'));

 RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('uid'),v.get_string('article'),null,v.get_string('receive_cell'));

 if v.has('return_unit_proof')then

  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('original_lot_uid'),v.get_string('article'),v.get_string('return_source_cell'),null);

  declare wire clob:=v.get_object('return_unit_proof').get_array('units').to_clob;begin

   for x in(select K from json_table(wire,'$[*]'columns(K varchar2(64)path '$.key')))loop RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',x.K);end loop;

  end;

  RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_APPROVAL',v.get_string('approval_operation_id'));

 end if;

 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','PALLET:'||v.get_string('uid'));

 if v.has('reuse_boxes')then RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RETURN_REUSE_PROOF',p_operation);end if;

 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;

 end;

 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is

 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');plan clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();

 v_naklad number;v_document varchar2(100);v_number varchar2(20);v_pickup varchar2(100);v_approval varchar2(100);v_sap varchar2(100);v_uid varchar2(200);v_old_uid varchar2(200);v_origin varchar2(200);v_article varchar2(160);v_ware number;v_cell varchar2(60);v_base varchar2(20);v_qty number;v_version number;v_event number;v_gross number;v_net number;v_price number;v_expiry date;v_produced date;v_batch varchar2(100);v_batch_source varchar2(30);v_disposition varchar2(20);

 begin

 select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');

 describe_receipt(p_request,p_actor,fresh);fresh.put('naklad_id',v.get_number('naklad_id'));

 if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20886,'STORE_RETURN_RECEIVING_SOURCE_CHANGED');end if;

 v_pickup:=v.get_string('pickup_operation_id');v_approval:=v.get_string('approval_operation_id');v_sap:=v.get_string('sap_operation_id');v_uid:=v.get_string('uid');v_old_uid:=v.get_string('original_lot_uid');v_origin:=v.get_string('stock_origin_uid');v_article:=v.get_string('article');

 v_ware:=v.get_number('warehouse_id');v_cell:=v.get_string('receive_cell');v_base:=v.get_string('base_uom');v_qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));v_version:=v.get_number('uom_version');

 v_gross:=RRL_STOCK_MATH.quantity(v.get_string('gross_weight_kg'));v_net:=RRL_STOCK_MATH.quantity(v.get_string('net_weight_kg'));v_price:=v.get_number('price');v_expiry:=to_date(v.get_string('expiry_date'),'FXYYYY-MM-DD');v_produced:=to_date(v.get_string('produced_date'),'FXYYYY-MM-DD');v_batch:=v.get_string('supplier_batch');v_batch_source:=v.get_string('batch_source');v_disposition:=v.get_string('disposition');

 RRL_STOCK_LOCATION_CORE.assert_receiving(v_cell,v_ware);

 v_naklad:=v.get_number('naklad_id');v_document:=v.get_string('return_document');v_number:='RTN:'||RRL_STOCK_PLAN_HELPER.decimal_text(v_naklad);

 insert into RRL_PRIHOD_NAKLAD(ID,NAKLAD_NUMBER,ZAKAZ_NUMBER,DATE_OF_NAKLAD,DATE_OF_ACCEPT,WARE_ID,POSTAVSHIK_NAME,CONDITION,DOCUMENT_KIND,RETURN_APPROVAL_OPERATION_ID,RETURN_DOCUMENT_REFERENCE)

 values(v_naklad,v_number,v_number,sysdate,sysdate,v_ware,unistr('\0412\043E\0437\0432\0440\0430\0442 \043C\0430\0433\0430\0437\0438\043D\0430'),1,'STORE_RETURN',v_approval,v_document);

 insert into RRL_PALLETS(UID_PALLET,ARTICUL,CREATION_DATE,EXPIRY_DATE,PRODUCED_DATE,UNIT_COUNT,PRICE,STOCK_ORIGIN_UID,CREATED_BY_STOCK_OP,WEIGHT_BRUTTO,PRIHOD_NAKLAD_ID)

 values(v_uid,v_article,systimestamp,v_expiry,v_produced,v_qty,v_price,v_origin,op,v_gross,v_naklad);

 RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_cell,v_qty,0,v_base,v_version,0);

 if v.has('return_unit_proof')then

  RRL_STOCK_UNIT_CORE.receive_return(v_old_uid,v.get_string('return_source_cell'),v_uid,v_cell,v_qty,v.get_object('return_unit_proof').get_array('units').to_clob);

  j.put('physical_unit_count',v.get_object('return_unit_proof').get_number('physical_unit_count'));j.put('mark_scan_confirmed',true);j.put('original_unit_codes_retained',true);

 end if;

 RRL_STOCK_BALANCE_CORE.write_leg(v_uid,null,v_cell,v_qty,v_base,v_version,1,1,1,p_actor,v_event);

 insert into RRL_STORE_RETURN_RECEIPT(OPERATION_ID,PICKUP_OPERATION_ID,APPROVAL_OPERATION_ID,SAP_OPERATION_ID,UID_PALLET,ORIGINAL_LOT_UID,WARE_ID,RECEIVE_CELL,ARTICLE,BASE_QTY,BASE_UOM,DISPOSITION,OBSERVED_BATCH,BATCH_SOURCE,EXPIRY_DATE,GROSS_WEIGHT_KG,NET_WEIGHT_KG,STOCK_EVENT_ID,RECEIVED_BY,NAKLAD_ID)

 values(op,v_pickup,v_approval,v_sap,v_uid,v_old_uid,v_ware,v_cell,v_article,v_qty,v_base,v_disposition,v_batch,v_batch_source,v_expiry,v_gross,v_net,v_event,p_actor,v_naklad);

 if v.has('reuse_boxes')then RRL_STOCK_RETURN_REUSE.persist_boxes(op,p_actor,v.get_object('reuse_boxes'));end if;

 if v.has('return_basis')then j.put('return_basis',v.get_string('return_basis'));j.put('customer_accepted_quantity_changed',false);end if;j.put('operation_id',op);j.put('pickup_operation_id',v_pickup);j.put('pallet_identifier',v_uid);j.put('warehouse_id',v_ware);j.put('cell',v_cell);j.put('quantity',v.get_string('quantity'));j.put('base_uom',v_base);

 j.put('receiving_document_id',v_naklad);j.put('document_kind','STORE_RETURN');j.put('event_id',v_event);j.put('status','RECEIVED_PENDING_PLACEMENT');j.put('custody','WAREHOUSE');j.put('available_for_reservation',false);j.put('batch_source',v_batch_source);j.put('financial_erp_completion_created',false);p_result:=j.to_clob;

 end;

end;




/
