from pathlib import Path
import json
folder=Path("db/migrations/2026-10-12_ni061_nested_receiving");out={}
def put(n,s):out[(folder/n).as_posix()]=s
put("001_columns.sql","""declare n number;begin
 select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_INTERWARE_PLAN'and COLUMN_NAME='SOURCE_PLACE_UID';
 if n=0 then execute immediate 'alter table RRL_INTERWARE_PLAN add(SOURCE_PLACE_UID varchar2(200),SOURCE_HU_JSON clob check(SOURCE_HU_JSON is json))';end if;
end;
/
""")
put("002_source.sql","""create or replace package RRL_IW_HU_SOURCE authid definer as
 function stock_uid(p_load varchar2)return varchar2;
 function context_json(p_load varchar2)return clob;
 procedure capture_context(p_load varchar2,p_actor varchar2,p_context out clob);
 procedure assert_context(p_load varchar2,p_context clob);
end;
/
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
 leaf_uid varchar2(200);n number;kind_value varchar2(80);
 begin
 leaf_uid:=stock_uid(p_load);select *into lf from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=p_load;
 tree:=json_object_t.parse(lf.COMPOSITION_JSON);nodes:=tree.get_array('nodes');
 if nodes.get_size=1 then return null;end if;
 select COMMAND_TYPE into kind_value from RRL_STOCK_OPERATION where OPERATION_ID=p_load and STATE='APPLIED';
 if kind_value!='HU_SHIP'or lf.ROOT_UID!=tree.get_string('root')then raise_application_error(-20886,'INTERWARE_FROZEN_NESTED_HU_LOAD_REQUIRED');end if;
 for i in 0..nodes.get_size-1 loop
 x:=treat(nodes.get(i)as json_object_t);
 if x.get_string('kind')='CONTAINER'then
 select *into pp from RRL_PALLETS where UID_PALLET=x.get_string('uid');
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
 select *into old_link from RRL_WMS_HU_LINK where HU_LINK_ID=x.get_number('id');
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
""")
put("003_receive_core.sql","""create or replace package RRL_IW_HU_REC_CORE authid definer accessible by(package RRL_STOCK_INTERWARE_REC)as
 procedure declare_rows(p_domain json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t);
 procedure restore(p_domain json_object_t,p_operation varchar2,p_actor varchar2);
end;
/
create or replace package body RRL_IW_HU_REC_CORE as
 procedure declare_rows(p_domain json_object_t,p_operation varchar2,p_resources in out nocopy json_array_t)is
 source_hu json_object_t;containers json_array_t;links json_array_t;x json_object_t;
 begin
 if not p_domain.has('nested_source')then return;end if;
 source_hu:=p_domain.get_object('nested_source');containers:=source_hu.get_array('containers');links:=source_hu.get_array('links');
 RRL_STOCK_PLAN_HELPER.anchor(p_resources,30,'HU',source_hu.get_string('stock_uid'));
 for i in 0..containers.get_size-1 loop x:=treat(containers.get(i)as json_object_t);
 RRL_STOCK_PLAN_HELPER.anchor(p_resources,30,'HU',x.get_string('uid'));RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_PALLETS',x.get_string('uid'));end loop;
 for i in 0..links.get_size-1 loop x:=treat(links.get(i)as json_object_t);
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('id')));
 RRL_STOCK_PLAN_HELPER.row_key(p_resources,'RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(x.get_number('new_id')));
 end loop;
 end;
 procedure restore(p_domain json_object_t,p_operation varchar2,p_actor varchar2)is
 source_hu json_object_t:=p_domain.get_object('nested_source');containers json_array_t:=source_hu.get_array('containers');links json_array_t:=source_hu.get_array('links');x json_object_t;
 v_uid varchar2(200);v_cell varchar2(60):=p_domain.get_string('receive_cell');v_load varchar2(100):=p_domain.get_string('source_load_operation_id');v_version number;
 v_parent varchar2(200);v_child varchar2(200);v_link number;
 begin
 for i in 0..containers.get_size-1 loop
 x:=treat(containers.get(i)as json_object_t);v_uid:=x.get_string('uid');v_version:=x.get_number('version');
 update RRL_PALLETS set HU_CURRENT_CELL=v_cell,HU_SHIPPED_OPERATION=null,HU_CONTENT_VERSION=HU_CONTENT_VERSION+1
 where UID_PALLET=v_uid and HU_KIND='CONTAINER'and HU_CURRENT_CELL is null and HU_SHIPPED_OPERATION=v_load and HU_CONTENT_VERSION=v_version;
 if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: receiving source container');end if;
 end loop;
 for i in 0..links.get_size-1 loop
 x:=treat(links.get(i)as json_object_t);v_parent:=x.get_string('parent');v_child:=x.get_string('child');v_link:=x.get_number('new_id');
 insert into RRL_WMS_HU_LINK(HU_LINK_ID,PARENT_UID,CHILD_PALLET_UID,ACTIVE_FLAG,LINK_VERSION,LINKED_OPERATION_ID,LINKED_BY)
 values(v_link,v_parent,v_child,1,0,p_operation,p_actor);
 end loop;
 end;
end;
/
""")
# Avoid JSON object member access in SQL expressions: extract values first.
p=folder/"002_source.sql";text=out[p.as_posix()]
text=text.replace("leaf_uid varchar2(200);n number;kind_value varchar2(80);","leaf_uid varchar2(200);n number;kind_value varchar2(80);v_uid varchar2(200);v_link_id number;")
text=text.replace("select *into pp from RRL_PALLETS where UID_PALLET=x.get_string('uid');","v_uid:=x.get_string('uid');select *into pp from RRL_PALLETS where UID_PALLET=v_uid;")
text=text.replace("select *into old_link from RRL_WMS_HU_LINK where HU_LINK_ID=x.get_number('id');","v_link_id:=x.get_number('id');select *into old_link from RRL_WMS_HU_LINK where HU_LINK_ID=v_link_id;")
out[p.as_posix()]=text
print(json.dumps(out))
