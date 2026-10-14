create or replace package RRL_STOCK_IW_RECOVERY_REC authid definer accessible by(package RRL_STOCK_POSTING_API)as 
 procedure assert_scope(p_approval varchar2,p_actor varchar2); 
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob); 
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob); 
end;
/

create or replace package body RRL_STOCK_IW_RECOVERY_REC as 
 procedure assert_scope(p_approval varchar2,p_actor varchar2)is n number;begin 
 select count(*)into n from RRL_INTERWARE_RECOVERY_APPROVAL a join RRL_INTERWARE_RECOVERY_REQUEST req on req.OPERATION_ID=a.REQUEST_OPERATION_ID 
 join RUSERS u on u.ID=p_actor where a.OPERATION_ID=p_approval and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1 
 and(u.WARE_ID=req.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN'); 
 if n!=1 then raise_application_error(-20882,'INTERWARE_RECOVERY_CURRENT_RECEIVER_REQUIRED');end if; 
 end; 
 procedure describe(p_request clob,p_actor varchar2,p_domain out json_object_t)is 
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');approval_id varchar2(100):=d.get_object('source').get_string('approval_operation_id'); 
 approval RRL_INTERWARE_RECOVERY_APPROVAL%rowtype;req RRL_INTERWARE_RECOVERY_REQUEST%rowtype;receipt RRL_INTERWARE_RECEIPT%rowtype;source json_object_t;units clob;fresh_units clob; 
 n number;expected_count number;total number;qty number;target_uid varchar2(200);old_uid varchar2(200);source_cell varchar2(60);target_cell varchar2(60); 
 scan_article varchar2(160);scan_uom varchar2(20);ver number;scan_domain json_object_t;legs json_array_t;leg json_object_t;unit_count number;chosen_keys json_array_t;chosen_unit json_object_t; 
 begin 
 assert_scope(approval_id,p_actor); 
 select *into approval from RRL_INTERWARE_RECOVERY_APPROVAL where OPERATION_ID=approval_id; 
 select *into req from RRL_INTERWARE_RECOVERY_REQUEST where OPERATION_ID=approval.REQUEST_OPERATION_ID; 
 select count(*)into n from RRL_IW_RECOVERY_CANCEL where REQUEST_OPERATION_ID=req.OPERATION_ID;if n!=0 then raise_application_error(-20886,'RECOVERY_REQUEST_CANCELLED');end if;
 select *into receipt from RRL_INTERWARE_RECEIPT where OPERATION_ID=req.RECEIPT_OPERATION_ID; 
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=approval_id and COMMAND_TYPE='INTERWARE_RECOVERY_APPROVE'and STATE='APPLIED'; 
 if n!=1 then raise_application_error(-20886,'INTERWARE_RECOVERY_APPLIED_APPROVAL_REQUIRED');end if; 
 select count(*)into n from RRL_INTERWARE_RECOVERY_RECEIPT where APPROVAL_OPERATION_ID=approval_id;if n!=0 then raise_application_error(-20886,'INTERWARE_RECOVERY_ALREADY_RECEIVED');end if; 
 source:=json_object_t.parse(approval.SOURCE_JSON);old_uid:=source.get_string('original_uid');source_cell:=source.get_string('source_cell');units:=source.get_array('source_units').to_clob;expected_count:=source.get_array('source_units').get_size; 
 qty:=RRL_STOCK_MATH.quantity(m.get_string('quantity'));target_uid:=m.get_string('receipt_pallet_identifier');target_cell:=m.get_string('scan_cell'); 
 if qty!=req.BASE_QTY or m.get_string('article')!=receipt.ARTICLE or m.get_string('base_uom')!=req.BASE_UOM 
 or m.get_string('scan_source_pallet')is null or m.get_string('scan_source_pallet')!=old_uid 
 or m.get_string('scan_pallet')is null or m.get_string('scan_pallet')!=target_uid then raise_application_error(-20886,'INTERWARE_RECOVERY_EXACT_APPROVED_SOURCE_SCANS_REQUIRED');end if; 
 select count(*)into n from RRL_CELLS where CELL=target_cell and WARE_ID=req.WARE_ID and nvl(BLOCKED_FOR_ACCEPT,0)=0 and BLOCKED_FOR_REMAINS=1 and BLOCKED_FOR_POPOLNENIE=1; 
 if n!=1 then raise_application_error(-20886,'INTERWARE_RECOVERY_RECEIVING_QUARANTINE_CELL_REQUIRED');end if; 
 RRL_STOCK_QC_ITEM.resolve_barcode(m.get_string('scan_article'),scan_article,scan_uom); 
 if scan_article!=receipt.ARTICLE then raise_application_error(-20886,'INTERWARE_RECOVERY_FOREIGN_ARTICLE_BARCODE');end if; 
 select max(POLICY_VERSION)into ver from RRL_STOCK_UOM_CONVERSION where ARTICUL=receipt.ARTICLE and INPUT_UOM=req.BASE_UOM and BASE_UOM=req.BASE_UOM and NUMERATOR=DENOMINATOR; 
 if ver is null then raise_application_error(-20886,'INTERWARE_RECOVERY_BASE_UOM_REQUIRED');end if; 
 select count(*)into n from RRL_REMAINS where UID_POLETA=old_uid and(REMAIN!=0 or HARD_RESERVED_BASE!=0); 
 if n!=0 then raise_application_error(-20886,'INTERWARE_RECOVERY_ORIGINAL_STOCK_ALREADY_PRESENT');end if; 
 if expected_count>10000 then raise_application_error(-20886,'INTERWARE_RECOVERY_UNIT_BOUND');end if; 
 if expected_count>0 then 
 select count(*),sum(u.BASE_QTY),json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION)order by u.PHYSICAL_UNIT_KEY returning clob) 
 into n,total,fresh_units from json_table(units,'$[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom',V number path '$.version'))j 
 join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=j.K join RRL_INTERWARE_SHORTAGE_UNIT book on book.PHYSICAL_UNIT_KEY=j.K and book.FACT_OPERATION_ID=req.LOSS_OPERATION_ID 
 where u.CURRENT_UID=old_uid and u.CURRENT_CELL=source_cell and u.STOCK_STATUS='ISSUED'and u.HARD_RESERVATION_ID is null 
 and u.UNIT_VERSION=j.V and u.BASE_QTY=RRL_STOCK_MATH.quantity(j.Q)and u.BASE_UOM=j.B and u.BASE_UOM=req.BASE_UOM; 
 if n!=expected_count or total!=qty or dbms_lob.compare(units,fresh_units)!=0 then raise_application_error(-20886,'INTERWARE_RECOVERY_APPROVED_LOST_UNITS_CHANGED');end if; 
 elsif RRL_INTERWARE_MARK_SCAN.required_for_article(receipt.ARTICLE)=1 then raise_application_error(-20886,'INTERWARE_RECOVERY_MARKED_IDENTITY_REQUIRED');end if; 
 p_domain:=json_object_t();p_domain.put('approval_operation_id',approval_id);p_domain.put('request_operation_id',req.OPERATION_ID);p_domain.put('loss_operation_id',req.LOSS_OPERATION_ID); 
 p_domain.put('receipt_operation_id',receipt.OPERATION_ID);p_domain.put('plan_operation_id',receipt.PLAN_OPERATION_ID);p_domain.put('warehouse_id',req.WARE_ID); 
 p_domain.put('article',receipt.ARTICLE);p_domain.put('base_uom',req.BASE_UOM);p_domain.put('source_cell',source_cell);p_domain.put('receive_cell',target_cell);p_domain.put('uom_version',ver); 
 RRL_STOCK_INTERWARE_PART.describe_partial(m,old_uid,receipt.EXPECTED_BASE_QTY,req.BASE_UOM,receipt.ARTICLE,p_domain); 
 p_domain.put('source_units',json_array_t.parse(units));p_domain.put('recovery_receipt',true); 
 if expected_count>0 then 
  leg:=json_object_t();leg.put('article',receipt.ARTICLE);leg.put('uid',old_uid);leg.put('cell',source_cell);leg.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));leg.put('base_uom',req.BASE_UOM); 
  chosen_keys:=json_array_t();
  for selected_index in 0..source.get_array('source_units').get_size-1 loop
   chosen_unit:=treat(source.get_array('source_units').get(selected_index)as json_object_t);chosen_keys.append(chosen_unit.get_string('key'));
  end loop;
  leg.put('selected_unit_keys',chosen_keys);
  legs:=json_array_t();legs.append(leg);scan_domain:=json_object_t();scan_domain.put('legs',legs); 
  RRL_INTERWARE_MARK_SCAN.validate_scan(scan_domain.to_clob,m.to_clob,unit_count); 
  if unit_count!=expected_count then raise_application_error(-20886,'INTERWARE_RECOVERY_EXACT_PROFILE_SCANS_REQUIRED');end if; 
 elsif m.has('unit_scans')and m.get_array('unit_scans').get_size>0 then raise_application_error(-20886,'INTERWARE_RECOVERY_UNEXPECTED_UNIT_SCANS');end if; 
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_RECOVERY_APPROVED_LOST_SOURCE_REQUIRED'); 
 end; 
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is 
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;u json_object_t; 
 begin 
 describe(p_request,d.get_string('actor'),v); 
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation); 
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_SHORTAGE_FACT',v.get_string('loss_operation_id')); 
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_RECOVERY_APPROVAL',v.get_string('approval_operation_id')); 
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_RECOVERY_RECEIPT',p_operation); 
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',v.get_string('uid')); 
 RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('uid'),v.get_string('article'),null,v.get_string('receive_cell')); 
 RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('original_root_uid'),v.get_string('article'),null,null); 
 RRL_STOCK_PLAN_HELPER.anchor(r,50,'STOCK',v.get_string('source_origin_uid')); 
 a:=v.get_array('source_units');for i in 0..a.get_size-1 loop u:=treat(a.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',u.get_string('key'));end loop; 
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','IW.RECOVERY.APPROVAL:'||v.get_string('approval_operation_id')); 
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256))); 
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob; 
 end; 
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is 
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');resolved clob;v json_object_t;fresh json_object_t;wire clob;units clob;j json_object_t; 
 uid_value varchar2(200);old_uid varchar2(200);cell_value varchar2(60);source_cell varchar2(60);article varchar2(160);uom varchar2(20);qty number;ware number;version_no number;event_id number; 
 approval_id varchar2(100);loss_id varchar2(100); 
 begin 
 select RESOLVED_PLAN_JSON into resolved from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(resolved).get_object('domain');describe(p_request,p_actor,fresh); 
 if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: recovery receiving');end if; 
 uid_value:=v.get_string('uid');old_uid:=v.get_string('original_root_uid');cell_value:=v.get_string('receive_cell');source_cell:=v.get_string('source_cell');article:=v.get_string('article'); 
 uom:=v.get_string('base_uom');qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));ware:=v.get_number('warehouse_id');version_no:=v.get_number('uom_version');approval_id:=v.get_string('approval_operation_id');loss_id:=v.get_string('loss_operation_id');wire:=v.to_clob;units:=v.get_array('source_units').to_clob; 
 RRL_STOCK_LOCATION_CORE.assert_receiving(cell_value,ware);RRL_STOCK_INTERWARE_PART.create_pallet(v,op); 
 RRL_STOCK_BALANCE_CORE.apply_delta(uid_value,cell_value,qty,0,uom,version_no,0); 
 RRL_STOCK_BALANCE_CORE.write_leg(uid_value,null,cell_value,qty,uom,version_no,1,1,1,p_actor,event_id); 
 insert into RRL_INTERWARE_RECOVERY_RECEIPT(OPERATION_ID,APPROVAL_OPERATION_ID,LOSS_OPERATION_ID,WARE_ID,ROOT_UID,RECEIVE_CELL,ARTICLE,BASE_QTY,BASE_UOM,STOCK_EVENT_ID,ACTOR,SOURCE_JSON) 
 values(op,approval_id,loss_id,ware,uid_value,cell_value,article,qty,uom,event_id,p_actor,wire); 
 insert into RRL_INTERWARE_RECOVERY_UNIT(PHYSICAL_UNIT_KEY,RECOVERY_OPERATION_ID,LOSS_OPERATION_ID,BASE_QTY,BASE_UOM,PREVIOUS_UNIT_VERSION) 
 select K,op,loss_id,RRL_STOCK_MATH.quantity(Q),B,V from json_table(units,'$[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom',V number path '$.version')); 
 if v.get_array('source_units').get_size>0 then RRL_STOCK_UNIT_CORE.receive_partial_issued(old_uid,source_cell,uid_value,cell_value,qty,units);end if; 
 j:=json_object_t();j.put('operation_id',op);j.put('approval_operation_id',approval_id);j.put('loss_operation_id',loss_id);j.put('status','RECOVERED_PENDING_PLACEMENT'); 
 j.put('pallet_identifier',uid_value);j.put('original_pallet_identifier',old_uid);j.put('warehouse_id',ware);j.put('quantity',v.get_string('quantity'));j.put('base_uom',uom);j.put('cell',cell_value); 
 j.put('physical_unit_count',v.get_array('source_units').get_size);j.put('event_id',event_id);j.put('stock_changed',true);j.put('historical_loss_preserved',true);j.put('customer_delivery_confirmed',false);j.put('regulatory_ack_verified',false);p_result:=j.to_clob; 
 insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values('IW.RECOVERY:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(op,'AL32UTF8'),sys.dbms_crypto.hash_sh256)),'INTERWARE_SHORTAGE_RECOVERED',p_result); 
 end; 
end;
/
