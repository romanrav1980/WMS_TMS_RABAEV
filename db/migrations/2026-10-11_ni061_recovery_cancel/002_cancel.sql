create or replace package RRL_STOCK_IW_RECOVERY_CANCEL authid definer accessible by(package RRL_STOCK_POSTING_API)as
 procedure assert_scope(p_request varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
end;
/
create or replace package body RRL_STOCK_IW_RECOVERY_CANCEL as
 procedure assert_scope(p_request varchar2,p_actor varchar2)is req RRL_INTERWARE_RECOVERY_REQUEST%rowtype;n number;approved number;
 begin
 select *into req from RRL_INTERWARE_RECOVERY_REQUEST where OPERATION_ID=p_request;
 select count(*)into approved from RRL_INTERWARE_RECOVERY_APPROVAL where REQUEST_OPERATION_ID=p_request;
 select count(*)into n from RUSERS u where u.ID=p_actor and nvl(u.DELETED,0)=0 and(u.WARE_ID=req.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN')
 and RRL_HAS_WRIGHT(u.ID,'store_return_approve')=1;
 if n!=1 or(approved>0 and req.ACTOR=p_actor)then raise_application_error(-20882,'RECOVERY_CANCEL_CURRENT_INDEPENDENT_CONTROLLER_REQUIRED');end if;
 exception when no_data_found then raise_application_error(-20886,'RECOVERY_CANCEL_REQUEST_REQUIRED');end;
 procedure describe(p_request clob,p_actor varchar2,p_domain out json_object_t)is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');req_id varchar2(100):=d.get_object('source').get_string('request_operation_id');
 req RRL_INTERWARE_RECOVERY_REQUEST%rowtype;n number;reason varchar2(2000):=m.get_string('reason');ref varchar2(2000):=m.get_string('evidence_reference');source json_object_t;
 begin
 assert_scope(req_id,p_actor);select *into req from RRL_INTERWARE_RECOVERY_REQUEST where OPERATION_ID=req_id;
 if m.get_size!=3 or trim(reason)is null or length(trim(reason))<8 or length(reason)>500 or trim(ref)is null or length(ref)>255
 or RRL_STOCK_MATH.quantity(m.get_string('quantity'))!=req.BASE_QTY then raise_application_error(-20886,'RECOVERY_CANCEL_EXACT_REQUEST_REASON_EVIDENCE_REQUIRED');end if;
 select count(*)into n from RRL_IW_RECOVERY_CANCEL where REQUEST_OPERATION_ID=req_id;if n!=0 then raise_application_error(-20886,'RECOVERY_REQUEST_ALREADY_CANCELLED');end if;
 select count(*)into n from RRL_INTERWARE_RECOVERY_APPROVAL approved join RRL_INTERWARE_RECOVERY_RECEIPT received on received.APPROVAL_OPERATION_ID=approved.OPERATION_ID
 where approved.REQUEST_OPERATION_ID=req_id;if n!=0 then raise_application_error(-20886,'RECOVERY_PHYSICALLY_RECEIVED_CANNOT_CANCEL');end if;
 source:=json_object_t.parse(req.SOURCE_JSON);
 p_domain:=json_object_t();p_domain.put('request_operation_id',req_id);p_domain.put('loss_operation_id',req.LOSS_OPERATION_ID);
 p_domain.put('warehouse_id',req.WARE_ID);p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(req.BASE_QTY));p_domain.put('base_uom',req.BASE_UOM);
 p_domain.put('source_units',source.get_array('source_units'));p_domain.put('reason',reason);p_domain.put('evidence_reference',ref);
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob)is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();a json_array_t;u json_object_t;begin
 describe(p_request,d.get_string('actor'),v);RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_SHORTAGE_FACT',v.get_string('loss_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_INTERWARE_RECOVERY_REQUEST',v.get_string('request_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_IW_RECOVERY_CANCEL',v.get_string('request_operation_id'));
 a:=v.get_array('source_units');for i in 0..a.get_size-1 loop u:=treat(a.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.anchor(r,60,'UNIT',u.get_string('key'));end loop;
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob)is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');wire clob;v json_object_t;fresh json_object_t;
 req_id varchar2(100);loss_id varchar2(100);ware number;qty number;uom varchar2(20);reason varchar2(2000);ref varchar2(2000);begin
 select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(wire).get_object('domain');
 describe(p_request,p_actor,fresh);if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'RECOVERY_CANCEL_SOURCE_CHANGED');end if;
 req_id:=v.get_string('request_operation_id');loss_id:=v.get_string('loss_operation_id');ware:=v.get_number('warehouse_id');qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));
 uom:=v.get_string('base_uom');reason:=v.get_string('reason');ref:=v.get_string('evidence_reference');wire:=v.to_clob;
 insert into RRL_IW_RECOVERY_CANCEL(OPERATION_ID,REQUEST_OPERATION_ID,LOSS_OPERATION_ID,WARE_ID,BASE_QTY,BASE_UOM,ACTOR,REASON_TEXT,EVIDENCE_REFERENCE,SOURCE_JSON)
 values(op,req_id,loss_id,ware,qty,uom,p_actor,reason,ref,wire);
 v.put('operation_id',op);v.put('status','RECOVERY_CANCELLED');v.put('stock_changed',false);v.put('historical_loss_preserved',true);v.put('quantity_restored_to_unreported',v.get_string('quantity'));p_result:=v.to_clob;end;
end;
/
