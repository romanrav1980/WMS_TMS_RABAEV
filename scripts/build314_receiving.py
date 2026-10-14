from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni061_nested_receiving");out={}
def before(name):return "\n".join(line.rstrip()for line in(d/("000_before_"+name.lower()+".sql")).read_text(encoding="utf-8").splitlines())+"\n"
def put(n,s):out[(d/n).as_posix()]=s
s=before("RRL_INTERWARE_PLAN_GUARD")
s=s.replace("join RRL_PALLETS p on p.UID_PALLET=f.ROOT_UID","join RRL_PALLETS p on p.UID_PALLET=:new.ROOT_UID",1)
s=s.replace("and f.ROOT_UID=:new.ROOT_UID","and f.ROOT_UID=nvl(:new.SOURCE_PLACE_UID,:new.ROOT_UID)",1)
needle=" if n!=1 then raise_application_error(-20886,'INTERWARE_EXACT_EXISTING_SINGLE_LOAD_REQUIRED');end if;"
s=s.replace(needle,needle+"""
 if :new.ROOT_UID!=RRL_IW_HU_SOURCE.stock_uid(:new.SOURCE_LOAD_OPERATION_ID)then raise_application_error(-20886,'INTERWARE_FROZEN_STOCK_LEAF_REQUIRED');end if;
 RRL_IW_HU_SOURCE.assert_context(:new.SOURCE_LOAD_OPERATION_ID,:new.SOURCE_HU_JSON);
 if (:new.SOURCE_HU_JSON is null and :new.SOURCE_PLACE_UID is not null)or(:new.SOURCE_HU_JSON is not null and(:new.SOURCE_PLACE_UID is null or :new.SOURCE_PLACE_UID=:new.ROOT_UID))then raise_application_error(-20886,'INTERWARE_PHYSICAL_PLACE_STOCK_KEYS_REQUIRED');end if;
""",1);put("004_plan_guard.sql",s)
s=before("RRL_STOCK_INTERWARE_REC")
old=" if nodes.get_size!=1 then raise_application_error(-20886,'INTERWARE_SINGLE_STOCK_NODE_REQUIRED');end if;\n leaf:=treat(nodes.get(0)as json_object_t);"
assert old in s
replacement=""" if nodes.get_size<1 or nodes.get_size>200 then raise_application_error(-20886,'INTERWARE_STOCK_NODE_BOUND');end if;
 leaf:=null;
 for i in 0..nodes.get_size-1 loop
  declare candidate json_object_t:=treat(nodes.get(i)as json_object_t);begin
   if candidate.get_string('kind')='STOCK'then
    if leaf is not null then raise_application_error(-20886,'INTERWARE_ONE_STOCK_NODE_REQUIRED');end if;leaf:=candidate;
   elsif candidate.get_string('kind')!='CONTAINER'then raise_application_error(-20886,'INTERWARE_STOCK_CONTAINER_ONLY');end if;
  end;
 end loop;
 if leaf is null then raise_application_error(-20886,'INTERWARE_STOCK_NODE_REQUIRED');end if;
 RRL_IW_HU_SOURCE.assert_context(plan.SOURCE_LOAD_OPERATION_ID,plan.SOURCE_HU_JSON);
"""
s=s.replace(old,replacement,1)
s=s.replace("m.get_string('scan_pallet')!=plan.ROOT_UID","m.get_string('scan_pallet')!=nvl(plan.SOURCE_PLACE_UID,plan.ROOT_UID)",1)
needle=" if source_units.get_number('physical_unit_count')>0 then\n  p_domain.put('source_units'"
assert needle in s
s=s.replace(needle," if plan.SOURCE_HU_JSON is not null then p_domain.put('nested_source',json_object_t.parse(plan.SOURCE_HU_JSON));end if;\n"+needle,1)
s=s.replace(" if m.get_boolean('partial_receipt')then"," if m.get_boolean('partial_receipt')then\n  if plan.SOURCE_HU_JSON is not null then raise_application_error(-20886,'INTERWARE_NESTED_WHOLE_RECEIPT_REQUIRED');end if;",1)
needle=" describe_source(p_request,d.get_string('actor'),v);";assert needle in s
s=s.replace(needle,needle+"\n RRL_IW_HU_REC_CORE.declare_rows(v,p_operation,r);",1)
needle="  v_original_root:=v.get_string('original_root_uid');";assert needle in s
s=s.replace(needle,"""  if v.has('nested_source')then
   RRL_IW_HU_REC_CORE.restore(v,op,p_actor);
   j.put('physical_place_identifier',v.get_object('nested_source').get_string('place_uid'));
   j.put('physical_tree_restored',true);j.put('physical_place_count',1);
  end if;
"""+needle,1)
put("005_receiving.sql",s)
# Guard container changes using frozen native resolved source and held original identities.
s=before("RRL_HU_CONTAINER_GUARD")
s=s.replace("'HU_REPACK_SLOT','UNLOAD_SHIPMENT')","'HU_REPACK_SLOT','UNLOAD_SHIPMENT','INTERWARE_RECEIVE')",1)
needle=" if v_kind='UNLOAD_SHIPMENT'then";assert needle in s
extra=""" if v_kind='INTERWARE_RECEIVE'then
 if not updating then raise_application_error(-20863,'INTERWARE_EXISTING_CONTAINER_ONLY');end if;
 declare wire clob;n number;state_name varchar2(20);cell_text varchar2(60);load_id varchar2(100);begin
 select STATE,RESOLVED_PLAN_JSON into state_name,wire from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
 cell_text:=json_object_t.parse(wire).get_object('domain').get_string('receive_cell');load_id:=json_object_t.parse(wire).get_object('domain').get_string('source_load_operation_id');
 select count(*)into n from json_table(wire,'$.domain.nested_source.containers[*]'columns(U varchar2(200)path '$.uid',V number path '$.version',T varchar2(20)path '$.type',W varchar2(60)path '$.tare'))frozen
 where frozen.U=:new.UID_PALLET and frozen.V=:old.HU_CONTENT_VERSION and frozen.T=:old.HU_TYPE and frozen.W=RRL_STOCK_PLAN_HELPER.decimal_text(:old.HU_TARE_WEIGHT_KG);
 if state_name!='IN_FLIGHT'or n!=1 or :old.HU_SHIPPED_OPERATION!=load_id or :old.HU_CURRENT_CELL is not null or :new.HU_SHIPPED_OPERATION is not null or :new.HU_CURRENT_CELL!=cell_text or nvl(:new.HU_TYPE,'~')!=nvl(:old.HU_TYPE,'~')or nvl(:new.HU_TARE_WEIGHT_KG,-1)!=nvl(:old.HU_TARE_WEIGHT_KG,-1)then raise_application_error(-20863,'INTERWARE_FROZEN_CONTAINER_RECEIPT_REQUIRED');end if;
 end;
 end if;
"""
s=s.replace(needle,extra+needle,1);put("006_container_guard.sql",s)
s=before("RRL_HU_LINK_WRITE_GUARD");s=s.replace("'HU_REPACK_SLOT','UNLOAD_SHIPMENT')","'HU_REPACK_SLOT','UNLOAD_SHIPMENT','INTERWARE_RECEIVE')",1)
needle=" if v_kind='UNLOAD_SHIPMENT'then";assert needle in s
s=s.replace(needle,""" if v_kind='INTERWARE_RECEIVE'then
 if not inserting or :new.CHILD_CASE_TASK_ID is not null then raise_application_error(-20863,'INTERWARE_APPEND_SOURCE_LINK_ONLY');end if;
 declare wire clob;state_name varchar2(20);n number;begin
 select RESOLVED_PLAN_JSON,STATE into wire,state_name from RRL_STOCK_OPERATION where OPERATION_ID=v_op;
 select count(*)into n from json_table(wire,'$.domain.nested_source.links[*]'columns(
 N number path '$.new_id',P varchar2(200)path '$.parent',C varchar2(200)path '$.child'))frozen
 where frozen.N=:new.HU_LINK_ID and frozen.P=:new.PARENT_UID and frozen.C=:new.CHILD_PALLET_UID;
 if state_name!='IN_FLIGHT'or n!=1 then raise_application_error(-20863,'INTERWARE_FROZEN_LINK_RECEIPT_REQUIRED');end if;
 end;
 end if;
"""+needle,1);put("007_link_guard.sql",s)
s=before("RRL_HU_DEPARTURE_GUARD");needle="  if kind='UNLOAD_SHIPMENT'then";assert needle in s
s=s.replace(needle,"""  if kind='INTERWARE_RECEIVE'then
   if not updating or :old.HU_SHIPPED_OPERATION is null or :new.HU_SHIPPED_OPERATION is not null or :new.HU_CURRENT_CELL is null or :new.HU_KIND!='CONTAINER'then raise_application_error(-20863,'INTERWARE_EXISTING_CONTAINER_RECEIPT_ONLY');end if;
   declare wire clob;n number;load_id varchar2(100);state_name varchar2(20);cell_text varchar2(60);begin
    select STATE,RESOLVED_PLAN_JSON into state_name,wire from RRL_STOCK_OPERATION where OPERATION_ID=op;
    load_id:=json_object_t.parse(wire).get_object('domain').get_string('source_load_operation_id');cell_text:=json_object_t.parse(wire).get_object('domain').get_string('receive_cell');
    select count(*)into n from json_table(wire,'$.domain.nested_source.containers[*]'columns(U varchar2(200)path '$.uid',V number path '$.version'))frozen where frozen.U=:new.UID_PALLET and frozen.V=:old.HU_CONTENT_VERSION;
    if state_name!='IN_FLIGHT'or n!=1 or load_id!=:old.HU_SHIPPED_OPERATION or cell_text!=:new.HU_CURRENT_CELL or :new.HU_CONTENT_VERSION!=:old.HU_CONTENT_VERSION+1 then raise_application_error(-20863,'INTERWARE_CONTAINER_ORIGINAL_LOAD_REQUIRED');end if;
   end;
   RRL_STOCK_LOCK_API.assert_held(30,RRL_STOCK_LOCK_API.resource_key('HU',:new.UID_PALLET));return;
  end if;
"""+needle,1);put("008_departure_guard.sql",s)
put("009_recompile.sql","""declare n number;begin
 for attempt in 1..5 loop
 for item in(select OBJECT_NAME,OBJECT_TYPE from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%'and OBJECT_TYPE in('PACKAGE','PACKAGE BODY','TRIGGER','FUNCTION','PROCEDURE','VIEW'))loop
 begin
 if item.OBJECT_TYPE='PACKAGE BODY'then execute immediate 'alter package '||dbms_assert.simple_sql_name(item.OBJECT_NAME)||' compile body';
 elsif item.OBJECT_TYPE='PACKAGE'then execute immediate 'alter package '||dbms_assert.simple_sql_name(item.OBJECT_NAME)||' compile specification';
 else execute immediate 'alter '||item.OBJECT_TYPE||' '||dbms_assert.simple_sql_name(item.OBJECT_NAME)||' compile';end if;
 exception when others then null;end;
 end loop;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID'and OBJECT_NAME not like 'BIN$%';exit when n=0;
 end loop;
 if n!=0 then raise_application_error(-20899,'NESTED_RECEIVING_INVALID_OBJECTS');end if;
end;
/
""")
print(json.dumps(out))
