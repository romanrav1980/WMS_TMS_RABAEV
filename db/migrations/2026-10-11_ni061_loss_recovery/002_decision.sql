create or replace package RRL_STOCK_IW_RECOVERY_PLAN authid definer accessible by(package RRL_STOCK_POSTING_API) as
 procedure assert_scope(p_request clob,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_IW_RECOVERY_PLAN as
 procedure assert_scope(p_request clob,p_actor varchar2)is
 d json_object_t:=json_object_t.parse(p_request);kind varchar2(80):=d.get_string('command_type');loss_id varchar2(100);req_id varchar2(100);reporter varchar2(100);n number;
 begin
 if kind='INTERWARE_RECOVERY_REPORT'then loss_id:=d.get_object('source').get_string('loss_operation_id');
 elsif kind='INTERWARE_RECOVERY_APPROVE'then req_id:=d.get_object('source').get_string('request_operation_id');
  select LOSS_OPERATION_ID,ACTOR into loss_id,reporter from RRL_INTERWARE_RECOVERY_REQUEST where OPERATION_ID=req_id;
 else raise_application_error(-20886,'INTERWARE_RECOVERY_DECISION_REQUIRED');end if;
 select count(*)into n from RRL_INTERWARE_SHORTAGE_FACT loss join RRL_INTERWARE_RECEIPT r on r.OPERATION_ID=loss.RECEIPT_OPERATION_ID
 join RUSERS u on u.ID=p_actor where loss.OPERATION_ID=loss_id and nvl(u.DELETED,0)=0
 and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
 and RRL_HAS_WRIGHT(u.ID,case when kind='INTERWARE_RECOVERY_REPORT'then 'transport_dispatch_edit'else 'store_return_approve'end)=1;
 if n!=1 or(kind='INTERWARE_RECOVERY_APPROVE'and reporter=p_actor)then raise_application_error(-20882,'INTERWARE_RECOVERY_CURRENT_INDEPENDENT_TARGET_ACTOR_REQUIRED');end if;
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_RECOVERY_SOURCE_NOT_FOUND');
 end;
 procedure describe(p_request clob,p_actor varchar2,p_domain out json_object_t)is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');kind varchar2(80):=d.get_string('command_type');
 loss_id varchar2(100);req_id varchar2(100);loss RRL_INTERWARE_SHORTAGE_FACT%rowtype;receipt RRL_INTERWARE_RECEIPT%rowtype;req RRL_INTERWARE_RECOVERY_REQUEST%rowtype;
 n number;quantity number;wire clob;source json_object_t;unit_wire clob;fresh_units clob;expected_count number;total number;
 reason varchar2(2000):=m.get_string('reason');ref varchar2(2000):=m.get_string('evidence_reference');old_uid varchar2(200);old_cell varchar2(60);
 begin
 assert_scope(p_request,p_actor);
 if m.get_size!=3 or trim(reason)is null or length(trim(reason))<8 or length(reason)>500 or trim(ref)is null or length(ref)>255 then raise_application_error(-20886,'INTERWARE_RECOVERY_EXPLICIT_EVIDENCE_REQUIRED');end if;
 quantity:=RRL_STOCK_MATH.quantity(m.get_string('quantity'));
 if kind='INTERWARE_RECOVERY_REPORT'then loss_id:=d.get_object('source').get_string('loss_operation_id');
 else req_id:=d.get_object('source').get_string('request_operation_id');select *into req from RRL_INTERWARE_RECOVERY_REQUEST where OPERATION_ID=req_id;loss_id:=req.LOSS_OPERATION_ID;end if;
 select *into loss from RRL_INTERWARE_SHORTAGE_FACT where OPERATION_ID=loss_id;
 select *into receipt from RRL_INTERWARE_RECEIPT where OPERATION_ID=loss.RECEIPT_OPERATION_ID;
 select count(*)into n from RRL_STOCK_OPERATION where OPERATION_ID=loss_id and STATE='APPLIED'and COMMAND_TYPE='INTERWARE_SHORTAGE_CONFIRM';
 if n!=1 or quantity<=0 or quantity!=loss.SHORT_QTY or receipt.ORIGINAL_ROOT_UID is null or quantity+receipt.BASE_QTY!=receipt.EXPECTED_BASE_QTY then raise_application_error(-20886,'INTERWARE_RECOVERY_WHOLE_CONFIRMED_DIFFERENCE_REQUIRED');end if;
 select count(*)into n from RRL_INTERWARE_RECOVERY_RECEIPT where LOSS_OPERATION_ID=loss_id;if n!=0 then raise_application_error(-20886,'INTERWARE_RECOVERY_ALREADY_RECEIVED');end if;
 if kind='INTERWARE_RECOVERY_REPORT'then
 select count(*)into n from RRL_INTERWARE_RECOVERY_REQUEST where LOSS_OPERATION_ID=loss_id;if n!=0 then raise_application_error(-20886,'INTERWARE_RECOVERY_ALREADY_REPORTED');end if;
 else
 select count(*)into n from RRL_INTERWARE_RECOVERY_APPROVAL where REQUEST_OPERATION_ID=req_id;if n!=0 then raise_application_error(-20886,'INTERWARE_RECOVERY_ALREADY_APPROVED');end if;
 end if;
 source:=json_object_t.parse(loss.SOURCE_JSON);unit_wire:=source.get_array('missing_units').to_clob;expected_count:=source.get_array('missing_units').get_size;
 if expected_count>10000 then raise_application_error(-20886,'INTERWARE_RECOVERY_UNIT_BOUND');end if;
 old_uid:=source.get_string('original_uid');old_cell:=source.get_string('source_cell');
 if expected_count>0 then
 select count(*),sum(u.BASE_QTY),json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION)order by u.PHYSICAL_UNIT_KEY returning clob)
 into n,total,fresh_units from json_table(unit_wire,'$[*]'columns(K varchar2(64)path '$.key',Q varchar2(60)path '$.quantity',B varchar2(20)path '$.base_uom',V number path '$.version'))j
 join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=j.K join RRL_INTERWARE_SHORTAGE_UNIT book on book.PHYSICAL_UNIT_KEY=j.K and book.FACT_OPERATION_ID=loss_id
 where u.CURRENT_UID=old_uid and u.CURRENT_CELL=old_cell and u.STOCK_STATUS='ISSUED'and u.HARD_RESERVATION_ID is null
 and u.BASE_QTY=RRL_STOCK_MATH.quantity(j.Q)and u.BASE_UOM=j.B and u.BASE_UOM=receipt.BASE_UOM and u.UNIT_VERSION=j.V and book.UNIT_VERSION=j.V;
 if n!=expected_count or total!=quantity then raise_application_error(-20886,'INTERWARE_RECOVERY_EXACT_ISSUED_LOST_UNITS_REQUIRED');end if;
 else fresh_units:='[]';end if;
 p_domain:=json_object_t();p_domain.put('loss_operation_id',loss_id);p_domain.put('receipt_operation_id',receipt.OPERATION_ID);p_domain.put('warehouse_id',receipt.WARE_ID);
 p_domain.put('original_uid',old_uid);p_domain.put('source_cell',old_cell);p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(quantity));p_domain.put('base_uom',receipt.BASE_UOM);
 p_domain.put('source_units',json_array_t.parse(fresh_units));
 if req_id is not null then
  if dbms_lob.compare(json_object_t.parse(req.SOURCE_JSON).get_array('source_units').to_clob,fresh_units)!=0 then raise_application_error(-20886,'INTERWARE_RECOVERY_REPORTED_VERSIONS_CHANGED');end if;
  p_domain.put('request_operation_id',req_id);p_domain.put('reporter',req.ACTOR);
 end if;
 p_domain.put('reason',reason);p_domain.put('evidence_reference',ref);
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_RECOVERY_CONFIRMED_SOURCE_REQUIRED');
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;u json_object_t;
 begin
 describe(p_request,d.get_string('actor'),v);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_SHORTAGE_FACT',v.get_string('loss_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_RECOVERY_REQUEST',nvl(v.get_string('request_operation_id'),p_operation));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_RECOVERY_APPROVAL',nvl(v.get_string('request_operation_id'),p_operation));
 a:=v.get_array('source_units');for i in 0..a.get_size-1 loop u:=treat(a.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',u.get_string('key'));end loop;
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','IW.RECOVERY.LOSS:'||v.get_string('loss_operation_id'));
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');kind varchar2(80):=d.get_string('command_type');resolved clob;v json_object_t;fresh json_object_t;j json_object_t;
 loss_id varchar2(100);rec_id varchar2(100);req_id varchar2(100);ware number;qty number;uom varchar2(20);reason varchar2(2000);ref varchar2(2000);wire clob;
 begin
 select RESOLVED_PLAN_JSON into resolved from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(resolved).get_object('domain');
 describe(p_request,p_actor,fresh);if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: recovery decision');end if;
 loss_id:=v.get_string('loss_operation_id');rec_id:=v.get_string('receipt_operation_id');req_id:=v.get_string('request_operation_id');
 ware:=v.get_number('warehouse_id');qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));uom:=v.get_string('base_uom');reason:=v.get_string('reason');ref:=v.get_string('evidence_reference');wire:=v.to_clob;
 if kind='INTERWARE_RECOVERY_REPORT'then
 insert into RRL_INTERWARE_RECOVERY_REQUEST(OPERATION_ID,LOSS_OPERATION_ID,RECEIPT_OPERATION_ID,WARE_ID,BASE_QTY,BASE_UOM,ACTOR,REASON_TEXT,EVIDENCE_REFERENCE,SOURCE_JSON)
 values(op,loss_id,rec_id,ware,qty,uom,p_actor,reason,ref,wire);
 else
 insert into RRL_INTERWARE_RECOVERY_APPROVAL(OPERATION_ID,REQUEST_OPERATION_ID,ACTOR,REASON_TEXT,EVIDENCE_REFERENCE,SOURCE_JSON)values(op,req_id,p_actor,reason,ref,wire);
 end if;
 j:=json_object_t.parse(wire);j.put('operation_id',op);j.put('actor',p_actor);j.put('status',case when kind='INTERWARE_RECOVERY_REPORT'then 'RECOVERY_PENDING_INDEPENDENT_APPROVAL'else 'RECOVERY_APPROVED_PENDING_PHYSICAL_RECEIPT'end);
 j.put('stock_changed',false);j.put('regulatory_ack_verified',false);p_result:=j.to_clob;
 end;
end;
/
