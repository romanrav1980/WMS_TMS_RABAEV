create or replace package RRL_STOCK_INTERWARE_SHORT_CMD authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure assert_scope(p_request clob,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_INTERWARE_SHORT_CMD as
 procedure assert_scope(p_request clob,p_actor varchar2)is
 d json_object_t:=json_object_t.parse(p_request);rec_id varchar2(100);v_kind varchar2(80):=d.get_string('command_type');n number;reporter varchar2(100);v_request varchar2(100);
 begin
 if v_kind='INTERWARE_SHORTAGE_REPORT'then rec_id:=d.get_object('source').get_string('receipt_operation_id');
 elsif v_kind='INTERWARE_SHORTAGE_CONFIRM'then
  v_request:=d.get_object('source').get_string('request_operation_id');select RECEIPT_OPERATION_ID,ACTOR into rec_id,reporter from RRL_INTERWARE_SHORTAGE_REQUEST where OPERATION_ID=v_request;
 else raise_application_error(-20886,'INTERWARE_SHORTAGE_COMMAND_REQUIRED');end if;
 select count(*)into n from RRL_INTERWARE_RECEIPT r join RUSERS u on u.ID=p_actor where r.OPERATION_ID=rec_id and nvl(u.DELETED,0)=0
 and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
 and RRL_HAS_WRIGHT(u.ID,case when v_kind='INTERWARE_SHORTAGE_REPORT'then 'transport_dispatch_edit'else 'store_return_approve'end)=1;
 if n!=1 or(v_kind='INTERWARE_SHORTAGE_CONFIRM'and reporter=p_actor)then raise_application_error(-20882,'INTERWARE_SHORTAGE_CURRENT_INDEPENDENT_TARGET_ACTOR_REQUIRED');end if;
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_SHORTAGE_REQUEST_NOT_FOUND');
 end;
 procedure describe(p_request clob,p_actor varchar2,p_domain out json_object_t)is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');v_kind varchar2(80):=d.get_string('command_type');receipt RRL_INTERWARE_RECEIPT%rowtype;req RRL_INTERWARE_SHORTAGE_REQUEST%rowtype;
 rec_id varchar2(100);request_id varchar2(100);resolved clob;dom json_object_t;original_units clob;accepted_units clob;missing_units clob;
 n number;expected_count number;qty number;v_source_cell varchar2(60);reason varchar2(2000):=m.get_string('reason');ref varchar2(2000):=m.get_string('evidence_reference');quantity number;
 begin
 assert_scope(p_request,p_actor);
 if m.get_size!=3 or trim(reason)is null or length(trim(reason))<8 or length(reason)>500 or trim(ref)is null or length(ref)>255 then raise_application_error(-20886,'INTERWARE_SHORTAGE_REASON_DOCUMENT_REQUIRED');end if;
 quantity:=RRL_STOCK_MATH.quantity(m.get_string('quantity'));
 if v_kind='INTERWARE_SHORTAGE_REPORT'then rec_id:=d.get_object('source').get_string('receipt_operation_id');
 else request_id:=d.get_object('source').get_string('request_operation_id');select *into req from RRL_INTERWARE_SHORTAGE_REQUEST where OPERATION_ID=request_id;rec_id:=req.RECEIPT_OPERATION_ID;end if;
 select *into receipt from RRL_INTERWARE_RECEIPT where OPERATION_ID=rec_id;
 if receipt.ORIGINAL_ROOT_UID is null or receipt.EXPECTED_BASE_QTY<=receipt.BASE_QTY or quantity!=receipt.EXPECTED_BASE_QTY-receipt.BASE_QTY then raise_application_error(-20886,'INTERWARE_SHORTAGE_EXACT_PARTIAL_DIFFERENCE_REQUIRED');end if;
 select count(*)into n from RRL_INTERWARE_SHORTAGE_FACT where RECEIPT_OPERATION_ID=rec_id;if n!=0 then raise_application_error(-20886,'INTERWARE_SHORTAGE_ALREADY_CONFIRMED');end if;
 if v_kind='INTERWARE_SHORTAGE_REPORT'then
  select count(*)into n from RRL_INTERWARE_SHORTAGE_REQUEST where RECEIPT_OPERATION_ID=rec_id;if n!=0 then raise_application_error(-20886,'INTERWARE_SHORTAGE_ALREADY_REPORTED');end if;
 end if;
 select RESOLVED_PLAN_JSON into resolved from RRL_STOCK_OPERATION where OPERATION_ID=rec_id and STATE='APPLIED'and COMMAND_TYPE='INTERWARE_RECEIVE';
 dom:=json_object_t.parse(resolved).get_object('domain');v_source_cell:=dom.get_string('source_cell');expected_count:=0;
 if dom.has('original_source_units')then
  original_units:=dom.get_array('original_source_units').to_clob;accepted_units:=dom.get_array('source_units').to_clob;
  if dom.get_array('original_source_units').get_size>10000 or dom.get_array('source_units').get_size>10000 then raise_application_error(-20886,'INTERWARE_SHORTAGE_UNIT_BOUND');end if;
  select count(*)into expected_count from json_table(original_units,'$[*]'columns(K varchar2(64)path '$.key'))j
   where not exists(select 1 from json_table(accepted_units,'$[*]'columns(K varchar2(64)path '$.key'))a where a.K=j.K);
  select count(*),sum(u.BASE_QTY),
   json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION)order by u.PHYSICAL_UNIT_KEY returning clob)
   into n,qty,missing_units from json_table(original_units,'$[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom'))j
   join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=j.K
   where not exists(select 1 from json_table(accepted_units,'$[*]'columns(K varchar2(64)path '$.key'))a where a.K=j.K)
   and u.CURRENT_UID=receipt.ORIGINAL_ROOT_UID and u.CURRENT_CELL=v_source_cell and u.STOCK_STATUS='ISSUED'and u.HARD_RESERVATION_ID is null
   and u.BASE_QTY=RRL_STOCK_MATH.quantity(j.Q)and u.BASE_UOM=j.B and u.BASE_UOM=receipt.BASE_UOM
   and not exists(select 1 from RRL_INTERWARE_SHORTAGE_UNIT booked where booked.PHYSICAL_UNIT_KEY=u.PHYSICAL_UNIT_KEY);
  if expected_count<1 or n!=expected_count or qty!=quantity then raise_application_error(-20886,'INTERWARE_SHORTAGE_CURRENT_EXACT_ISSUED_UNITS_REQUIRED');end if;
 else missing_units:='[]';end if;
 p_domain:=json_object_t();p_domain.put('receipt_operation_id',rec_id);p_domain.put('plan_operation_id',receipt.PLAN_OPERATION_ID);
 p_domain.put('source_load_operation_id',receipt.SOURCE_LOAD_OPERATION_ID);p_domain.put('original_uid',receipt.ORIGINAL_ROOT_UID);p_domain.put('accepted_uid',receipt.ROOT_UID);
 p_domain.put('warehouse_id',receipt.WARE_ID);p_domain.put('expected_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(receipt.EXPECTED_BASE_QTY));
 p_domain.put('accepted_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(receipt.BASE_QTY));p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(quantity));
 p_domain.put('base_uom',receipt.BASE_UOM);p_domain.put('missing_units',json_array_t.parse(missing_units));p_domain.put('source_cell',v_source_cell);
 if request_id is not null then
  if dbms_lob.compare(json_object_t.parse(req.SOURCE_JSON).get_array('missing_units').to_clob,missing_units)!=0 then raise_application_error(-20886,'INTERWARE_SHORTAGE_REPORTED_UNIT_VERSIONS_CHANGED');end if;
  p_domain.put('request_operation_id',request_id);p_domain.put('reporter',req.ACTOR);
 end if;
 p_domain.put('reason',reason);p_domain.put('evidence_reference',ref);
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_SHORTAGE_ACTUAL_PARTIAL_RECEIPT_REQUIRED');
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();units json_array_t;u json_object_t;
 begin
 describe(p_request,d.get_string('actor'),v);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_RECEIPT',v.get_string('receipt_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_SHORTAGE_REQUEST',nvl(v.get_string('request_operation_id'),p_operation));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_SHORTAGE_FACT',v.get_string('receipt_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_TT_HU_LOAD_FACT',v.get_string('source_load_operation_id'));
 RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',v.get_string('original_uid'));
 units:=v.get_array('missing_units');for i in 0..units.get_size-1 loop u:=treat(units.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',u.get_string('key'));end loop;
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','IW.SHORT.RECEIPT:'||v.get_string('receipt_operation_id'));
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');kind varchar2(80):=d.get_string('command_type');wire clob;v json_object_t;fresh json_object_t;j json_object_t;
 rec_id varchar2(100);plan_id varchar2(100);load_id varchar2(100);req_id varchar2(100);old_uid varchar2(200);new_uid varchar2(200);ware number;expected number;accepted number;quantity number;uom varchar2(20);reason varchar2(2000);ref varchar2(2000);units clob;domain_wire clob;
 begin
 select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(wire).get_object('domain');
 describe(p_request,p_actor,fresh);if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: interwarehouse shortage');end if;
 rec_id:=v.get_string('receipt_operation_id');plan_id:=v.get_string('plan_operation_id');load_id:=v.get_string('source_load_operation_id');req_id:=v.get_string('request_operation_id');
 old_uid:=v.get_string('original_uid');new_uid:=v.get_string('accepted_uid');ware:=v.get_number('warehouse_id');expected:=RRL_STOCK_MATH.quantity(v.get_string('expected_quantity'));
 accepted:=RRL_STOCK_MATH.quantity(v.get_string('accepted_quantity'));quantity:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));uom:=v.get_string('base_uom');reason:=v.get_string('reason');ref:=v.get_string('evidence_reference');units:=v.get_array('missing_units').to_clob;domain_wire:=v.to_clob;
 if kind='INTERWARE_SHORTAGE_REPORT'then
  insert into RRL_INTERWARE_SHORTAGE_REQUEST(OPERATION_ID,RECEIPT_OPERATION_ID,PLAN_OPERATION_ID,SOURCE_LOAD_OPERATION_ID,ORIGINAL_UID,ACCEPTED_UID,WARE_ID,EXPECTED_QTY,ACCEPTED_QTY,SHORT_QTY,BASE_UOM,ACTOR,REASON_TEXT,EVIDENCE_REFERENCE,SOURCE_JSON)
   values(op,rec_id,plan_id,load_id,old_uid,new_uid,ware,expected,accepted,quantity,uom,p_actor,reason,ref,domain_wire);
 else
  insert into RRL_INTERWARE_SHORTAGE_FACT(OPERATION_ID,REQUEST_OPERATION_ID,RECEIPT_OPERATION_ID,ACTOR,REASON_TEXT,EVIDENCE_REFERENCE,SHORT_QTY,SOURCE_JSON)
   values(op,req_id,rec_id,p_actor,reason,ref,quantity,domain_wire);
  insert into RRL_INTERWARE_SHORTAGE_UNIT(PHYSICAL_UNIT_KEY,FACT_OPERATION_ID,ORIGINAL_UID,UNIT_VERSION,BASE_QTY,BASE_UOM)
   select K,op,old_uid,V,RRL_STOCK_MATH.quantity(Q),B from json_table(units,'$[*]'columns(K varchar2(64)path '$.key',V number path '$.version',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom'));
 end if;
 j:=json_object_t.parse(v.to_clob);j.put('operation_id',op);j.put('actor',p_actor);j.put('status',case when kind='INTERWARE_SHORTAGE_REPORT'then 'PENDING_INDEPENDENT_CONFIRMATION'else 'CONFIRMED_CARRIER_SHORTAGE'end);
 j.put('stock_changed',false);j.put('carrier_custody_released',false);j.put('regulatory_ack_verified',false);p_result:=j.to_clob;
 insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values('IW.SHORT:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(op,'AL32UTF8'),sys.dbms_crypto.hash_sh256)),kind,p_result);
 end;
end;
/
