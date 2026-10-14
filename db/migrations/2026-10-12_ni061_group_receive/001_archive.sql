create or replace package RRL_IW_GROUP_ARCHIVE authid definer accessible by(package RRL_IW_GROUP_SOURCE,package RRL_IW_GROUP_REC)as
 function snapshot_json(p_load varchar2)return clob;
end;
/
create or replace package body RRL_IW_GROUP_ARCHIVE as
 function snapshot_json(p_load varchar2)return clob is
 lf RRL_TT_HU_LOAD_FACT%rowtype;wire clob;tree json_object_t;domain_value json_object_t;
 nodes json_array_t;shipments json_array_t;lots json_array_t:=json_array_t();links json_array_t;
 item json_object_t;part json_object_t;leg json_object_t;node json_object_t;entry json_object_t;
 result_value json_object_t:=json_object_t();manifest json_object_t;profile_wire clob;n number;st number;
 type seen_set is table of boolean index by varchar2(200);seen_lots seen_set;seen_st seen_set;leaf_count number:=0;
 v_uid varchar2(200);v_article varchar2(160);v_uom varchar2(20);v_qty number;v_version number;v_link number;v_parent varchar2(200);v_child varchar2(200);
 begin
 select *into lf from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=p_load and STATUS='DEPARTED'and ROOT_CASE_TASK_ID is null;
 select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=p_load and STATE='APPLIED'and COMMAND_TYPE='HU_SHIP';
 tree:=json_object_t.parse(lf.COMPOSITION_JSON);nodes:=tree.get_array('nodes');domain_value:=json_object_t.parse(wire).get_object('domain');shipments:=domain_value.get_array('shipments');
 if nodes.get_size<3 or nodes.get_size>200 or tree.get_number('top_place_count')!=1 or tree.get_string('root')!=lf.ROOT_UID or shipments.get_size<2 or shipments.get_size>200 then raise_application_error(-20886,'INTERWARE_GROUP_BOUNDED_TOP_REQUIRED');end if;
 for i in 0..nodes.get_size-1 loop
  node:=treat(nodes.get(i)as json_object_t);v_uid:=node.get_string('uid');v_version:=node.get_number('version');
  if node.get_string('kind')='STOCK'then
   if node.get_number('case_task_id')is not null or seen_lots.exists(node.get_string('uid'))then raise_application_error(-20886,'INTERWARE_GROUP_DISTINCT_STOCK_ONLY');end if;
   seen_lots(node.get_string('uid')):=true;leaf_count:=leaf_count+1;
  elsif node.get_string('kind')='CONTAINER'then
   select count(*)into n from RRL_PALLETS where UID_PALLET=v_uid and HU_KIND='CONTAINER'and HU_CURRENT_CELL is null and HU_SHIPPED_OPERATION=p_load and HU_CONTENT_VERSION=v_version+1;
   if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_CONTAINER_EPOCH_CHANGED');end if;
  else raise_application_error(-20886,'INTERWARE_GROUP_STOCK_CONTAINER_ONLY');end if;
 end loop;
 if leaf_count!=shipments.get_size or leaf_count!=tree.get_number('leaf_count')then raise_application_error(-20886,'INTERWARE_GROUP_ONE_ST_PER_LEAF_REQUIRED');end if;
 links:=tree.get_array('links');
 if links.get_size!=nodes.get_size-1 then raise_application_error(-20886,'INTERWARE_GROUP_COMPLETE_TREE_REQUIRED');end if;
 for i in 0..links.get_size-1 loop
  item:=treat(links.get(i)as json_object_t);v_link:=item.get_number('id');v_parent:=item.get_string('parent');v_child:=item.get_string('child');v_version:=item.get_number('version');
  select count(*)into n from RRL_WMS_HU_LINK where HU_LINK_ID=v_link and PARENT_UID=v_parent and CHILD_PALLET_UID=v_child and CHILD_CASE_TASK_ID is null and ACTIVE_FLAG=0 and UNLINKED_OPERATION_ID=p_load and LINK_VERSION=v_version+1;
  if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_FROZEN_LINK_CHANGED');end if;
 end loop;
 select count(*)into n from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=p_load and ACTIVE_FLAG=1;
 if n!=shipments.get_size then raise_application_error(-20886,'INTERWARE_GROUP_MEMBER_COUNT_CHANGED');end if;
 for i in 0..shipments.get_size-1 loop
  part:=treat(shipments.get(i)as json_object_t).get_object('domain');st:=part.get_number('document_id');
  if part.get_array('legs').get_size!=1 or part.get_number('return_supplier_id')is not null or part.has('interwarehouse_onward_source')or seen_st.exists(to_char(st))then raise_application_error(-20886,'INTERWARE_GROUP_FIRST_CUSTOMER_LEG_REQUIRED');end if;
  seen_st(to_char(st)):=true;leg:=treat(part.get_array('legs').get(0)as json_object_t);
 v_uid:=leg.get_string('uid');v_article:=leg.get_string('article');v_uom:=leg.get_string('base_uom');v_qty:=RRL_STOCK_MATH.quantity(leg.get_string('quantity'));
  if not seen_lots.exists(leg.get_string('uid'))then raise_application_error(-20886,'INTERWARE_GROUP_FOREIGN_LEAF');end if;
  seen_lots.delete(leg.get_string('uid'));
  select count(*)into n from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=p_load and ACTIVE_FLAG=1 and SBORKA_PALLET_ID=st;
  if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_EXACT_MEMBER_REQUIRED');end if;
  select count(*)into n from json_table(lf.COMPOSITION_JSON,'$.nodes[*]'columns(NODE_KIND varchar2(20)path '$.kind',NODE_UID varchar2(200)path '$.uid',ARTICLE_VALUE varchar2(160)path '$.article',QTY_VALUE varchar2(60)path '$.quantity',UOM_VALUE varchar2(20)path '$.base_uom'))j
  where NODE_KIND='STOCK'and NODE_UID=v_uid and ARTICLE_VALUE=v_article and UOM_VALUE=v_uom and RRL_STOCK_MATH.quantity(QTY_VALUE)=v_qty;
  if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_EXACT_WHOLE_LEAF_REQUIRED');end if;
  select count(*)into n from RRL_REMAINS where UID_POLETA=v_uid and(nvl(REMAIN,0)!=0 or nvl(HARD_RESERVED_BASE,0)!=0);
  if n!=0 then raise_application_error(-20886,'INTERWARE_GROUP_SOURCE_ALREADY_PRESENT');end if;
  manifest:=json_object_t.parse(RRL_INTERWARE_UNIT_SOURCE.issued_manifest(p_load,leg.get_string('uid'),lf.COMPOSITION_JSON));
  select json_arrayagg(json_object('system_code'value SYSTEM_CODE,'profile_code'value PROFILE_CODE,'profile_version'value PROFILE_VERSION,'scan_mode'value SCAN_MODE)order by SYSTEM_CODE,PROFILE_CODE returning clob)
   into profile_wire from RRL_SKU_RECEIPT_PROFILE where ARTICUL=v_article;
  entry:=leg.clone();entry.put('st_id',st);entry.put('issued_manifest',manifest);entry.put('profiles',json_array_t.parse(nvl(profile_wire,'[]')));lots.append(entry);
 end loop;
 if seen_lots.count!=0 then raise_application_error(-20886,'INTERWARE_GROUP_UNBOUND_LEAF');end if;
 select count(*)into n from RRL_STORE_RECEIPT_FACT where LOAD_OPERATION_ID=p_load;
 if n!=0 then raise_application_error(-20886,'INTERWARE_GROUP_ALREADY_ACCEPTED_BY_STORE');end if;
 select count(*)into n from RRL_INTERWARE_PLAN where SOURCE_LOAD_OPERATION_ID=p_load;
 if n!=0 then raise_application_error(-20886,'INTERWARE_GROUP_SCALAR_PLAN_EXISTS');end if;
 result_value.put('source_load_operation_id',p_load);result_value.put('source_trip_id',lf.TT_ID);result_value.put('source_warehouse_id',lf.WARE_ID);
 result_value.put('physical_place_identifier',lf.ROOT_UID);result_value.put('source_composition',tree);result_value.put('lots',lots);result_value.put('stock_leaf_count',leaf_count);
 return result_value.to_clob;
 exception when no_data_found then raise_application_error(-20886,'INTERWARE_GROUP_DEPARTED_ARCHIVE_REQUIRED');
 end;
end;
/
create or replace package body RRL_IW_GROUP_SOURCE as
 function source_json(p_load varchar2,p_actor varchar2)return clob is
 begin RRL_INTERWARE_UNIT_SOURCE.assert_scope(p_load,p_actor);return RRL_IW_GROUP_ARCHIVE.snapshot_json(p_load);end;
end;
/
