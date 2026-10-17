create or replace package body RRL_IW_HU_SOURCE as
 function stock_uid(p_load varchar2)return varchar2 is
 wire clob;tree json_object_t;nodes json_array_t;x json_object_t;result_uid varchar2(200);n number:=0;
 begin
 select COMPOSITION_JSON into wire from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=p_load and STATUS='DEPARTED'and ROOT_CASE_TASK_ID is null;
 tree:=json_object_t.parse(wire);nodes:=tree.get_array('nodes');
 if nodes.get_size<1 or nodes.get_size>200 or tree.get_number('leaf_count')!=1 or tree.get_number('top_place_count')!=1 then raise_application_error(-20886,'INTERWARE_ONE_STOCK_LEAF_SOURCE_REQUIRED');end if;
 for i in 0..nodes.get_size-1 loop
 x:=treat(nodes.get(i)as json_object_t);
 if x.get_string('kind')='STOCK'then result_uid:=x.get_string('uid');n:=n+1;
 elsif x.get_string('kind')!='CONTAINER'then raise_application_error(-20886,'INTERWARE_STOCK_CONTAINER_ONLY_SOURCE');end if;
 end loop;
 if n!=1 or result_uid is null then raise_application_error(-20886,'INTERWARE_ONE_STOCK_LEAF_SOURCE_REQUIRED');end if;
 return result_uid;
 end;
 function context_json(p_load varchar2)return clob is
 lf RRL_TT_HU_LOAD_FACT%rowtype;tree json_object_t;nodes json_array_t;links json_array_t;containers json_array_t:=json_array_t();context_links json_array_t:=json_array_t();
 x json_object_t;item json_object_t;result_value json_object_t:=json_object_t();pp RRL_PALLETS%rowtype;old_link RRL_WMS_HU_LINK%rowtype;
 leaf_uid varchar2(200);n number;kind_value varchar2(80);v_uid varchar2(200);v_link_id number;
 begin
 leaf_uid:=stock_uid(p_load);select *into lf from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=p_load;
 tree:=json_object_t.parse(lf.COMPOSITION_JSON);nodes:=tree.get_array('nodes');
 if nodes.get_size=1 then return null;end if;
 select COMMAND_TYPE into kind_value from RRL_STOCK_OPERATION where OPERATION_ID=p_load and STATE='APPLIED';
 if kind_value!='HU_SHIP'or lf.ROOT_UID!=tree.get_string('root')then raise_application_error(-20886,'INTERWARE_FROZEN_NESTED_HU_LOAD_REQUIRED');end if;
 for i in 0..nodes.get_size-1 loop
 x:=treat(nodes.get(i)as json_object_t);
 if x.get_string('kind')='CONTAINER'then
 v_uid:=x.get_string('uid');select *into pp from RRL_PALLETS where UID_PALLET=v_uid;
 if pp.HU_KIND!='CONTAINER'or pp.HU_SHIPPED_OPERATION!=p_load or pp.HU_CURRENT_CELL is not null or pp.HU_CONTENT_VERSION!=x.get_number('version')+1 then raise_application_error(-20886,'INTERWARE_NESTED_CONTAINER_EPOCH_CHANGED');end if;
 select count(*)into n from RRL_TARE_BOOK where PLACE_KIND='HU'and PLACE_ID=pp.UID_PALLET and STATUS='HELD';
 if n!=0 then raise_application_error(-20886,'INTERWARE_NESTED_RETAINED_TARE_CUSTODY_REQUIRED');end if;
 item:=json_object_t();item.put('uid',pp.UID_PALLET);item.put('version',pp.HU_CONTENT_VERSION);item.put('type',pp.HU_TYPE);item.put('tare',RRL_STOCK_PLAN_HELPER.decimal_text(pp.HU_TARE_WEIGHT_KG));containers.append(item);
 end if;
 end loop;
 links:=tree.get_array('links');
 if links.get_size!=nodes.get_size-1 then raise_application_error(-20886,'INTERWARE_NESTED_COMPLETE_TREE_REQUIRED');end if;
 for i in 0..links.get_size-1 loop
 x:=treat(links.get(i)as json_object_t);
 v_link_id:=x.get_number('id');select *into old_link from RRL_WMS_HU_LINK where HU_LINK_ID=v_link_id;
 if old_link.ACTIVE_FLAG!=0 or old_link.UNLINKED_OPERATION_ID!=p_load or old_link.PARENT_UID!=x.get_string('parent')or old_link.CHILD_PALLET_UID!=x.get_string('child')or old_link.CHILD_CASE_TASK_ID is not null or old_link.LINK_VERSION!=x.get_number('version')+1 then raise_application_error(-20886,'INTERWARE_NESTED_FROZEN_LINK_CHANGED');end if;
 item:=x.clone();item.put('version',old_link.LINK_VERSION);context_links.append(item);
 end loop;
 result_value.put('source_load_operation_id',p_load);result_value.put('place_uid',lf.ROOT_UID);result_value.put('stock_uid',leaf_uid);result_value.put('containers',containers);result_value.put('links',context_links);
 return result_value.to_clob;
 end;
 procedure capture_context(p_load varchar2,p_actor varchar2,p_context out clob)is
 wire clob;value json_object_t;links json_array_t;x json_object_t;new_id number;
 begin
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 RRL_INTERWARE_UNIT_SOURCE.assert_scope(p_load,p_actor);
 wire:=context_json(p_load);if wire is null then p_context:=null;return;end if;
 value:=json_object_t.parse(wire);links:=value.get_array('links');
 for i in 0..links.get_size-1 loop x:=treat(links.get(i)as json_object_t);select RRL_WMS_HU_LINK_SQ.nextval into new_id from dual;x.put('new_id',new_id);links.put(i,x,true);end loop;
 value.put('links',links);p_context:=value.to_clob;
 end;
 procedure assert_context(p_load varchar2,p_context clob)is
 actual clob:=context_json(p_load);value json_object_t;links json_array_t;x json_object_t;new_id number;n number;
 type id_map is table of number index by varchar2(80);seen id_map;key_value varchar2(80);
 begin
 if actual is null and p_context is null then return;end if;
 if actual is null or p_context is null then raise_application_error(-20886,'INTERWARE_NESTED_CONTEXT_REQUIRED');end if;
 value:=json_object_t.parse(p_context);links:=value.get_array('links');
 for i in 0..links.get_size-1 loop
 x:=treat(links.get(i)as json_object_t);new_id:=x.get_number('new_id');
 if new_id is null or new_id<1 or new_id!=trunc(new_id)then raise_application_error(-20886,'INTERWARE_NESTED_RESERVED_LINK_ID_REQUIRED');end if;
 key_value:=RRL_STOCK_PLAN_HELPER.decimal_text(new_id);
 if seen.exists(key_value)then raise_application_error(-20886,'INTERWARE_NESTED_DUPLICATE_NEW_LINK');end if;seen(key_value):=1;
 select count(*)into n from RRL_WMS_HU_LINK where HU_LINK_ID=new_id;if n!=0 then raise_application_error(-20886,'INTERWARE_NESTED_LINK_ID_ALREADY_USED');end if;
 x.remove('new_id');links.put(i,x,true);
 end loop;
 value.put('links',links);
 if dbms_lob.compare(actual,value.to_clob)!=0 then raise_application_error(-20886,'INTERWARE_NESTED_FROZEN_CONTEXT_CHANGED');end if;
 end;
end;
/
