create or replace package RRL_STOCK_STORE_RETURN_PUT authid definer accessible by(package RRL_STOCK_POSTING_API,package RRL_STOCK_TASK_PLAN,package RRL_STOCK_TASK_CORE,package RRL_STOCK_TASK_DOMAIN) as
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob);
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob);
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t);
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t);
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2);
end;
/
create or replace package body RRL_STOCK_STORE_RETURN_PUT as
 procedure describe_current(p_receipt varchar2,p_actor varchar2,p_task number,p_domain out json_object_t) is
 receipt RRL_STORE_RETURN_RECEIPT%rowtype;policy RRL_STORE_RETURN_WARE_POLICY%rowtype;
 v_target varchar2(60);v_p number;v_h number;v_unit varchar2(20);v_stock_version number;v_capacity number;v_height number;v_weight number;v_unknown number;n number;v_plan_count number;
 begin
 if RRL_HAS_WRIGHT(p_actor,'warehouse_return_place')!=1 then raise_application_error(-20882,'STORE_RETURN_PLACEMENT_FORBIDDEN');end if;
 select * into receipt from RRL_STORE_RETURN_RECEIPT where OPERATION_ID=p_receipt;
 select count(*) into n from RUSERS where ID=p_actor and nvl(DELETED,0)=0 and(upper(trim(USER_GROUP))='GLOBAL_ADMIN' or WARE_ID=receipt.WARE_ID);
 if n!=1 then raise_application_error(-20882,'STORE_RETURN_PLACEMENT_WAREHOUSE_BINDING_REQUIRED');end if;
 select * into policy from RRL_STORE_RETURN_WARE_POLICY where WARE_ID=receipt.WARE_ID;
 if receipt.DISPOSITION='REUSE' then
 select nvl(r.PICK_CELL,a.CELL) into v_target from RRL_ARTICULS a left join RRL_RECEIPT_SKU_RULE r on r.ARTICUL=a.ACTICUL and r.WARE_ID=receipt.WARE_ID where a.ACTICUL=receipt.ARTICLE;
 RRL_STOCK_RETURN_REUSE.assert_pick_target(receipt,v_target);
 else v_target:=case receipt.DISPOSITION when 'SUPPLIER' then policy.SUPPLIER_TARGET_CELL else policy.DISPOSAL_TARGET_CELL end;end if;
 if v_target is null or v_target=receipt.RECEIVE_CELL then raise_application_error(-20886,'STORE_RETURN_SEPARATE_TARGET_CONFIGURATION_REQUIRED');end if;
 if receipt.DISPOSITION!='REUSE' then
 select count(*) into n from RRL_CELLS where CELL=v_target and WARE_ID=receipt.WARE_ID and nvl(BLOCKED_FOR_ACCEPT,0)=0 and BLOCKED_FOR_REMAINS=1 and BLOCKED_FOR_POPOLNENIE=1 and nvl(OTBOR,0)=0;
 if n!=1 then raise_application_error(-20886,'STORE_RETURN_BLOCKED_TARGET_REQUIRED');end if;end if;
 select LIMIT_WEIGHT,LIMIT_HEIGHT into v_capacity,v_height from RRL_CELLS where CELL=v_target;
 if nvl(v_height,0)>0 then raise_application_error(-20886,'STORE_RETURN_TARGET_HEIGHT_PROOF_REQUIRED');end if;
 select count(*) into n from RRL_TOPOLOGY_CELL_SLOT slot_record join RRL_TOPOLOGY_CELL cell_record on cell_record.TOPOLOGY_CELL_ID=slot_record.TOPOLOGY_CELL_ID
 join RRL_WAREHOUSE_TOPOLOGY topology on topology.TOPOLOGY_ID=cell_record.TOPOLOGY_ID
 where cell_record.LEGACY_CELL_CODE=v_target and cell_record.WARE_ID=receipt.WARE_ID and cell_record.ACTIVE=1 and slot_record.ACTIVE=1 and topology.STATUS='PUBLISHED';
 if n!=0 then raise_application_error(-20886,'STORE_RETURN_PHYSICAL_SLOT_PLAN_REQUIRED');end if;
 select count(*) into n from RRL_STORE_RETURN_PLACEMENT where RECEIPT_OPERATION_ID=p_receipt;
 if n!=0 then raise_application_error(-20886,'STORE_RETURN_ALREADY_PLACED');end if;
 select REMAIN,HARD_RESERVED_BASE,BASE_UOM,STOCK_VERSION into v_p,v_h,v_unit,v_stock_version from RRL_REMAINS where UID_POLETA=receipt.UID_PALLET and CELL=receipt.RECEIVE_CELL;
 if v_p!=receipt.BASE_QTY or v_h!=0 or v_unit!=receipt.BASE_UOM then raise_application_error(-20886,'STORE_RETURN_WHOLE_UNRESERVED_RECEIVING_STOCK_REQUIRED');end if;
 select count(*) into n from RRL_REMAINS where UID_POLETA=receipt.UID_PALLET and CELL!=receipt.RECEIVE_CELL and(REMAIN!=0 or HARD_RESERVED_BASE!=0);
 if n!=0 then raise_application_error(-20886,'STORE_RETURN_MULTIPLE_SOURCE_CELLS_DENIED');end if;
 select count(*) into v_plan_count from RRL_STORE_RETURN_PUT_PLAN where RECEIPT_OPERATION_ID=p_receipt;
 if v_plan_count>100 then raise_application_error(-20881,'STORE_RETURN_PLAN_HISTORY_BOUND_100');end if;
 select count(*) into n from RRL_STORE_RETURN_PUT_PLAN plan_record join RRL_WAREHOUSE_TASK wt on wt.TASK_ID=plan_record.TASK_ID
 where plan_record.RECEIPT_OPERATION_ID=p_receipt and wt.STATUS!='CANCELLED' and(p_task is null or wt.TASK_ID!=p_task);
 if n!=0 then raise_application_error(-20886,'STORE_RETURN_EXISTING_ACTIVE_PLACEMENT_TASK');end if;
 if nvl(v_capacity,0)>0 then
  select nvl(sum(pp.WEIGHT_BRUTTO),0),nvl(sum(case when pp.WEIGHT_BRUTTO is null then 1 else 0 end),0) into v_weight,v_unknown
  from (
   select r.UID_POLETA UID_PALLET from RRL_REMAINS r where r.CELL=v_target and r.REMAIN>0 and r.UID_POLETA!=receipt.UID_PALLET
   union
   select wt.UID_PALLET from RRL_WAREHOUSE_TASK wt where wt.TO_CELL=v_target and wt.STATUS not in('DONE','CANCELLED')
    and wt.UID_PALLET!=receipt.UID_PALLET and(p_task is null or wt.TASK_ID!=p_task)
  ) occupants join RRL_PALLETS pp on pp.UID_PALLET=occupants.UID_PALLET;
  if v_unknown>0 or v_weight+receipt.GROSS_WEIGHT_KG>v_capacity then raise_application_error(-20886,'STORE_RETURN_TARGET_TOTAL_WEIGHT_EXCEEDED');end if;
 end if;
 p_domain:=json_object_t();p_domain.put('receipt_operation_id',p_receipt);p_domain.put('naklad_id',receipt.NAKLAD_ID);p_domain.put('warehouse_id',receipt.WARE_ID);p_domain.put('uid',receipt.UID_PALLET);p_domain.put('article',receipt.ARTICLE);
 p_domain.put('from_cell',receipt.RECEIVE_CELL);p_domain.put('target_cell',v_target);p_domain.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(receipt.BASE_QTY));p_domain.put('base_uom',receipt.BASE_UOM);p_domain.put('stock_version',v_stock_version);
 p_domain.put('policy_version',policy.POLICY_VERSION);p_domain.put('disposition',receipt.DISPOSITION);
 exception when no_data_found then raise_application_error(-20886,'STORE_RETURN_PLACEMENT_SOURCE_CONFIGURATION_REQUIRED');
 end;
 procedure declare_rows(p_domain json_object_t,p_resources in out nocopy json_array_t) is
 begin
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_RETURN_RECEIPT',p_domain.get_string('receipt_operation_id'));
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_PRIHOD_NAKLAD',RRL_STOCK_PLAN_HELPER.decimal_text(p_domain.get_number('naklad_id')));
 end;
 procedure compile_command(p_request clob,p_operation varchar2,p_policies out clob,p_resources out clob,p_domain out clob) is
 d json_object_t:=json_object_t.parse(p_request);v json_object_t;f json_array_t:=json_array_t();r json_array_t:=json_array_t();v_task number;
 begin
 describe_current(d.get_object('source').get_string('receipt_operation_id'),d.get_string('actor'),null,v);
 select RRL_WAREHOUSE_TASK_SQ.nextval into v_task from dual;v.put('task_id',v_task);
 RRL_STOCK_PLAN_HELPER.fence(f,'RELEASE','STOCK');RRL_STOCK_PLAN_HELPER.fence(f,'CONFIG','WAREHOUSE');RRL_STOCK_PLAN_HELPER.anchor(r,10,'OP',p_operation);
 RRL_STOCK_PLAN_HELPER.anchor(r,70,'UNIQUE','STOCK.OUTBOX:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(p_operation,'AL32UTF8'),sys.dbms_crypto.hash_sh256)));
 declare_rows(v,r);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_STORE_RETURN_PUT_PLAN',p_operation);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WAREHOUSE_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(v_task));
 RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('uid'),v.get_string('article'),v.get_string('from_cell'),v.get_string('target_cell'));
 p_policies:=f.to_clob;p_resources:=r.to_clob;p_domain:=v.to_clob;
 end;
 procedure execute_command(p_request clob,p_actor varchar2,p_result out clob) is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');plan clob;v json_object_t;fresh json_object_t;j json_object_t:=json_object_t();
 v_receipt varchar2(100);v_task number;v_doc number;v_ware number;v_policy number;v_uid varchar2(200);v_article varchar2(160);v_from varchar2(60);v_to varchar2(60);v_unit varchar2(20);v_qty number;
 begin
 select RESOLVED_PLAN_JSON into plan from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(plan).get_object('domain');v_receipt:=v.get_string('receipt_operation_id');v_task:=v.get_number('task_id');
 describe_current(v_receipt,p_actor,null,fresh);fresh.put('task_id',v_task);
 if dbms_lob.compare(v.to_clob,fresh.to_clob)!=0 then raise_application_error(-20886,'STORE_RETURN_PLACEMENT_PLAN_SOURCE_CHANGED');end if;
 v_doc:=v.get_number('naklad_id');v_ware:=v.get_number('warehouse_id');v_policy:=v.get_number('policy_version');v_uid:=v.get_string('uid');v_article:=v.get_string('article');v_from:=v.get_string('from_cell');v_to:=v.get_string('target_cell');v_unit:=v.get_string('base_uom');v_qty:=RRL_STOCK_MATH.quantity(v.get_string('quantity'));
 insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,TARGET_ARTICUL,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY)
 values(v_task,'PUTAWAY','MANUAL',v_task,'STORE_RETURN',v_doc,v_uid,v_article,v_from,v_to,v_ware,v_ware,v_qty,v_unit,'PALLET','PLANNED',p_actor);
 insert into RRL_STORE_RETURN_PUT_PLAN(OPERATION_ID,RECEIPT_OPERATION_ID,TASK_ID,POLICY_VERSION,TARGET_CELL,PLANNED_BY)values(op,v_receipt,v_task,v_policy,v_to,p_actor);
 j.put('operation_id',op);j.put('task_id',v_task);j.put('receipt_operation_id',v_receipt);j.put('from_cell',v_from);j.put('to_cell',v_to);j.put('quantity',v.get_string('quantity'));j.put('base_uom',v_unit);j.put('warehouse_stock_changed',false);p_result:=j.to_clob;
 end;
 procedure plan_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_resources in out nocopy json_array_t,p_domain in out nocopy json_object_t) is
 v_receipt varchar2(100);v json_object_t;v_policy number;v_target varchar2(60);op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');
 begin
 select RECEIPT_OPERATION_ID,POLICY_VERSION,TARGET_CELL into v_receipt,v_policy,v_target from RRL_STORE_RETURN_PUT_PLAN where TASK_ID=p_task.TASK_ID;
 describe_current(v_receipt,p_actor,p_task.TASK_ID,v);
 if p_task.TASK_SOURCE!='MANUAL' or p_task.TASK_TYPE!='PUTAWAY' or p_task.SOURCE_DOC_TYPE!='STORE_RETURN' or p_task.SOURCE_DOC_ID!=v.get_number('naklad_id')
 or p_task.UID_PALLET!=v.get_string('uid') or p_task.FROM_CELL!=v.get_string('from_cell') or p_task.TO_CELL!=v.get_string('target_cell') or p_task.UNIT_CODE!=v.get_string('base_uom')
 or p_task.QTY!=RRL_STOCK_MATH.quantity(v.get_string('quantity')) or p_task.QTY_MODE!='PALLET' or v_policy!=v.get_number('policy_version') or v_target!=p_task.TO_CELL then raise_application_error(-20886,'STORE_RETURN_ORIGINAL_PLACEMENT_TASK_CONFLICT');end if;
 declare_rows(v,p_resources);
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_STORE_RETURN_PLACEMENT',RRL_STOCK_PLAN_HELPER.decimal_text(p_task.TASK_ID));
 RRL_STOCK_PLAN_HELPER.anchor(p_resources,70,'UNIQUE','SAP.OUTBOX:STORE_RETURN_PLACED:'||RRL_STOCK_PLAN_HELPER.decimal_text(p_task.TASK_ID));
 p_domain.put('store_return_placement',v);
 exception when no_data_found then raise_application_error(-20886,'STORE_RETURN_REGISTERED_PLACEMENT_TASK_REQUIRED');
 end;
 procedure validate_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_actor varchar2,p_frozen json_object_t) is
 r json_array_t:=json_array_t();d json_object_t:=json_object_t();current_domain json_object_t;
 begin
 plan_task(p_task,p_actor,r,d);current_domain:=d.get_object('store_return_placement');
 if p_frozen is null or dbms_lob.compare(current_domain.to_clob,p_frozen.to_clob)!=0 then raise_application_error(-20886,'STORE_RETURN_PLACEMENT_LOCKED_SOURCE_CHANGED');end if;
 end;
 procedure complete_task(p_task RRL_WAREHOUSE_TASK%rowtype,p_quantity number,p_target_uid varchar2,p_actor varchar2) is
 v_receipt varchar2(100);receipt RRL_STORE_RETURN_RECEIPT%rowtype;sap RRL_STORE_RETURN_SAP%rowtype;approval RRL_STORE_RETURN_APPROVAL%rowtype;
 op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');payload json_object_t:=json_object_t();v_payload clob;v_event varchar2(100);n number;
 begin
 select RECEIPT_OPERATION_ID into v_receipt from RRL_STORE_RETURN_PUT_PLAN where TASK_ID=p_task.TASK_ID;
 select * into receipt from RRL_STORE_RETURN_RECEIPT where OPERATION_ID=v_receipt;
 if p_quantity!=receipt.BASE_QTY or p_target_uid!=receipt.UID_PALLET then raise_application_error(-20886,'STORE_RETURN_WHOLE_PLACEMENT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_STORE_RETURN_PLACEMENT',RRL_STOCK_PLAN_HELPER.decimal_text(p_task.TASK_ID)));
 select count(*) into n from RRL_WAREHOUSE_TASK where TASK_ID=p_task.TASK_ID and STATUS='DONE' and FACT_QTY=receipt.BASE_QTY;
 if n!=1 then raise_application_error(-20886,'STORE_RETURN_COMPLETED_PHYSICAL_TASK_REQUIRED');end if;
 insert into RRL_STORE_RETURN_PLACEMENT(OPERATION_ID,RECEIPT_OPERATION_ID,TASK_ID,UID_PALLET,TARGET_CELL,BASE_QTY,BASE_UOM,PLACED_BY)values(op,v_receipt,p_task.TASK_ID,p_target_uid,p_task.TO_CELL,receipt.BASE_QTY,receipt.BASE_UOM,p_actor);
 update RRL_PRIHOD_NAKLAD set CONDITION=2 where ID=receipt.NAKLAD_ID and DOCUMENT_KIND='STORE_RETURN' and CONDITION=1;
 if sql%rowcount!=1 then raise_application_error(-20886,'STORE_RETURN_DOCUMENT_PLACEMENT_STATE_CONFLICT');end if;
 select * into sap from RRL_STORE_RETURN_SAP where OPERATION_ID=receipt.SAP_OPERATION_ID;
 select * into approval from RRL_STORE_RETURN_APPROVAL where OPERATION_ID=receipt.APPROVAL_OPERATION_ID;
 payload.put('operation_id',op);payload.put('return_document',sap.RETURN_DOCUMENT);payload.put('sender',sap.SAP_SENDER);payload.put('approval_operation_id',receipt.APPROVAL_OPERATION_ID);payload.put('receipt_operation_id',v_receipt);payload.put('original_store_receipt',approval.RECEIPT_OPERATION_ID);
 payload.put('pallet_identifier',p_target_uid);payload.put('original_lot_uid',receipt.ORIGINAL_LOT_UID);payload.put('article',receipt.ARTICLE);payload.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(receipt.BASE_QTY));payload.put('base_uom',receipt.BASE_UOM);
 payload.put('warehouse_id',receipt.WARE_ID);payload.put('cell',p_task.TO_CELL);payload.put('disposition',receipt.DISPOSITION);payload.put('supplier_batch',receipt.OBSERVED_BATCH);payload.put('batch_source',receipt.BATCH_SOURCE);payload.put('expiry_date',to_char(receipt.EXPIRY_DATE,'YYYY-MM-DD'));
 payload.put('placement_confirmed',true);payload.put('supplier_transfer_confirmed',false);payload.put('external_sap_ack',false);
 v_event:='STORE_RETURN_PLACED:'||RRL_STOCK_PLAN_HELPER.decimal_text(p_task.TASK_ID);v_payload:=payload.to_clob;
 insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values(v_event,'STORE_RETURN_PLACED',v_payload);
 end;
end;
/
