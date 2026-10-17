create or replace package body RRL_QC_SCOPE_READ as
 function policy_json(p_domain clob) return clob is
  d json_object_t:=json_object_t.parse(p_domain);j json_object_t:=json_object_t();
  w number:=d.get_number('warehouse');origin_ware number:=w;document_no number:=d.get_number('document_id');addr varchar2(255);category varchar2(10);
  mode_name varchar2(10);independent number;percent number;selected_flag number:=0;
  ex_whole number:=0;ex_storage number:=0;depth_no number:=0;visited varchar2(2000):='|';stamp varchar2(16000):='';
  token varchar2(100);digest varchar2(64);
 begin
  select ADDR into addr from RRL_SBORKA_PALLETS where ID=document_no;
  category:=case when d.get_number('case_task') is null then 'STOCK' else 'CASE' end;
  select nvl(s.OUTGOING_QC_MODE,case when nvl(wa.BLOCK_IF_NO_PROOVE,0)=1 then 'ANY' else 'NONE' end),
   nvl(s.OUTGOING_QC_INDEPENDENT,0),nvl(s.OUTGOING_QC_SAMPLE_PERCENT,0)
   into mode_name,independent,percent from RRL_WARES wa left join RRL_RECEIPT_WARE_SETTINGS s on s.WARE_ID=wa.ID where wa.ID=w;
  while w is not null loop
   depth_no:=depth_no+1;token:=RRL_STOCK_PLAN_HELPER.decimal_text(w);
   if depth_no>16 or instr(visited,'|'||token||'|')>0 then raise_application_error(-20886,'QUALITY_WAREHOUSE_HIERARCHY_INVALID');end if;
   visited:=visited||token||'|';
   for r in(select * from RRL_QC_SCOPE_RULE where WARE_ID=w and STORE_ADDR in('*',addr)
    and PLACE_CATEGORY in('ANY',category)
    order by case when STORE_ADDR=addr then 0 else 1 end,case when PLACE_CATEGORY=category then 0 else 1 end)loop
    stamp:=stamp||length(token)||':'||token||length(r.STORE_ADDR)||':'||r.STORE_ADDR||':'||r.PLACE_CATEGORY||':'||r.RULE_VERSION||':'||r.ACTIVE_FLAG||';';
    if selected_flag=0 and r.ACTIVE_FLAG=1 then
     selected_flag:=1;mode_name:=r.CONTROL_MODE;independent:=r.INDEPENDENT_FLAG;percent:=r.SAMPLE_PERCENT;
     ex_whole:=r.EXEMPT_WHOLE;ex_storage:=r.EXEMPT_STORAGE;
     j.put('rule_warehouse_id',r.WARE_ID);j.put('store_addr',r.STORE_ADDR);j.put('place_category',r.PLACE_CATEGORY);j.put('rule_version',r.RULE_VERSION);
    end if;
   end loop;
   select PARENT_WARE_ID into w from RRL_WARES where ID=w;
  end loop;
  if stamp is not null then select standard_hash(stamp,'SHA256') into digest from dual;j.put('policy_stamp',digest);end if;
  j.put('warehouse_id',origin_ware);j.put('mode',mode_name);j.put('independent',independent);j.put('sample_percent',percent);
  j.put('exempt_whole',ex_whole);j.put('exempt_storage',ex_storage);j.put('scoped_rule',selected_flag=1);return j.to_clob;
 end;
 function exemption_json(p_domain clob) return clob is
  d json_object_t:=json_object_t.parse(p_domain);p json_object_t:=json_object_t.parse(policy_json(p_domain));
  j json_object_t:=json_object_t();legs json_array_t:=d.get_array('legs');leg json_object_t;
  v_uid varchar2(200);v_qty number;epoch number;original_qty number;v_uom varchar2(20);op varchar2(100);state_name varchar2(30);
  current_qty number;receipt_json clob;receipt json_object_t;article varchar2(160);batch_no number;expiry date;produced date;birth_op varchar2(100);origin_uid varchar2(200);
  storage_task number;storage_op varchar2(100);storage_cell varchar2(60);selected_cell varchar2(60);
  storage_document number:=d.get_number('document_id');storage_customer number:=d.get_number('customer_order_id');
  storage_identifier varchar2(200):=d.get_string('pallet_identifier');bound_version number:=d.get_number('bound_stock_version');
  current_bound_version number:=d.get_number('bound_current_stock_version');
 begin
  j.put('eligible',false);j.put('reason','NO_APPLICABLE_WHOLE_PALLET_EXCEPTION');
  if p.get_number('exempt_whole')!=1 and p.get_number('exempt_storage')!=1 then return j.to_clob;end if;
  if d.get_number('case_task') is not null or legs.get_size!=1 then j.put('reason','COMPOSITE_OR_CASE_REQUIRES_CONTROL');return j.to_clob;end if;
  leg:=treat(legs.get(0) as json_object_t);v_uid:=leg.get_string('uid');v_qty:=RRL_STOCK_MATH.quantity(leg.get_string('quantity'));
  select STOCK_COMPOSITION_VERSION,ARTICUL,PROD_BATCH_ID,EXPIRY_DATE,PRODUCED_DATE,CREATED_BY_STOCK_OP,STOCK_ORIGIN_UID into epoch,article,batch_no,expiry,produced,birth_op,origin_uid from RRL_PALLETS where UID_PALLET=v_uid;
  -- A fresh native birth changes epoch 0 -> 1. Any later partial/change/restore advances it again.
  if epoch!=1 then j.put('reason','PALLET_CHANGED_OR_LEGACY_PROVENANCE_UNKNOWN');return j.to_clob;end if;
  select r.POSTED_BASE_QTY,r.STOCK_BASE_UOM,r.STOCK_OPERATION_ID,o.STATE,r.RESULT_JSON into original_qty,v_uom,op,state_name,receipt_json
   from RRL_SAP_PALLET_RECEIPT r join RRL_STOCK_OPERATION o on o.OPERATION_ID=r.STOCK_OPERATION_ID where r.UID_PALLET=v_uid;
  select nvl(sum(REMAIN),0) into current_qty from RRL_REMAINS where UID_POLETA=v_uid;
  receipt:=json_object_t.parse(receipt_json);
  if state_name!='APPLIED' or original_qty!=v_qty or current_qty!=v_qty or v_uom!=leg.get_string('base_uom')
   or nvl(article,chr(0))!=nvl(receipt.get_string('material'),chr(0))
   or batch_no is not null or nvl(birth_op,chr(0))!=op or nvl(origin_uid,chr(0))!=v_uid
   or nvl(to_char(expiry,'YYYY-MM-DD'),chr(0))!=nvl(receipt.get_string('expiry_date'),chr(0))
   or nvl(to_char(produced,'YYYY-MM-DD'),chr(0))!=nvl(receipt.get_string('produced_date'),chr(0))
   then j.put('reason','WHOLE_ORIGINAL_RECEIPT_NOT_PROVED');return j.to_clob;end if;
  if p.get_number('exempt_whole')!=1 then
   -- Storage barcode is the existing scanned full-pallet binding, never a label pattern.
   if d.get_string('bound_physical_uid')is null or d.get_string('bound_physical_uid')!=v_uid
    or d.get_number('customer_order_id')is null then
    j.put('reason','STORAGE_IDENTIFIER_BINDING_REQUIRED');return j.to_clob;
   end if;
   selected_cell:=leg.get_string('cell');
   begin
    select wh.TASK_ID,m.OPERATION_ID,m.FROM_CELL into storage_task,storage_op,storage_cell
     from RRL_CUSTOMER_ORDER_FULFILLMENT ff
     join RRL_WAREHOUSE_TASK wh on wh.TASK_ID=ff.PICKED_WAREHOUSE_TASK_ID
     join RRL_WAREHOUSE_TASK_STOCK_MOVE m on m.TASK_ID=wh.TASK_ID and m.OPERATION_ID=ff.PICKED_OPERATION_ID
     join RRL_STOCK_OPERATION stock_op on stock_op.OPERATION_ID=m.OPERATION_ID
     join RRL_REMAINS current_stock on current_stock.UID_POLETA=ff.PICKED_PALLET_UID and current_stock.CELL=m.TO_CELL
     where ff.LEGACY_SBORKA_PALLET_ID=storage_document
      and ff.PALLET_UID=storage_identifier and ff.CUSTOMER_ORDER_ID=storage_customer
      and ff.STATUS='PICKED' and ff.PICKED_PALLET_UID=v_uid and ff.PICKED_STOCK_VERSION=bound_version
      and wh.TASK_SOURCE='WAVE' and wh.TASK_TYPE='PICKING_MOVE' and wh.QTY_MODE='PALLET' and wh.STATUS='DONE'
      and stock_op.STATE='APPLIED' and stock_op.COMMAND_TYPE='TASK_COMPLETE'
      and m.UID_PALLET=v_uid and m.TARGET_UID_PALLET=v_uid and m.BASE_QTY=v_qty and m.BASE_UOM=v_uom
      and current_stock.STOCK_VERSION=current_bound_version
      and current_stock.REMAIN=v_qty and current_stock.BASE_UOM=v_uom and current_stock.CELL=selected_cell;
   exception when no_data_found or too_many_rows then
    j.put('reason','STORAGE_IDENTIFIER_BINDING_NOT_PROVED');return j.to_clob;
   end;
   j.put('exemption_basis','SCANNED_ORIGINAL_STORAGE_IDENTIFIER');j.put('storage_pick_task_id',storage_task);
   j.put('storage_pick_operation_id',storage_op);j.put('storage_source_cell',storage_cell);
  else j.put('exemption_basis','WHOLE_UNCHANGED_NATIVE_RECEIPT');end if;
  j.put('eligible',true);j.put('reason','WHOLE_NATIVE_RECEIPT_UNCHANGED');j.put('uid_pallet',v_uid);
  j.put('supplier_batch',receipt.get_string('supplier_batch'));j.put('receipt_operation_id',op);j.put('base_quantity',RRL_STOCK_PLAN_HELPER.decimal_text(v_qty));j.put('base_uom',v_uom);
  j.put('composition_epoch',epoch);j.put('policy',p);return j.to_clob;
 exception when no_data_found or too_many_rows then j.put('eligible',false);j.put('reason','ORIGINAL_RECEIPT_PROVENANCE_UNAVAILABLE');return j.to_clob;
 end;
 procedure record_exemption(p_domain clob,p_signature varchar2) is
  op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');d json_object_t:=json_object_t.parse(p_domain);
  proof json_object_t;payload clob;existing clob;document_no number:=d.get_number('document_id');
 begin
  if op is null then return;end if;
  proof:=json_object_t.parse(exemption_json(p_domain));if not proof.get_boolean('eligible') then return;end if;
  if proof.get_object('policy').get_string('mode') not in('ANY','WEIGHT','BOTH')then return;end if;
  proof.put('composition_signature',p_signature);proof.put('operation_id',op);proof.put('document_id',d.get_number('document_id'));payload:=proof.to_clob;
  begin select PAYLOAD_JSON into existing from RRL_QC_EXEMPT_FACT where OPERATION_ID=op and DOCUMENT_ID=document_no;
   if dbms_lob.compare(existing,payload)!=0 then raise_application_error(-20886,'QUALITY_EXEMPTION_PROOF_CONFLICT');end if;
  exception when no_data_found then insert into RRL_QC_EXEMPT_FACT(OPERATION_ID,DOCUMENT_ID,PAYLOAD_JSON) values(op,document_no,payload);end;
 end;
end;
/
