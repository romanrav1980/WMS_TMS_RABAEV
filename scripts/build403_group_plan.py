from pathlib import Path
import json
d='db/migrations/2026-10-12_ni061_group_source'
out={}
out[d+'/001_schema.sql']="""begin execute immediate q'[create table RRL_IW_GROUP_PLAN(
 OPERATION_ID varchar2(100) primary key,PAYLOAD_HASH raw(32)not null,
 SOURCE_LOAD_OPERATION_ID varchar2(100)not null unique references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 SOURCE_WARE_ID number not null,TARGET_WARE_ID number not null,
 SOURCE_TT_ID number not null,TARGET_TT_ID number not null references RRL_TRANSPORT_TASK(ID),
 ROOT_UID varchar2(200)not null,INBOUND_DOCK varchar2(60)not null,OUTBOUND_DOCK varchar2(60)not null,
 ARRIVAL_DUE timestamp with time zone not null,READY_DUE timestamp with time zone not null,
 SOURCE_JSON clob not null check(SOURCE_JSON is json),RESULT_JSON clob not null check(RESULT_JSON is json),
 REASON_TEXT nvarchar2(500)not null,DECISION_REFERENCE varchar2(60)not null,
 ACTOR nvarchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 check(SOURCE_WARE_ID!=TARGET_WARE_ID),check(SOURCE_TT_ID!=TARGET_TT_ID),check(READY_DUE>=ARRIVAL_DUE)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_IW_GROUP_TARGET_IX on RRL_IW_GROUP_PLAN(TARGET_WARE_ID,ARRIVAL_DUE)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
"""
out[d+'/002_source.sql']="""create or replace package RRL_IW_GROUP_SOURCE authid definer as
 function source_json(p_load varchar2,p_actor varchar2)return clob;
end;
/
create or replace package body RRL_IW_GROUP_SOURCE as
 function source_json(p_load varchar2,p_actor varchar2)return clob is
 lf RRL_TT_HU_LOAD_FACT%rowtype;wire clob;tree json_object_t;domain_value json_object_t;
 nodes json_array_t;shipments json_array_t;lots json_array_t:=json_array_t();links json_array_t;
 item json_object_t;part json_object_t;leg json_object_t;node json_object_t;entry json_object_t;
 result_value json_object_t:=json_object_t();manifest json_object_t;profile_wire clob;n number;st number;
 type seen_set is table of boolean index by varchar2(200);seen_lots seen_set;seen_st seen_set;leaf_count number:=0;
 begin
 RRL_INTERWARE_UNIT_SOURCE.assert_scope(p_load,p_actor);
 select *into lf from RRL_TT_HU_LOAD_FACT where LOAD_OPERATION_ID=p_load and STATUS='DEPARTED'and ROOT_CASE_TASK_ID is null;
 select RESOLVED_PLAN_JSON into wire from RRL_STOCK_OPERATION where OPERATION_ID=p_load and STATE='APPLIED'and COMMAND_TYPE='HU_SHIP';
 tree:=json_object_t.parse(lf.COMPOSITION_JSON);nodes:=tree.get_array('nodes');domain_value:=json_object_t.parse(wire).get_object('domain');shipments:=domain_value.get_array('shipments');
 if nodes.get_size<3 or nodes.get_size>200 or tree.get_number('top_place_count')!=1 or tree.get_string('root')!=lf.ROOT_UID or shipments.get_size<2 or shipments.get_size>200 then raise_application_error(-20886,'INTERWARE_GROUP_BOUNDED_TOP_REQUIRED');end if;
 for i in 0..nodes.get_size-1 loop
  node:=treat(nodes.get(i)as json_object_t);
  if node.get_string('kind')='STOCK'then
   if node.get_number('case_task_id')is not null or seen_lots.exists(node.get_string('uid'))then raise_application_error(-20886,'INTERWARE_GROUP_DISTINCT_STOCK_ONLY');end if;
   seen_lots(node.get_string('uid')):=true;leaf_count:=leaf_count+1;
  elsif node.get_string('kind')='CONTAINER'then
   select count(*)into n from RRL_PALLETS where UID_PALLET=node.get_string('uid')and HU_KIND='CONTAINER'and HU_CURRENT_CELL is null and HU_SHIPPED_OPERATION=p_load and HU_CONTENT_VERSION=node.get_number('version')+1;
   if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_CONTAINER_EPOCH_CHANGED');end if;
  else raise_application_error(-20886,'INTERWARE_GROUP_STOCK_CONTAINER_ONLY');end if;
 end loop;
 if leaf_count!=shipments.get_size or leaf_count!=tree.get_number('leaf_count')then raise_application_error(-20886,'INTERWARE_GROUP_ONE_ST_PER_LEAF_REQUIRED');end if;
 links:=tree.get_array('links');
 if links.get_size!=nodes.get_size-1 then raise_application_error(-20886,'INTERWARE_GROUP_COMPLETE_TREE_REQUIRED');end if;
 for i in 0..links.get_size-1 loop
  item:=treat(links.get(i)as json_object_t);
  select count(*)into n from RRL_WMS_HU_LINK where HU_LINK_ID=item.get_number('id')and PARENT_UID=item.get_string('parent')and CHILD_PALLET_UID=item.get_string('child')and CHILD_CASE_TASK_ID is null and ACTIVE_FLAG=0 and UNLINKED_OPERATION_ID=p_load and LINK_VERSION=item.get_number('version')+1;
  if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_FROZEN_LINK_CHANGED');end if;
 end loop;
 select count(*)into n from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=p_load and ACTIVE_FLAG=1;
 if n!=shipments.get_size then raise_application_error(-20886,'INTERWARE_GROUP_MEMBER_COUNT_CHANGED');end if;
 for i in 0..shipments.get_size-1 loop
  part:=treat(shipments.get(i)as json_object_t).get_object('domain');st:=part.get_number('document_id');
  if part.get_array('legs').get_size!=1 or part.get_number('return_supplier_id')is not null or part.has('interwarehouse_onward_source')or seen_st.exists(to_char(st))then raise_application_error(-20886,'INTERWARE_GROUP_FIRST_CUSTOMER_LEG_REQUIRED');end if;
  seen_st(to_char(st)):=true;leg:=treat(part.get_array('legs').get(0)as json_object_t);
  if not seen_lots.exists(leg.get_string('uid'))then raise_application_error(-20886,'INTERWARE_GROUP_FOREIGN_LEAF');end if;
  seen_lots.delete(leg.get_string('uid'));
  select count(*)into n from RRL_TT_HU_LOAD_ST where LOAD_OPERATION_ID=p_load and ACTIVE_FLAG=1 and SBORKA_PALLET_ID=st;
  if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_EXACT_MEMBER_REQUIRED');end if;
  select count(*)into n from json_table(lf.COMPOSITION_JSON,'$.nodes[*]'columns(NODE_KIND varchar2(20)path '$.kind',NODE_UID varchar2(200)path '$.uid',ARTICLE_VALUE varchar2(160)path '$.article',QTY_VALUE varchar2(60)path '$.quantity',UOM_VALUE varchar2(20)path '$.base_uom'))j
  where NODE_KIND='STOCK'and NODE_UID=leg.get_string('uid')and ARTICLE_VALUE=leg.get_string('article')and UOM_VALUE=leg.get_string('base_uom')and RRL_STOCK_MATH.quantity(QTY_VALUE)=RRL_STOCK_MATH.quantity(leg.get_string('quantity'));
  if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_EXACT_WHOLE_LEAF_REQUIRED');end if;
  select count(*)into n from RRL_REMAINS where UID_POLETA=leg.get_string('uid')and(nvl(REMAIN,0)!=0 or nvl(HARD_RESERVED_BASE,0)!=0);
  if n!=0 then raise_application_error(-20886,'INTERWARE_GROUP_SOURCE_ALREADY_PRESENT');end if;
  manifest:=json_object_t.parse(RRL_INTERWARE_UNIT_SOURCE.issued_manifest(p_load,leg.get_string('uid'),lf.COMPOSITION_JSON));
  select json_arrayagg(json_object('system_code'value SYSTEM_CODE,'profile_code'value PROFILE_CODE,'profile_version'value PROFILE_VERSION,'scan_mode'value SCAN_MODE)order by SYSTEM_CODE,PROFILE_CODE returning clob)
   into profile_wire from RRL_SKU_RECEIPT_PROFILE where ARTICUL=leg.get_string('article');
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
"""
out[d+'/003_guard.sql']="""create or replace trigger RRL_IW_GROUP_PLAN_GUARD before insert or update or delete on RRL_IW_GROUP_PLAN for each row
declare wire clob;source_value json_object_t;n number;
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_GROUP_PLAN_IMMUTABLE');end if;
 RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);
 wire:=RRL_IW_GROUP_SOURCE.source_json(:new.SOURCE_LOAD_OPERATION_ID,:new.ACTOR);source_value:=json_object_t.parse(wire);
 if dbms_lob.compare(wire,:new.SOURCE_JSON)!=0 or source_value.get_number('source_trip_id')!=:new.SOURCE_TT_ID or source_value.get_number('source_warehouse_id')!=:new.SOURCE_WARE_ID or source_value.get_string('physical_place_identifier')!=:new.ROOT_UID then raise_application_error(-20886,'INTERWARE_GROUP_EXACT_SOURCE_REQUIRED');end if;
 select count(*)into n from RRL_TT_DOCK where DOCK=:new.INBOUND_DOCK and WARE_ID=:new.TARGET_WARE_ID and nvl(DOCK_IS_BLOCKED,0)=0;
 if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_TARGET_INBOUND_REQUIRED');end if;
 select count(*)into n from RRL_TRANSPORT_TASK t join RRL_TT_DOCK d on d.DOCK=t.DOCK and d.WARE_ID=:new.TARGET_WARE_ID and nvl(d.DOCK_IS_BLOCKED,0)=0
 where t.ID=:new.TARGET_TT_ID and t.DOCK=:new.OUTBOUND_DOCK and t.CONDITION='Спланирован'and nvl(t.DELETED,0)=0;
 if n!=1 then raise_application_error(-20886,'INTERWARE_GROUP_TARGET_TRIP_REQUIRED');end if;
end;
/
"""
p=Path('tmp/native401_rrl_interware_plan_guard_trigger.sql');t=p.read_text(encoding='utf-8')
out[d+'/000_before_plan_guard.sql']=t
needle=" RRL_STOCK_LOCK_API.assert_policy(RRL_STOCK_LOCK_API.resource_key('CONFIG','WAREHOUSE'),6);"
t=t.replace(needle,needle+"\n select count(*)into n from RRL_IW_GROUP_PLAN where SOURCE_LOAD_OPERATION_ID=:new.SOURCE_LOAD_OPERATION_ID;\n if n!=0 then raise_application_error(-20886,'INTERWARE_SCALAR_GROUP_PLAN_EXISTS');end if;",1)
out[d+'/004_scalar_guard.sql']=t
out[d+'/005_ledger.sql']="""begin
 insert into RRL_DB_MIGRATION(MIGRATION_ID,DESCRIPTION,APPLIED_BY)select '2026-10-12-403-grouped-interware-plan','Immutable whole multi-ST source plan; no quantity effect',user from dual where not exists(select 1 from RRL_DB_MIGRATION where MIGRATION_ID='2026-10-12-403-grouped-interware-plan');
end;
/
"""
out[d+'/apply.sql']='\n'.join('@@'+x for x in ['001_schema.sql','002_source.sql','003_guard.sql','004_scalar_guard.sql','005_ledger.sql'])+'\n'
out[d+'/rollback.sql']="""declare n number;begin select count(*)into n from RRL_IW_GROUP_PLAN;if n!=0 then raise_application_error(-20899,'GROUP_PLANS_REQUIRE_FORWARD_RECOVERY');end if;end;
/
@@000_before_plan_guard.sql
drop trigger RRL_IW_GROUP_PLAN_GUARD;
drop package RRL_IW_GROUP_SOURCE;
drop table RRL_IW_GROUP_PLAN;
delete from RRL_DB_MIGRATION where MIGRATION_ID='2026-10-12-403-grouped-interware-plan';
commit;
"""
print(json.dumps(out))
