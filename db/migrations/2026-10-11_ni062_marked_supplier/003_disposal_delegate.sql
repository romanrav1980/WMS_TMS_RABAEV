create or replace package RRL_STOCK_RETURN_DISPOSE authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_EFFECT_CORE) as
 procedure assert_scope(p_request varchar2,p_actor varchar2);
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure validate_consume(p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_quantity number,p_ware number,p_actor varchar2);
end;
/

create or replace package body RRL_STOCK_RETURN_DISPOSE as
 procedure assert_scope(p_request varchar2,p_actor varchar2)is n number;
 begin
  select count(*)into n from RRL_RETURN_DISPOSAL_REQUEST q join RRL_STORE_RETURN_RECEIPT r on r.OPERATION_ID=q.RECEIPT_OPERATION_ID join RUSERS u on u.ID=p_actor
   where q.OPERATION_ID=p_request and q.ACTOR!=p_actor and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'store_return_approve')=1 and(u.WARE_ID=r.WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
  if n!=1 then raise_application_error(-20882,'RETURN_DISPOSAL_CURRENT_INDEPENDENT_ACTOR_REQUIRED');end if;
 end;
 procedure describe(p_request clob,p_actor varchar2,p_domain out json_object_t) is
 d json_object_t:=json_object_t.parse(p_request);m json_object_t:=d.get_object('metadata');
 req RRL_RETURN_DISPOSAL_REQUEST%rowtype;rec RRL_STORE_RETURN_RECEIPT%rowtype;
 v_id varchar2(100):=m.get_string('request_operation_id');v_cell varchar2(60);v_qty number;v_h number;v_version number;v_uom varchar2(20);v_policy number;v_store varchar2(255);n number;actual number;total number;unit_wire clob;key_wire clob;profiles clob;leg json_object_t;legs json_array_t;scan_domain json_object_t;unit_count number;j json_object_t:=json_object_t();
 begin
 select *into req from RRL_RETURN_DISPOSAL_REQUEST where OPERATION_ID=v_id;
 select *into rec from RRL_STORE_RETURN_RECEIPT where OPERATION_ID=req.RECEIPT_OPERATION_ID;
 if rec.DISPOSITION!='DISPOSAL' then raise_application_error(-20886,'RETURN_DISPOSAL_APPROVED_DISPOSITION_REQUIRED');end if;
 select count(*)into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and(WARE_ID=rec.WARE_ID or upper(trim(USER_GROUP))='GLOBAL_ADMIN')and RRL_HAS_WRIGHT(ID,'store_return_approve')=1;
 if n!=1 or req.ACTOR=p_actor then raise_application_error(-20882,'RETURN_DISPOSAL_INDEPENDENT_BOUND_SC_REQUIRED');end if;
 if m.get_string('decision_reference')is null or length(m.get_string('decision_reference'))>60 then raise_application_error(-20886,'RETURN_DISPOSAL_DECISION_REQUIRED');end if;
 select count(*)into n from RRL_RETURN_DISPOSAL_FACT where RECEIPT_OPERATION_ID=rec.OPERATION_ID;if n!=0 then raise_application_error(-20886,'RETURN_DISPOSAL_ALREADY_POSTED');end if;
 select REMAIN,HARD_RESERVED_BASE,STOCK_VERSION,BASE_UOM,CELL into v_qty,v_h,v_version,v_uom,v_cell from RRL_REMAINS where UID_POLETA=rec.UID_PALLET and REMAIN>0;
 if v_qty!=rec.BASE_QTY or v_h!=0 or v_uom!=rec.BASE_UOM or v_version!=m.get_number('expected_stock_version')or m.get_number('expected_stock_version')is null then raise_application_error(-20886,'RETURN_DISPOSAL_CURRENT_WHOLE_UNRESERVED_VERSION_REQUIRED');end if;
 if m.get_string('scan_pallet')is null or m.get_string('scan_pallet')!=rec.UID_PALLET or m.get_string('scan_cell')is null or m.get_string('scan_cell')!=v_cell then raise_application_error(-20886,'RETURN_DISPOSAL_SOURCE_SCANS_REQUIRED');end if;
 select count(*)into n from RRL_CELLS where CELL=v_cell and WARE_ID=rec.WARE_ID and BLOCKED_FOR_REMAINS=1 and BLOCKED_FOR_POPOLNENIE=1;if n!=1 then raise_application_error(-20886,'RETURN_DISPOSAL_SEGREGATED_SOURCE_REQUIRED');end if;
 select count(*)into n from RRL_WMS_HU_LINK where ACTIVE_FLAG=1 and(CHILD_PALLET_UID=rec.UID_PALLET or PARENT_UID=rec.UID_PALLET);if n!=0 then raise_application_error(-20886,'RETURN_DISPOSAL_STANDALONE_SOURCE_REQUIRED');end if;
 select count(*)into n from dual where exists(select 1 from RRL_SKU_RECEIPT_PROFILE where ARTICUL=rec.ARTICLE)or exists(select 1 from RRL_SKU_RECEIPT_POLICY where ARTICUL=rec.ARTICLE and MARKING_REQUIRED=1)or exists(select 1 from RRL_FINISHED_GOODS_SKU where ARTICUL=rec.ARTICLE and CRPT_REQUIRED=1);
 if n!=0 then
  select count(*),sum(case when SCAN_MODE='UNIT'and lengthb(SYSTEM_CODE)<=30 then 0 else 1 end),json_arrayagg(json_object('system_code'value SYSTEM_CODE,'profile_code'value PROFILE_CODE,'profile_version'value PROFILE_VERSION,'scan_mode'value SCAN_MODE)order by SYSTEM_CODE,PROFILE_CODE returning clob)
   into n,actual,profiles from RRL_SKU_RECEIPT_PROFILE where ARTICUL=rec.ARTICLE;
  if n<1 or n>50 or actual!=0 then raise_application_error(-20886,'RETURN_DISPOSAL_CURRENT_UNIT_PROFILES_REQUIRED');end if;
  select count(*),sum(u.BASE_QTY),json_arrayagg(json_object('key'value u.PHYSICAL_UNIT_KEY,'quantity'value RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY),'base_uom'value u.BASE_UOM,'version'value u.UNIT_VERSION,'origin_uid'value u.UID_PALLET,'unit_id'value u.UNIT_ID)order by u.PHYSICAL_UNIT_KEY returning clob),json_arrayagg(u.PHYSICAL_UNIT_KEY order by u.PHYSICAL_UNIT_KEY returning clob)
   into n,total,unit_wire,key_wire from RRL_STORE_RETURN_UNIT b join RRL_WMS_RECEIPT_UNIT u on u.PHYSICAL_UNIT_KEY=b.PHYSICAL_UNIT_KEY
   where b.APPROVAL_OPERATION_ID=rec.APPROVAL_OPERATION_ID and u.CURRENT_UID=rec.UID_PALLET and u.CURRENT_CELL=v_cell and u.BASE_QTY=b.BASE_QTY and u.BASE_UOM=b.BASE_UOM and u.STOCK_STATUS='AVAILABLE'and u.HARD_RESERVATION_ID is null;
  select count(*)into actual from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=rec.UID_PALLET and CURRENT_CELL=v_cell;
  if n<1 or n>10000 or actual!=n or total!=rec.BASE_QTY then raise_application_error(-20886,'RETURN_DISPOSAL_EXACT_ORIGINAL_APPROVED_UNITS_REQUIRED');end if;
  leg:=json_object_t();leg.put('uid',rec.UID_PALLET);leg.put('article',rec.ARTICLE);leg.put('cell',v_cell);leg.put('base_uom',v_uom);leg.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));legs:=json_array_t();legs.append(leg);scan_domain:=json_object_t();scan_domain.put('legs',legs);
  RRL_STOCK_QC_MARK.validate_scan(scan_domain.to_clob,m.to_clob,unit_count);
  if unit_count!=n then raise_application_error(-20886,'RETURN_DISPOSAL_EXACT_SCANNED_UNIT_COUNT_REQUIRED');end if;
  j.put('disposal_units',json_array_t.parse(unit_wire));j.put('disposal_unit_keys',json_array_t.parse(key_wire));j.put('disposal_profiles',json_array_t.parse(profiles));
 elsif m.has('unit_scans')and m.get_array('unit_scans').get_size>0 then raise_application_error(-20886,'RETURN_DISPOSAL_ORDINARY_UNEXPECTED_SCANS');end if;
 select max(POLICY_VERSION)into v_policy from RRL_STOCK_UOM_CONVERSION where ARTICUL=rec.ARTICLE and INPUT_UOM=v_uom and BASE_UOM=v_uom and NUMERATOR=1 and DENOMINATOR=1;
 if v_policy is null then raise_application_error(-20886,'RETURN_DISPOSAL_BASE_UOM_REQUIRED');end if;
 select f.STORE_ADDR into v_store from RRL_STORE_RETURN_APPROVAL a join RRL_STORE_RECEIPT_FACT f on f.OPERATION_ID=a.RECEIPT_OPERATION_ID where a.OPERATION_ID=rec.APPROVAL_OPERATION_ID;
 if v_store is null then raise_application_error(-20886,'RETURN_DISPOSAL_ORIGINAL_LOSS_STORE_REQUIRED');end if;
 j.put('request_operation_id',req.OPERATION_ID);j.put('receipt_operation_id',rec.OPERATION_ID);j.put('uid',rec.UID_PALLET);j.put('article',rec.ARTICLE);j.put('cell',v_cell);j.put('warehouse_id',rec.WARE_ID);j.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));j.put('base_uom',v_uom);j.put('uom_version',v_policy);j.put('stock_version',v_version);j.put('loss_store_addr',v_store);j.put('document_reference',req.DOCUMENT_REFERENCE);j.put('document_sha256',req.DOCUMENT_SHA256);j.put('decision_reference',m.get_string('decision_reference'));
 p_domain:=j;
 exception when no_data_found then raise_application_error(-20886,'RETURN_DISPOSAL_SOURCE_REQUIRED');when too_many_rows then raise_application_error(-20886,'RETURN_DISPOSAL_ONE_SOURCE_REQUIRED');end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();
 begin
 describe(p_request,d.get_string('actor'),v);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');
 RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RETURN_DISPOSAL_REQUEST',v.get_string('request_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_RECEIPT',v.get_string('receipt_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_RETURN_DISPOSAL_FACT',p_operation);
 RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('uid'),v.get_string('article'),v.get_string('cell'),null);
 if v.has('disposal_profiles')then RRL_REGULATORY_API.declare_stock_events(p_operation,'MARKED_GOODS_DISPOSED',v.get_array('disposal_profiles').to_clob,r);end if;
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','SAP.OUTBOX:RETURN_DISPOSAL:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure validate_consume(p_receipt varchar2,p_uid varchar2,p_cell varchar2,p_quantity number,p_ware number,p_actor varchar2) is
 op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_name varchar2(80);req clob;v json_object_t;
 begin
 select COMMAND_TYPE,CANONICAL_REQUEST into kind_name,req from RRL_STOCK_OPERATION where OPERATION_ID=op and STATE='IN_FLIGHT';
 if kind_name!='STORE_RETURN_DISPOSE' then raise_application_error(-20886,'RETURN_DISPOSAL_EXPLICIT_ROOT_REQUIRED');end if;
 describe(req,p_actor,v);
 if v.get_string('receipt_operation_id')!=p_receipt or v.get_string('uid')!=p_uid or v.get_string('cell')!=p_cell or v.get_number('warehouse_id')!=p_ware or RRL_STOCK_MATH.quantity(v.get_string('quantity'))!=p_quantity then raise_application_error(-20886,'RETURN_DISPOSAL_EXACT_SOURCE_REQUIRED');end if;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');plan clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();payload json_object_t;body clob;
 v_req varchar2(100);v_receipt varchar2(100);v_uid varchar2(200);v_cell varchar2(60);v_unit varchar2(20);v_store varchar2(255);v_ref varchar2(255);v_qty number;v_ware number;v_policy number;v_event varchar2(100);keys clob;unit_wire clob;profile_wire clob;code_wire clob;gov json_object_t;gov_id number;gov_key varchar2(100);gov_ids json_array_t:=json_array_t();
 begin
 select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');describe(p_request,p_actor,fresh);
 if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20890,'CLOSURE_CHANGED: return disposal');end if;
 v_req:=v.get_string('request_operation_id');v_receipt:=v.get_string('receipt_operation_id');v_uid:=v.get_string('uid');v_cell:=v.get_string('cell');v_unit:=v.get_string('base_uom');v_store:=v.get_string('loss_store_addr');v_ref:=v.get_string('decision_reference');v_qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));v_ware:=v.get_number('warehouse_id');v_policy:=v.get_number('uom_version');
 if v.has('disposal_unit_keys')then keys:=v.get_array('disposal_unit_keys').to_clob;end if;
 RRL_STOCK_EFFECT_CORE.consume(v_uid,v_cell,v_qty,v_unit,v_policy,v_ware,p_actor,1,p_units=>keys,p_disposal_receipt=>v_receipt);
 insert into RRL_RETURN_DISPOSAL_FACT(OPERATION_ID,REQUEST_OPERATION_ID,RECEIPT_OPERATION_ID,UID_PALLET,BASE_QTY,BASE_UOM,LOSS_STORE_ADDR,DECISION_REFERENCE,ACTOR)values(op,v_req,v_receipt,v_uid,v_qty,v_unit,v_store,v_ref,p_actor);
 j.put('operation_id',op);j.put('status','DISPOSED');j.put('receipt_operation_id',v_receipt);j.put('quantity',v.get_string('quantity'));j.put('base_uom',v_unit);j.put('pallet_identifier',v_uid);j.put('loss_store_addr',v_store);j.put('external_sap_ack',false);
 if v.has('disposal_profiles')then
  gov_ids:=json_array_t.parse(RRL_REGULATORY_API.enqueue_stock_events(op,'MARKED_GOODS_DISPOSED',v.to_clob,v.get_array('disposal_units').to_clob,v.get_array('disposal_profiles').to_clob));
  j.put('physical_unit_count',v.get_array('disposal_units').get_size);j.put('regulatory_event_ids',gov_ids);j.put('regulatory_status','PENDING');j.put('external_regulatory_ack',false);
 end if;
 payload:=json_object_t.parse(v.to_clob);payload.put('operation_id',op);payload.put('status','DISPOSED');payload.put('actor',p_actor);body:=payload.to_clob;v_event:='RETURN.DISPOSAL:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(op,'AL32UTF8'),sys.dbms_crypto.hash_sh256));
 insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values(v_event,'STORE_RETURN_DISPOSED',body);p_result:=j.to_clob;
 end;
end;
/
