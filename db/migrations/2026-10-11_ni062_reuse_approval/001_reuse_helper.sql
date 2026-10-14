CREATE OR REPLACE EDITIONABLE PACKAGE "RABAEV"."RRL_STOCK_RETURN_REUSE" authid definer accessible by(package RRL_STOCK_STORE_RETURN_REC_CMD,package RRL_STOCK_STORE_RETURN_PUT,package RRL_STOCK_STORE_RETURN_CMD,package RRL_RETURN_REUSE_API) as
 procedure describe_source(p_lot varchar2,p_article varchar2,p_unit varchar2,p_qty number,p_proof out json_object_t);
 procedure describe_boxes(p_approval RRL_STORE_RETURN_APPROVAL%rowtype,p_metadata json_object_t,p_scan_uom varchar2,p_batch_source varchar2,p_ware number,p_proof out json_object_t);
 procedure persist_boxes(p_operation varchar2,p_actor varchar2,p_proof json_object_t);
 procedure assert_pick_target(p_receipt RRL_STORE_RETURN_RECEIPT%rowtype,p_target varchar2);
end;
/
CREATE OR REPLACE EDITIONABLE PACKAGE BODY "RABAEV"."RRL_STOCK_RETURN_REUSE" as

 procedure describe_source(p_lot varchar2,p_article varchar2,p_unit varchar2,p_qty number,p_proof out json_object_t)is
  lot RRL_PALLETS%rowtype;n number;batch varchar2(100);base varchar2(20);num number;den number;scale number;version number;box number;
 begin
  select *into lot from RRL_PALLETS where UID_PALLET=p_lot;
  if lot.ARTICUL is null or lot.ARTICUL!=p_article or lot.EXPIRY_DATE is null or trunc(lot.EXPIRY_DATE)<trunc(sysdate)then raise_application_error(-20886,'RETURN_REUSE_SOURCE_EXPIRY_ARTICLE_REQUIRED');end if;
  select count(*),min(SUPPLIER_BATCH)into n,batch from RRL_SAP_PALLET_RECEIPT where UID_PALLET=nvl(lot.STOCK_ORIGIN_UID,lot.UID_PALLET);
  if n!=1 or batch is null then raise_application_error(-20886,'RETURN_REUSE_ORIGINAL_VERIFIED_BATCH_GOOD_BOX_REQUIRED');end if;
  select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE,POLICY_VERSION into base,num,den,scale,version from RRL_STOCK_UOM_CONVERSION
   where ARTICUL=p_article and INPUT_UOM='BOX'and POLICY_VERSION=(select max(POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM='BOX');
  box:=RRL_STOCK_MATH.convert_exact('1',num,den,scale);
  if base!=p_unit or box<=0 or mod(p_qty,box)!=0 then raise_application_error(-20886,'RETURN_REUSE_FULL_BOX_BASE_QUANTITY_CONFLICT');end if;
  p_proof:=json_object_t();p_proof.put('supplier_batch',batch);p_proof.put('origin_uid',nvl(lot.STOCK_ORIGIN_UID,lot.UID_PALLET));
  p_proof.put('expiry_date',to_char(lot.EXPIRY_DATE,'YYYY-MM-DD'));p_proof.put('uom_policy_version',version);
  p_proof.put('box_count',RRL_STOCK_PLAN_HELPER.decimal_text(p_qty/box));p_proof.put('box_base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(box));
  p_proof.put('physical_completeness_verified',false);
 exception when no_data_found then raise_application_error(-20886,'RETURN_REUSE_CURRENT_SOURCE_BOX_UOM_REQUIRED');
 end;

 procedure describe_boxes(p_approval RRL_STORE_RETURN_APPROVAL%rowtype,p_metadata json_object_t,p_scan_uom varchar2,p_batch_source varchar2,p_ware number,p_proof out json_object_t) is
 v_count number;v_num number;v_den number;v_scale number;v_version number;v_base varchar2(20);v_box number;v_quantity number;v_good boolean;v_min_days number;
 begin
 if p_approval.COMPLETE_GOOD_BOX!=1 or p_batch_source!='ORIGINAL_SAP_VERIFIED' then raise_application_error(-20886,'RETURN_REUSE_ORIGINAL_VERIFIED_BATCH_GOOD_BOX_REQUIRED');end if;
 v_good:=p_metadata.get_boolean('complete_good_boxes');
 if v_good is null or not v_good or p_scan_uom!='BOX' or not regexp_like(p_metadata.get_string('full_box_count'),'^[1-9][0-9]{0,17}$')then raise_application_error(-20886,'RETURN_REUSE_PHYSICAL_COMPLETE_BOX_BARCODE_COUNT_REQUIRED');end if;
 select nvl(max(MIN_SHELF_DAYS),0)into v_min_days from RRL_RECEIPT_SKU_RULE where ARTICUL=p_approval.ARTICLE and WARE_ID=p_ware;
 if to_date(p_metadata.get_string('expiry_date'),'FXYYYY-MM-DD')<trunc(sysdate)+v_min_days then raise_application_error(-20886,'RETURN_REUSE_SHELF_LIFE_REQUIRED');end if;
 v_count:=RRL_STOCK_MATH.quantity(p_metadata.get_string('full_box_count'));
 select BASE_UOM,NUMERATOR,DENOMINATOR,BASE_SCALE,POLICY_VERSION into v_base,v_num,v_den,v_scale,v_version from RRL_STOCK_UOM_CONVERSION
 where ARTICUL=p_approval.ARTICLE and INPUT_UOM='BOX' and POLICY_VERSION=(select max(POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_approval.ARTICLE and INPUT_UOM='BOX');
 v_box:=RRL_STOCK_MATH.convert_exact('1',v_num,v_den,v_scale);v_quantity:=RRL_STOCK_MATH.convert_exact(p_metadata.get_string('full_box_count'),v_num,v_den,v_scale);
 if v_base!=p_approval.BASE_UOM or v_quantity!=p_approval.BASE_QTY then raise_application_error(-20886,'RETURN_REUSE_FULL_BOX_BASE_QUANTITY_CONFLICT');end if;
 p_proof:=json_object_t();p_proof.put('box_count',RRL_STOCK_PLAN_HELPER.decimal_text(v_count));p_proof.put('box_base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_box));p_proof.put('uom_policy_version',v_version);p_proof.put('barcode',p_metadata.get_string('scan_article'));p_proof.put('supplier_batch',p_metadata.get_string('supplier_batch'));
 exception when no_data_found then raise_application_error(-20886,'RETURN_REUSE_CURRENT_BOX_UOM_REQUIRED');end;
 procedure persist_boxes(p_operation varchar2,p_actor varchar2,p_proof json_object_t) is v_count number;v_box number;v_version number;v_code varchar2(128);v_batch varchar2(100);
 begin
 if p_proof is null then return;end if;
 v_count:=RRL_STOCK_MATH.quantity(p_proof.get_string('box_count'));v_box:=RRL_STOCK_MATH.quantity(p_proof.get_string('box_base_quantity'));v_version:=p_proof.get_number('uom_policy_version');v_code:=p_proof.get_string('barcode');v_batch:=p_proof.get_string('supplier_batch');
 insert into RRL_RETURN_REUSE_PROOF(OPERATION_ID,BOX_COUNT,BOX_BASE_QTY,UOM_POLICY_VERSION,ARTICLE_BARCODE,SOURCE_BATCH,ACTOR)values(p_operation,v_count,v_box,v_version,v_code,v_batch,p_actor);
 end;
 procedure assert_pick_target(p_receipt RRL_STORE_RETURN_RECEIPT%rowtype,p_target varchar2) is n number;v_min_days number;v_tmin number;v_tmax number;v_cell_min number;v_cell_max number;v_mix number;v_planned_count number:=0;v_key varchar2(1000);
 begin
 select count(*)into n from RRL_RETURN_REUSE_PROOF where OPERATION_ID=p_receipt.OPERATION_ID and BOX_COUNT*BOX_BASE_QTY=p_receipt.BASE_QTY and SOURCE_BATCH=p_receipt.OBSERVED_BATCH;
 if n!=1 or p_receipt.BATCH_SOURCE!='ORIGINAL_SAP_VERIFIED'then raise_application_error(-20886,'RETURN_REUSE_RECEIVED_FULL_BOX_PROOF_REQUIRED');end if;
 select count(*)into n from RRL_CELLS where CELL=p_target and WARE_ID=p_receipt.WARE_ID and OTBOR=1 and nvl(IS_SYSTEM,0)=0 and nvl(BLOCKED_FOR_ACCEPT,0)=0 and nvl(BLOCKED_FOR_REMAINS,0)=0 and nvl(BLOCKED_FOR_POPOLNENIE,0)=0;
 if n!=1 then raise_application_error(-20886,'RETURN_REUSE_CURRENT_PICKING_CELL_REQUIRED');end if;
 select nvl(max(MIN_SHELF_DAYS),0),max(TEMP_MIN),max(TEMP_MAX)into v_min_days,v_tmin,v_tmax from RRL_RECEIPT_SKU_RULE where WARE_ID=p_receipt.WARE_ID and ARTICUL=p_receipt.ARTICLE;
 if trunc(p_receipt.EXPIRY_DATE)<trunc(sysdate)+v_min_days then raise_application_error(-20886,'RETURN_REUSE_SHELF_LIFE_REQUIRED');end if;
 if v_tmin is not null or v_tmax is not null then
  select TEMP_MIN,TEMP_MAX into v_cell_min,v_cell_max from RRL_RECEIPT_CELL_RULE where WARE_ID=p_receipt.WARE_ID and CELL=p_target;
  if v_cell_min is null or v_cell_max is null or(v_tmin is not null and v_cell_min<v_tmin)or(v_tmax is not null and v_cell_max>v_tmax)then raise_application_error(-20886,'RETURN_REUSE_PICKING_TEMPERATURE_REQUIRED');end if;
 end if;
 select nvl(max(ALLOW_PICK_BATCH_MIX),0) into v_mix from RRL_RECEIPT_SKU_RULE where WARE_ID=p_receipt.WARE_ID and ARTICUL=p_receipt.ARTICLE;
 v_key:=RRL_STOCK_REPL_ADMISSION.lot_key(p_receipt.UID_PALLET);
 for planned in(select wt.UID_PALLET,pp.ARTICUL from RRL_WAREHOUSE_TASK wt join RRL_PALLETS pp on pp.UID_PALLET=wt.UID_PALLET
  where wt.TO_CELL=p_target and wt.STATUS not in('DONE','CANCELLED') and wt.UID_PALLET!=p_receipt.UID_PALLET)loop
  v_planned_count:=v_planned_count+1;if v_planned_count>200 then raise_application_error(-20881,'RETURN_REUSE_PLANNED_TARGET_BOUND_200');end if;
  if planned.ARTICUL!=p_receipt.ARTICLE or(v_mix!=1 and RRL_STOCK_REPL_ADMISSION.lot_key(planned.UID_PALLET)!=v_key)then raise_application_error(-20886,'RETURN_REUSE_PLANNED_TARGET_SKU_BATCH_CONFLICT');end if;
 end loop;
 RRL_STOCK_REPL_ADMISSION.assert_target(p_receipt.UID_PALLET,p_target,p_receipt.WARE_ID,p_receipt.ARTICLE);
 exception when no_data_found then raise_application_error(-20886,'RETURN_REUSE_PICKING_POLICY_REQUIRED');end;
end;
/
