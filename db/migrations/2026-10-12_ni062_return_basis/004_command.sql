create or replace PACKAGE BODY          "RRL_STOCK_STORE_RETURN_CMD" as
 procedure assert_actor(p_actor varchar2)is n number;
 begin select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and RRL_HAS_WRIGHT(ID,'store_return_approve')=1;if n!=1 then raise_application_error(-20882,'STORE_RETURN_CURRENT_APPROVER_REQUIRED');end if;end;
 procedure describe_return(p_request clob,p_actor varchar2,p_domain out json_object_t) is
 d json_object_t:=json_object_t.parse(p_request);s json_object_t:=d.get_object('source');m json_object_t:=d.get_object('metadata');
 v_receipt varchar2(100):=s.get_string('receipt_operation_id');v_line number:=s.get_number('line_no');
 v_qty number;v_used number;v_basis varchar2(10):=nvl(m.get_string('return_basis'),'ACCEPTED');v_limit number;v_units number;v_scale number;v_destination varchar2(20):=m.get_string('disposition');v_reason varchar2(32767):=m.get_string('reason');
 v_reference varchar2(32767):=m.get_string('decision_reference');v_good boolean:=m.get_boolean('complete_good_box');
 original RRL_STORE_RECEIPT_LINE%rowtype;v_store varchar2(255);v_load varchar2(100);selected_units clob;source_cell varchar2(60);reuse_source json_object_t;
 begin
 if RRL_HAS_WRIGHT(p_actor,'store_return_approve')!=1 then raise_application_error(-20882,'STORE_RETURN_SUPPLY_CHAIN_APPROVAL_REQUIRED');end if;
 if v_line is null or v_line!=trunc(v_line) or v_line<1 then raise_application_error(-20886,'STORE_RETURN_ORIGINAL_LINE_REQUIRED');end if;
 if v_destination is null or v_destination not in('REUSE','SUPPLIER','DISPOSAL') or trim(v_reason) is null or lengthb(v_reason)>2000 or trim(v_reference) is null or lengthb(v_reference)>255 then raise_application_error(-20886,'STORE_RETURN_REASON_DESTINATION_DECISION_REQUIRED');end if;
 if v_basis not in('ACCEPTED','REFUSED','DAMAGED')then raise_application_error(-20886,'STORE_RETURN_BASIS_REQUIRED');end if;
 if v_basis!='ACCEPTED'and v_destination='REUSE'then raise_application_error(-20886,'STORE_RETURN_EXCEPTION_REUSE_INSPECTION_REQUIRED');end if;
 if v_destination='REUSE' and (v_good is null or not v_good) then raise_application_error(-20886,'STORE_RETURN_REUSE_COMPLETE_GOOD_BOX_REQUIRED');end if;
 select * into original from RRL_STORE_RECEIPT_LINE where OPERATION_ID=v_receipt and LINE_NO=v_line;
 select STORE_ADDR,LOAD_OPERATION_ID,nvl(json_value(COMPOSITION_JSON,'$.physical_unit_count' returning number),1) into v_store,v_load,v_units from RRL_STORE_RECEIPT_FACT where OPERATION_ID=v_receipt;

 v_qty:=RRL_STOCK_MATH.quantity(m.get_string('quantity'));
 select BASE_SCALE into v_scale from RRL_STOCK_UOM_CONVERSION where ARTICUL=original.ARTICLE and INPUT_UOM=original.BASE_UOM and BASE_UOM=original.BASE_UOM and POLICY_VERSION=(select max(POLICY_VERSION) from RRL_STOCK_UOM_CONVERSION where ARTICUL=original.ARTICLE and INPUT_UOM=original.BASE_UOM and BASE_UOM=original.BASE_UOM);
 RRL_STOCK_MATH.assert_base(v_qty,v_scale);
 select nvl(sum(BASE_QTY),0) into v_used from RRL_STORE_RETURN_APPROVAL where RECEIPT_OPERATION_ID=v_receipt and LINE_NO=v_line and RETURN_BASIS=v_basis;
 case v_basis when 'ACCEPTED'then v_limit:=original.ACCEPTED_BASE_QTY;when 'REFUSED'then v_limit:=original.REFUSED_BASE_QTY;when 'DAMAGED'then v_limit:=original.DAMAGED_BASE_QTY;end case;
 if v_qty+v_used>v_limit then raise_application_error(-20886,'STORE_RETURN_SOURCE_DISPOSITION_QUANTITY_EXCEEDED');end if;
 if RRL_STOCK_QC_MARK.required_for_article(original.ARTICLE)=1 then v_units:=greatest(v_units,1);end if;
 p_domain:=json_object_t();
 if v_destination='REUSE'then
  RRL_STOCK_RETURN_REUSE.describe_source(original.LOT_UID,original.ARTICLE,original.BASE_UOM,v_qty,reuse_source);
  p_domain.put('reuse_source',reuse_source);
 end if;

 if v_units>0 then
  if not m.has('unit_keys')then raise_application_error(-20886,'STORE_RETURN_EXACT_UNIT_SELECTION_REQUIRED');end if;
  selected_units:=RRL_STORE_RETURN_UNIT_CORE.select_disposition_units(v_receipt,original.LOT_UID,original.BASE_UOM,v_qty,m.get_array('unit_keys').to_clob,v_basis);
  select json_value(COMPOSITION_JSON,'$.cell')into source_cell from RRL_STORE_RECEIPT_FACT where OPERATION_ID=v_receipt;
  p_domain.put('return_units',json_array_t.parse(selected_units));p_domain.put('source_cell',source_cell);
 elsif m.has('unit_keys')and m.get_array('unit_keys').get_size>0 then raise_application_error(-20886,'STORE_RETURN_UNEXPECTED_UNIT_SELECTION');end if;
if v_basis!='ACCEPTED'then p_domain.put('return_basis',v_basis);end if;
 p_domain.put('receipt_operation_id',v_receipt);p_domain.put('line_no',v_line);p_domain.put('load_operation_id',v_load);p_domain.put('store_address',v_store);
 p_domain.put('lot_uid',original.LOT_UID);p_domain.put('article',original.ARTICLE);p_domain.put('base_uom',original.BASE_UOM);p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));
 p_domain.put('previously_approved',RRL_STOCK_PLAN_HELPER.decimal_text(v_used));p_domain.put('disposition',v_destination);p_domain.put('reason',v_reason);p_domain.put('decision_reference',v_reference);
 if v_good then p_domain.put('complete_good_box',1);else p_domain.put('complete_good_box',0);end if;
 exception when no_data_found then raise_application_error(-20886,'STORE_RETURN_ORIGINAL_RECEIPT_OR_UOM_NOT_FOUND');
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();units json_array_t;x json_object_t;
 begin
 describe_return(p_request,d.get_string('actor'),v);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RECEIPT_LINE',v.get_string('receipt_operation_id')||':'||RRL_STOCK_PLAN_HELPER.decimal_text(v.get_number('line_no')));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_APPROVAL',p_operation);
 if v.has('return_units')then
  RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('lot_uid'),v.get_string('article'),v.get_string('source_cell'),null);
  units:=v.get_array('return_units');for i in 0..units.get_size-1 loop x:=treat(units.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',x.get_string('key'));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_UNIT',p_operation||':'||x.get_string('key'));end loop;
 end if;
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');v_receipt varchar2(100):=d.get_object('source').get_string('receipt_operation_id');
 v_line number:=d.get_object('source').get_number('line_no');v_dummy number;plan clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 v_lot varchar2(200);v_article varchar2(160);v_unit varchar2(20);v_qty number;v_destination varchar2(20);v_reason varchar2(2000);v_reference varchar2(255);v_good number;v_basis varchar2(10);
 begin
 select LINE_NO into v_dummy from RRL_STORE_RECEIPT_LINE where OPERATION_ID=v_receipt and LINE_NO=v_line for update;
 describe_return(p_request,p_actor,fresh);
 select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');
 if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20886,'STORE_RETURN_SOURCE_OR_APPROVAL_CHANGED');end if;
 v_basis:=nvl(v.get_string('return_basis'),'ACCEPTED');
 v_lot:=v.get_string('lot_uid');v_article:=v.get_string('article');v_unit:=v.get_string('base_uom');v_qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));
 v_destination:=v.get_string('disposition');v_reason:=v.get_string('reason');v_reference:=v.get_string('decision_reference');v_good:=v.get_number('complete_good_box');
 insert into RRL_STORE_RETURN_APPROVAL(OPERATION_ID,RECEIPT_OPERATION_ID,LINE_NO,LOT_UID,ARTICLE,BASE_UOM,BASE_QTY,DISPOSITION,REASON_TEXT,DECISION_REFERENCE,COMPLETE_GOOD_BOX,APPROVED_BY,RETURN_BASIS)
 values(op,v_receipt,v_line,v_lot,v_article,v_unit,v_qty,v_destination,v_reason,v_reference,v_good,p_actor,v_basis);
 if v.has('return_units')then
  RRL_STORE_RETURN_UNIT_CORE.persist(op,v_receipt,v_lot,v.get_string('source_cell'),v.get_array('return_units').to_clob);j.put('physical_unit_count',v.get_array('return_units').get_size);
 end if;
 if v_basis!='ACCEPTED'then j.put('return_basis',v_basis);j.put('customer_accepted_quantity_changed',false);end if;
 j.put('operation_id',op);j.put('receipt_operation_id',v_receipt);j.put('line_no',v_line);j.put('quantity',v.get_string('quantity'));j.put('base_uom',v_unit);j.put('disposition',v_destination);
 j.put('status','WAITING_SAP_AND_LOGISTICS');j.put('warehouse_stock_changed',false);j.put('sap_verified',false);j.put('government_ack_created',false);p_result:=j.to_clob;
 end;
end;

/
