create or replace package RRL_STOCK_INTERWARE_PART authid definer accessible by(package RRL_STOCK_INTERWARE_REC) as
 procedure describe_partial(p_metadata json_object_t,p_original_uid varchar2,p_original_qty number,p_unit varchar2,p_article varchar2,p_domain in out json_object_t);
 procedure create_pallet(p_domain json_object_t,p_operation varchar2);
end;
/
create or replace package body RRL_STOCK_INTERWARE_PART as
 procedure describe_partial(p_metadata json_object_t,p_original_uid varchar2,p_original_qty number,p_unit varchar2,p_article varchar2,p_domain in out json_object_t)is
  v_target_uid varchar2(200):=p_metadata.get_string('receipt_pallet_identifier');qty number;gross number;reason varchar2(4000):=p_metadata.get_string('discrepancy_reason');ref varchar2(2000):=p_metadata.get_string('discrepancy_reference');
  lot RRL_PALLETS%rowtype;n number;scale number;
 begin
  if v_target_uid is null or v_target_uid=p_original_uid or length(v_target_uid)>50 or lengthb(v_target_uid)>150 or trim(reason)is null or length(trim(reason))<8 or length(reason)>1000 or trim(ref)is null or length(ref)>255 then raise_application_error(-20886,'INTERWARE_PARTIAL_FRESH_PALLET_REASON_REQUIRED');end if;
  qty:=RRL_STOCK_MATH.quantity(p_metadata.get_string('quantity'));gross:=RRL_STOCK_MATH.quantity(p_metadata.get_string('gross_weight_kg'));
  if qty<=0 or qty>=p_original_qty or gross<=0 or gross>1000000 then raise_application_error(-20886,'INTERWARE_PARTIAL_POSITIVE_ACTUAL_QUANTITY_GROSS_REQUIRED');end if;
  select BASE_SCALE into scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM=p_unit and BASE_UOM=p_unit and NUMERATOR=DENOMINATOR
   and POLICY_VERSION=(select max(POLICY_VERSION)from RRL_STOCK_UOM_CONVERSION where ARTICUL=p_article and INPUT_UOM=p_unit and BASE_UOM=p_unit and NUMERATOR=DENOMINATOR);
  RRL_STOCK_MATH.assert_base(qty,scale);
  select count(*)into n from RRL_PALLETS where UID_PALLET=v_target_uid;if n!=0 then raise_application_error(-20886,'INTERWARE_PARTIAL_PALLET_ALREADY_EXISTS');end if;
  select count(*)into n from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_original_uid;
  if n!=0 or RRL_INTERWARE_MARK_SCAN.required_for_article(p_article)=1 then raise_application_error(-20886,'INTERWARE_PARTIAL_EXACT_SERIALIZED_SELECTION_REQUIRED');end if;
  select *into lot from RRL_PALLETS where UID_PALLET=p_original_uid;
  p_domain.put('partial_receipt',true);p_domain.put('original_root_uid',p_original_uid);p_domain.put('uid',v_target_uid);
  p_domain.put('expected_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(p_original_qty));p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));
  p_domain.put('short_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(p_original_qty-qty));p_domain.put('gross_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(gross));
  p_domain.put('discrepancy_reason',reason);p_domain.put('discrepancy_reference',ref);p_domain.put('source_price',lot.PRICE);
  p_domain.put('source_expiry',to_char(lot.EXPIRY_DATE,'YYYY-MM-DD HH24:MI:SS'));p_domain.put('source_produced',to_char(lot.PRODUCED_DATE,'YYYY-MM-DD HH24:MI:SS'));
  p_domain.put('source_origin_uid',nvl(lot.STOCK_ORIGIN_UID,lot.UID_PALLET));p_domain.put('source_naklad_id',lot.PRIHOD_NAKLAD_ID);
  p_domain.put('gross_weight_basis','MANUAL_RECEIVER_OBSERVATION');p_domain.put('carrier_shortage_resolved',false);
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_PARTIAL_ORIGINAL_LOT_UOM_REQUIRED');
 end;
 procedure create_pallet(p_domain json_object_t,p_operation varchar2)is
  v_target_uid varchar2(200):=p_domain.get_string('uid');article varchar2(160):=p_domain.get_string('article');origin varchar2(200):=p_domain.get_string('source_origin_uid');
  expiry date:=to_date(p_domain.get_string('source_expiry'),'YYYY-MM-DD HH24:MI:SS');produced date:=to_date(p_domain.get_string('source_produced'),'YYYY-MM-DD HH24:MI:SS');
  qty number:=RRL_STOCK_MATH.quantity(p_domain.get_string('quantity'));gross number:=RRL_STOCK_MATH.quantity(p_domain.get_string('gross_weight_kg'));price number:=p_domain.get_number('source_price');naklad number:=p_domain.get_number('source_naklad_id');
 begin
  if not p_domain.get_boolean('partial_receipt')then raise_application_error(-20863,'INTERWARE_PARTIAL_CAPTURED_PLAN_REQUIRED');end if;
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',v_target_uid));
  RRL_STOCK_LOCK_API.assert_held(50,RRL_STOCK_LOCK_API.resource_key('STOCK',p_domain.get_string('original_root_uid')));
  insert into RRL_PALLETS(UID_PALLET,ARTICUL,CREATION_DATE,EXPIRY_DATE,PRODUCED_DATE,UNIT_COUNT,PRICE,STOCK_ORIGIN_UID,CREATED_BY_STOCK_OP,WEIGHT_BRUTTO,PRIHOD_NAKLAD_ID)
   values(v_target_uid,article,systimestamp,expiry,produced,qty,price,origin,p_operation,gross,naklad);
 end;
end;
/
