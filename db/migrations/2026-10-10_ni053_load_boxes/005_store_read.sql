create or replace package RRL_STOCK_STORE_RECEIPT_READ authid definer as
 procedure describe_load(p_load varchar2,p_actor varchar2,p_store varchar2,p_domain out clob);
 function preview_json(p_load varchar2,p_actor varchar2,p_store varchar2) return clob;
end;
/
create or replace package body RRL_STOCK_STORE_RECEIPT_READ as
 procedure require_receiver(p_actor varchar2,p_store varchar2) is n number;
 begin
  if RRL_HAS_WRIGHT(p_actor,'store_receipt_confirm')!=1 then raise_application_error(-20882,'STORE_RECEIPT_FORBIDDEN');end if;
  select count(*) into n from RUSERS where ID=p_actor and USER_GROUP='GLOBAL_ADMIN';
  if n=0 then
   select count(*) into n from RRL_STORE_RECEIPT_USER where USER_ID=p_actor and STORE_ADDR=p_store;
   if n!=1 then raise_application_error(-20882,'STORE_RECEIVER_ADDRESS_BINDING_REQUIRED');end if;
  end if;
 end;
 procedure describe_load(p_load varchar2,p_actor varchar2,p_store varchar2,p_domain out clob) is
  lf RRL_TT_HU_LOAD_FACT%rowtype;policy RRL_STORE_RECEIPT_POLICY%rowtype;n number;members number;
  tree json_object_t;j json_object_t:=json_object_t();root_node json_object_t;nodes clob;ids json_array_t:=json_array_t();physical_boxes json_array_t:=json_array_t();box_json json_object_t;min_box_kg number;box_no number:=0;
 begin
  require_receiver(p_actor,p_store);
  select * into policy from RRL_STORE_RECEIPT_POLICY where STORE_ADDR=p_store;
  select * into lf from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=p_load;
  if lf.STATUS!='DEPARTED' or lf.DEPARTURE_OPERATION_ID is null then raise_application_error(-20886,'STORE_RECEIPT_ACTUAL_DEPARTURE_REQUIRED');end if;
  select count(*) into n from RRL_STOCK_OPERATION where OPERATION_ID=lf.LOAD_OPERATION_ID and STATE='APPLIED';
  if n!=1 then raise_application_error(-20886,'STORE_RECEIPT_COMMITTED_LOAD_REQUIRED');end if;
  select count(*) into n from RRL_STOCK_OPERATION where OPERATION_ID=lf.DEPARTURE_OPERATION_ID and STATE='APPLIED';
  if n!=1 then raise_application_error(-20886,'STORE_RECEIPT_COMMITTED_DEPARTURE_REQUIRED');end if;
  select count(*),sum(case when DESTINATION_ADDR=p_store then 1 else 0 end) into members,n
   from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=p_load and ACTIVE_FLAG=1;
  if members<1 or members>200 or n is null or n!=members then raise_application_error(-20886,'STORE_RECEIPT_FROZEN_SINGLE_DESTINATION_REQUIRED');end if;
  tree:=json_object_t.parse(lf.COMPOSITION_JSON);root_node:=treat(tree.get_array('nodes').get(0) as json_object_t);
  if tree.get_array('nodes').get_size>200 then raise_application_error(-20881,'STORE_RECEIPT_NODE_BOUND_200');end if;
  nodes:=tree.get_array('nodes').to_clob;
  select count(*) into n from json_table(nodes,'$[*]' columns(KIND_NAME varchar2(20) path '$.kind',ARTICLE varchar2(160) path '$.article')) x
   where x.KIND_NAME='STOCK' and(exists(select 1 from RRL_SKU_RECEIPT_PROFILE p where p.ARTICUL=x.ARTICLE)
    or exists(select 1 from RRL_SKU_RECEIPT_POLICY p where p.ARTICUL=x.ARTICLE and p.MARKING_REQUIRED=1));
  j.put('requires_marked_recipient_flow',n>0 or nvl(tree.get_number('physical_unit_count'),1)>0);
  j.put('load_operation_id',p_load);j.put('trip_id',lf.TT_ID);j.put('store_address',p_store);
  j.put('root',tree.get_string('root'));j.put('root_scan_identifier',case when root_node.get_string('kind')='CASE' then root_node.get_string('sscc') else tree.get_string('root') end);
  j.put('root_sscc',root_node.get_string('sscc'));j.put('policy_version',policy.POLICY_VERSION);j.put('mode',policy.RECEIPT_MODE);
  j.put('snapshot',tree);j.put('composition_signature',rawtohex(sys.dbms_crypto.hash(tree.to_clob,sys.dbms_crypto.hash_sh256)));
  j.put('shipping_gross_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(lf.GROSS_WEIGHT_KG));
  select count(*) into n from RRL_STORE_RECEIPT_FACT where LOAD_OPERATION_ID=p_load;j.put('already_received',n>0);
  for r in(select SBORKA_PALLET_ID from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=p_load and ACTIVE_FLAG=1 order by SBORKA_PALLET_ID)loop ids.append(r.SBORKA_PALLET_ID);end loop;j.put('st_ids',ids);
  for box in(select BOX_UID,BOX_CONTENT_VERSION,GROSS_WEIGHT_KG,MEASUREMENT_ORIGIN,MEASUREMENT_REF,RECORDED_BY from RRL_TT_LOAD_BOX_WEIGHT where LOAD_OPERATION_ID=p_load order by BOX_UID fetch first 201 rows only)loop
   box_no:=box_no+1;if box_no>200 then raise_application_error(-20881,'STORE_PHYSICAL_BOX_BOUND_200');end if;
   if min_box_kg is null then min_box_kg:=box.GROSS_WEIGHT_KG;else min_box_kg:=least(min_box_kg,box.GROSS_WEIGHT_KG);end if;
   box_json:=json_object_t();box_json.put('box_uid',box.BOX_UID);box_json.put('content_version',box.BOX_CONTENT_VERSION);box_json.put('gross_weight_kg',RRL_STOCK_PLAN_HELPER.decimal_text(box.GROSS_WEIGHT_KG));
   box_json.put('origin',box.MEASUREMENT_ORIGIN);box_json.put('measurement_ref',box.MEASUREMENT_REF);box_json.put('recorded_by',box.RECORDED_BY);physical_boxes.append(box_json);
  end loop;
  j.put('physical_boxes',physical_boxes);j.put('shipping_weight_tolerance_kg',RRL_STOCK_PLAN_HELPER.decimal_text(min_box_kg/2));
  p_domain:=j.to_clob;
 exception when no_data_found then raise_application_error(-20886,'STORE_RECEIPT_LOAD_OR_EXPLICIT_POLICY_NOT_FOUND');
 end;
 function preview_json(p_load varchar2,p_actor varchar2,p_store varchar2) return clob is result clob;
 begin describe_load(p_load,p_actor,p_store,result);return result;end;
end;
/
