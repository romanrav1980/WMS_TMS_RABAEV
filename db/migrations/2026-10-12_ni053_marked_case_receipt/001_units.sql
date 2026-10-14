create or replace package body RRL_INTERWARE_UNIT_SOURCE as 
 procedure assert_scope(p_load varchar2,p_actor varchar2)is n number; 
 begin 
  select count(*)into n from RRL_TT_HU_LOAD_FACT lf join RUSERS u on u.ID=p_actor 
   where lf.LOAD_OPERATION_ID=p_load and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_edit')=1 and(upper(trim(u.USER_GROUP))='GLOBAL_ADMIN'or u.WARE_ID=lf.WARE_ID); 
  if n!=1 then raise_application_error(-20882,'INTERWARE_CURRENT_SOURCE_DISPATCHER_REQUIRED');end if; 
 end; 
 procedure assert_case_archive(p_load varchar2,p_tree json_object_t)is
 nodes clob:=p_tree.get_array('nodes').to_clob;cases number;n number;leafs number;
 begin
 select count(*)into cases from json_table(nodes,'$[*]'columns(NODE_KIND varchar2(20)path '$.kind'))where NODE_KIND='CASE';
 if cases=0 then return;end if;
 select count(*)into n from json_table(nodes,'$[*]'columns(
 NODE_KIND varchar2(20)path '$.kind',NODE_UID varchar2(160)path '$.uid',CASE_ID number path '$.case_task_id',CASE_SSCC varchar2(32)path '$.sscc',CASE_VERSION number path '$.version'))j
 join RRL_CASE_PICK_TASK t on t.CASE_PICK_TASK_ID=j.CASE_ID
 join RRL_TT_HU_LOAD_FACT lf on lf.LOAD_OPERATION_ID=p_load and lf.WARE_ID=t.WARE_ID
 where j.NODE_KIND='CASE'and j.NODE_UID='CASE:'||RRL_STOCK_PLAN_HELPER.decimal_text(t.CASE_PICK_TASK_ID)
 and t.STATUS='SHIPPED'and t.SHIPPED_OPERATION=p_load and t.SSCC=j.CASE_SSCC and t.CONTENT_VERSION=j.CASE_VERSION+1;
 if n!=cases then raise_application_error(-20884,'STORE_CASE_EXACT_FROZEN_SHIPMENT_REQUIRED');end if;
 select count(*)into leafs from json_table(nodes,'$[*]'columns(NODE_KIND varchar2(20)path '$.kind',CASE_ID number path '$.case_task_id'))where NODE_KIND='STOCK'and CASE_ID is not null;
 select count(*)into n from json_table(nodes,'$[*]'columns(NODE_KIND varchar2(20)path '$.kind',NODE_UID varchar2(160)path '$.uid',CASE_ID number path '$.case_task_id'))j
 join RRL_CASE_CARRIER_LOT c on c.CASE_PICK_TASK_ID=j.CASE_ID and c.LOT_UID=j.NODE_UID
 where j.NODE_KIND='STOCK'and exists(select 1 from json_table(nodes,'$[*]'columns(PARENT_KIND varchar2(20)path '$.kind',PARENT_CASE number path '$.case_task_id'))p where p.PARENT_KIND='CASE'and p.PARENT_CASE=j.CASE_ID);
 if n!=leafs or leafs<cases then raise_application_error(-20884,'STORE_CASE_EXACT_CARRIER_LOTS_REQUIRED');end if;
 end;
 function issued_manifest(p_load varchar2,p_uid varchar2,p_snapshot clob)return clob is 
  tree json_object_t:=json_object_t.parse(p_snapshot);node json_object_t;plain json_array_t:=json_array_t();units json_array_t:=json_array_t();x json_object_t;j json_object_t:=json_object_t();finger json_object_t:=json_object_t(); 
  wire clob;expected varchar2(64);actual varchar2(64);cell_value varchar2(60);uom_value varchar2(20);qty number;total number:=0;n number:=0;required_count number;proof_count number;nodes json_array_t;candidate json_object_t;stock_nodes number:=0;selected_nodes number:=0;archive_wire clob;archive_tree json_object_t;root_id varchar2(200); 
 begin 
  nodes:=tree.get_array('nodes');
  if nodes.get_size<1 or nodes.get_size>200 or tree.get_number('leaf_count')<1 or tree.get_number('top_place_count')!=1 then raise_application_error(-20886,'INTERWARE_SINGLE_PHYSICAL_ROOT_REQUIRED');end if;
  if nodes.get_size=1 then node:=treat(nodes.get(0)as json_object_t);
  else
   select lf.COMPOSITION_JSON,lf.ROOT_UID into archive_wire,root_id from RRL_TT_HU_LOAD_FACT lf
   join RRL_STOCK_OPERATION root_op on root_op.OPERATION_ID=lf.LOAD_OPERATION_ID and root_op.STATE='APPLIED'and root_op.COMMAND_TYPE in('HU_SHIP','LOAD_SHIPMENT')
   where lf.LOAD_OPERATION_ID=p_load and lf.STATUS in('LOADED','DEPARTED');
   archive_tree:=json_object_t.parse(archive_wire);
   if dbms_lob.compare(archive_tree.to_clob,tree.to_clob)!=0 or root_id!=tree.get_string('root')then raise_application_error(-20884,'INTERWARE_NESTED_FROZEN_LOAD_ARCHIVE_REQUIRED');end if;
   for i in 0..nodes.get_size-1 loop
    candidate:=treat(nodes.get(i)as json_object_t);
    if candidate.get_string('kind')='STOCK'then stock_nodes:=stock_nodes+1;if candidate.get_string('uid')=p_uid then node:=candidate;selected_nodes:=selected_nodes+1;end if;
    elsif candidate.get_string('kind')not in('CONTAINER','CASE')then raise_application_error(-20886,'INTERWARE_NESTED_STOCK_ONLY_REQUIRED');end if;
   end loop;
   if selected_nodes!=1 or stock_nodes!=tree.get_number('leaf_count')then raise_application_error(-20886,'INTERWARE_NESTED_ONE_STOCK_LEAF_REQUIRED');end if;
  end if;
assert_case_archive(p_load,tree);
cell_value:=tree.get_string('cell');uom_value:=node.get_string('base_uom');qty:=RRL_STOCK_MATH.quantity(node.get_string('quantity')); 
  if node.get_string('kind')!='STOCK'or node.get_string('uid')!=p_uid or cell_value is null or uom_value is null then raise_application_error(-20886,'INTERWARE_ORIGINAL_STOCK_SOURCE_REQUIRED');end if; 
  select count(*)into required_count from RRL_PALLETS p where p.UID_PALLET=p_uid and(exists(select 1 from RRL_SKU_RECEIPT_PROFILE profile where profile.ARTICUL=p.ARTICUL)or exists(select 1 from RRL_SKU_RECEIPT_POLICY policy where policy.ARTICUL=p.ARTICUL and(policy.MARKING_REQUIRED=1 or policy.SERIALIZED_WEIGHT_BOXES=1))or exists(select 1 from RRL_FINISHED_GOODS_SKU fg where fg.ARTICUL=p.ARTICUL and fg.CRPT_REQUIRED=1)); 
  for u in(select PHYSICAL_UNIT_KEY,BASE_QTY,BASE_UOM,CURRENT_CELL,UNIT_VERSION,STOCK_STATUS,HARD_RESERVATION_ID from RRL_WMS_RECEIPT_UNIT where CURRENT_UID=p_uid order by PHYSICAL_UNIT_KEY fetch first 10001 rows only)loop 
   n:=n+1;if n>10000 or u.PHYSICAL_UNIT_KEY is null or u.BASE_QTY<=0 or u.BASE_UOM is null or u.BASE_UOM!=uom_value or u.CURRENT_CELL is null or u.CURRENT_CELL!=cell_value or u.STOCK_STATUS!='ISSUED'or u.HARD_RESERVATION_ID is not null or u.UNIT_VERSION is null then raise_application_error(-20884,'INTERWARE_ORIGINAL_ISSUED_UNIT_SET_REQUIRED');end if; 
   x:=json_object_t();x.put('key',u.PHYSICAL_UNIT_KEY);x.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(u.BASE_QTY));x.put('base_uom',u.BASE_UOM);plain.append(x.clone());x.put('version',u.UNIT_VERSION);units.append(x);total:=total+u.BASE_QTY; 
  end loop; 
  if(tree.get_number('leaf_count')=1 and n!=nvl(tree.get_number('physical_unit_count'),0))or(n>0 and total!=qty)or(required_count>0 and n=0)then raise_application_error(-20884,'INTERWARE_EXACT_MARKED_SOURCE_QUANTITY_REQUIRED');end if; 
  if n>0 then 
   select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=p_load and STATE='APPLIED'; 
   select count(*),max(S)into proof_count,expected from json_table(wire,'$.physical_before[*]'columns(U varchar2(150)path '$.uid',S varchar2(64)path '$.unit_signature'))where U=p_uid; 
   if proof_count!=1 or expected is null then raise_application_error(-20884,'INTERWARE_ORIGINAL_UNIT_FINGERPRINT_REQUIRED');end if; 
   finger.put('units',plain);actual:=rawtohex(sys.dbms_crypto.hash(finger.to_clob,sys.dbms_crypto.hash_sh256)); 
   if actual!=expected then raise_application_error(-20884,'INTERWARE_ORIGINAL_UNIT_FINGERPRINT_CONFLICT');end if; 
   j.put('unit_signature',actual); 
  end if; 
  j.put('units',units);j.put('physical_unit_count',n);j.put('unit_capture_required',n>0);j.put('quantity',RRL_STOCK_PLAN_HELPER.decimal_text(qty));j.put('base_uom',uom_value);j.put('source_cell',cell_value);return j.to_clob; 
 end; 
 procedure capture_plan(p_plan varchar2,p_actor varchar2)is 
  plan RRL_INTERWARE_PLAN%rowtype;wire clob;signature_value varchar2(64);n number; 
 begin 
  RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6); 
  select *into plan from RRL_INTERWARE_PLAN where OPERATION_ID=p_plan; 
  assert_scope(plan.SOURCE_LOAD_OPERATION_ID,p_actor); 
  select count(*)into n from RRL_INTERWARE_UNIT_MANIFEST where PLAN_OPERATION_ID=p_plan; 
  if n>0 then return;end if; 
  select count(*)into n from RRL_INTERWARE_RECEIPT where PLAN_OPERATION_ID=p_plan; 
  if n>0 then raise_application_error(-20886,'INTERWARE_MANIFEST_CAPTURE_BEFORE_RECEIPT_REQUIRED');end if; 
  select count(*)into n from RRL_REMAINS where UID_POLETA=plan.ROOT_UID and(nvl(REMAIN,0)!=0 or nvl(HARD_RESERVED_BASE,0)!=0); 
  if n>0 then raise_application_error(-20886,'INTERWARE_SOURCE_STOCK_ALREADY_PRESENT');end if; 
  wire:=issued_manifest(plan.SOURCE_LOAD_OPERATION_ID,plan.ROOT_UID,plan.SOURCE_COMPOSITION_JSON); 
  if json_object_t.parse(wire).get_number('physical_unit_count')=0 then return;end if; 
  signature_value:=json_object_t.parse(wire).get_string('unit_signature'); 
  insert into RRL_INTERWARE_UNIT_MANIFEST(PLAN_OPERATION_ID,UNIT_SIGNATURE,MANIFEST_JSON,CREATED_BY)values(p_plan,signature_value,wire,p_actor); 
 end; 
 function plan_manifest(p_plan varchar2,p_actor varchar2)return clob is n number;wire clob; 
 begin 
  select count(*)into n from RRL_INTERWARE_PLAN p join RUSERS u on u.ID=p_actor where p.OPERATION_ID=p_plan and nvl(u.DELETED,0)=0 
   and(upper(trim(u.USER_GROUP))='GLOBAL_ADMIN'or(u.WARE_ID=p.SOURCE_WARE_ID and RRL_HAS_WRIGHT(u.ID,'transport_dispatch_view')=1)or(u.WARE_ID=p.TARGET_WARE_ID and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1)); 
  if n!=1 then raise_application_error(-20882,'INTERWARE_CURRENT_MANIFEST_READER_REQUIRED');end if; 
  begin select MANIFEST_JSON into wire from RRL_INTERWARE_UNIT_MANIFEST where PLAN_OPERATION_ID=p_plan; 
  exception when no_data_found then return '{"units":[],"physical_unit_count":0,"unit_capture_required":false}';end; 
  return wire; 
 end; 
end;

/
