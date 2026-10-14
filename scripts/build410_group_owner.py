from pathlib import Path
import json
d='db/migrations/2026-10-12_ni061_group_receive';out={}
t=Path('tmp/native401_rrl_stock_interware_rec_package_body.sql').read_text(encoding='utf-8')
out[d+'/000_before_rec.sql']=t
private=""" procedure execute_group(p_request clob,p_actor varchar2,v json_object_t,p_result out clob)is
 d json_object_t:=json_object_t.parse(p_request);op varchar2(100):=d.get_string('operation_id');kind_value varchar2(80):=d.get_string('command_type');
 j json_object_t:=json_object_t();lots json_array_t:=v.get_array('lots');results json_array_t:=json_array_t();item json_object_t;manifest json_object_t;line_value json_object_t;
 v_plan varchar2(100):=v.get_string('plan_operation_id');v_root varchar2(200):=v.get_string('uid');v_ware number:=v.get_number('warehouse_id');
 v_cell varchar2(60):=v.get_string('receive_cell');v_unload varchar2(100):=v.get_string('unload_operation_id');v_uid varchar2(200);v_article varchar2(160);v_qty number;v_uom varchar2(20);v_version number;v_event number;unit_count number:=0;
 begin
 RRL_IW_GROUP_REC.assert_fresh(p_request,p_actor,v);
 j.put('operation_id',op);j.put('plan_operation_id',v_plan);j.put('physical_place_identifier',v_root);j.put('warehouse_id',v_ware);j.put('source_load_operation_id',v.get_string('source_load_operation_id'));j.put('customer_fulfillment_repeated',false);
 if kind_value='INTERWARE_UNLOAD'then
  insert into RRL_IW_GROUP_UNLOAD(OPERATION_ID,PLAN_OPERATION_ID,ROOT_UID,WARE_ID,ACTOR)values(op,v_plan,v_root,v_ware,p_actor);
  j.put('status','UNLOADED_PENDING_RECEIPT');j.put('stock_changed',false);p_result:=j.to_clob;return;
 end if;
 RRL_STOCK_LOCATION_CORE.assert_receiving(v_cell,v_ware);
 insert into RRL_IW_GROUP_RECEIPT(OPERATION_ID,PLAN_OPERATION_ID,UNLOAD_OPERATION_ID,ROOT_UID,WARE_ID,RECEIVE_CELL,ACTOR)values(op,v_plan,v_unload,v_root,v_ware,v_cell,p_actor);
 for i in 0..lots.get_size-1 loop
  item:=treat(lots.get(i)as json_object_t);manifest:=item.get_object('issued_manifest');
  v_uid:=item.get_string('uid');v_article:=item.get_string('article');v_qty:=RRL_STOCK_MATH.quantity(item.get_string('quantity'));v_uom:=item.get_string('base_uom');v_version:=item.get_number('uom_version');
  RRL_STOCK_BALANCE_CORE.apply_delta(v_uid,v_cell,v_qty,0,v_uom,v_version,0);
  RRL_STOCK_BALANCE_CORE.write_leg(v_uid,null,v_cell,v_qty,v_uom,v_version,1,1,1,p_actor,v_event);
  if manifest.get_number('physical_unit_count')>0 then
   RRL_STOCK_UNIT_CORE.receive_issued(v_uid,manifest.get_string('source_cell'),v_cell,v_qty,manifest.get_array('units').to_clob);
   unit_count:=unit_count+manifest.get_number('physical_unit_count');
  end if;
  insert into RRL_IW_GROUP_RECEIPT_LINE(OPERATION_ID,ROOT_UID,ST_ID,ARTICLE,BASE_QTY,BASE_UOM,STOCK_EVENT_ID)values(op,v_uid,item.get_number('st_id'),v_article,v_qty,v_uom,v_event);
  line_value:=json_object_t();line_value.put('uid',v_uid);line_value.put('st_id',item.get_number('st_id'));line_value.put('article',v_article);line_value.put('quantity',item.get_string('quantity'));line_value.put('base_uom',v_uom);line_value.put('event_id',v_event);results.append(line_value);
 end loop;
 RRL_IW_HU_REC_CORE.restore(v,op,p_actor);
 j.put('status','RECEIVED_PENDING_WHOLE_HU_PLACEMENT');j.put('stock_changed',true);j.put('cell',v_cell);j.put('physical_tree_restored',true);j.put('physical_place_count',1);j.put('stock_leaf_count',lots.get_size);j.put('lines',results);j.put('physical_unit_count',unit_count);j.put('regulatory_ack_verified',false);j.put('external_sap_ack',false);
 insert into RRL_SAP_RECEIPT_OUTBOX(EVENT_ID,EVENT_TYPE,PAYLOAD_JSON)values('INTERWAREGROUP:'||rawtohex(sys.dbms_crypto.hash(utl_i18n.string_to_raw(op,'AL32UTF8'),sys.dbms_crypto.hash_sh256)),'INTERWAREHOUSE_RECEIVED',j.to_clob);
 p_result:=j.to_clob;
 end;
"""
t=t.replace(' procedure assert_scope(',private+' procedure assert_scope(',1)
needle=' begin\n  select count(*)into n from RRL_INTERWARE_PLAN'
scope=""" begin
  select count(*)into n from RRL_IW_GROUP_PLAN where OPERATION_ID=p_plan;
  if n=1 then
   select count(*)into n from RRL_IW_GROUP_PLAN p join RUSERS u on u.ID=p_actor where p.OPERATION_ID=p_plan and nvl(u.DELETED,0)=0 and RRL_HAS_WRIGHT(u.ID,'interwarehouse_receive')=1 and(u.WARE_ID=p.TARGET_WARE_ID or upper(trim(u.USER_GROUP))='GLOBAL_ADMIN');
   if n!=1 then raise_application_error(-20882,'INTERWARE_GROUP_TARGET_RECEIVER_REQUIRED');end if;return;
  end if;
  select count(*)into n from RRL_INTERWARE_PLAN"""
assert needle in t;t=t.replace(needle,scope,1)
needle=" begin\n describe_source(p_request,d.get_string('actor'),v);"
replacement=""" begin
 declare group_count number;group_plan varchar2(100):=d.get_object('source').get_string('plan_operation_id');begin
  select count(*)into group_count from RRL_IW_GROUP_PLAN where OPERATION_ID=group_plan;
  if group_count=1 then RRL_IW_GROUP_REC.compile_command(p_request,p_operation,p_policies,p_resources,p_domain);return;end if;
 end;
 describe_source(p_request,d.get_string('actor'),v);"""
assert needle in t;t=t.replace(needle,replacement,1)
needle="select RESOLVED_PLAN_JSON into resolved from RRL_STOCK_OPERATION where OPERATION_ID=op;v:=json_object_t.parse(resolved).get_object('domain');"
assert needle in t;t=t.replace(needle,needle+"\n if v.has('group_receipt')then execute_group(p_request,p_actor,v,p_result);return;end if;",1)
out[d+'/004_owner.sql']=t
out[d+'/005_fact_guards.sql']="""create or replace package RRL_IW_GROUP_FACT_GUARD authid definer as
 procedure assert_head(p_operation varchar2,p_plan varchar2,p_uid varchar2,p_ware number,p_actor varchar2,p_kind varchar2,p_cell varchar2 default null,p_unload varchar2 default null);
end;
/
create or replace package body RRL_IW_GROUP_FACT_GUARD as
 procedure assert_head(p_operation varchar2,p_plan varchar2,p_uid varchar2,p_ware number,p_actor varchar2,p_kind varchar2,p_cell varchar2 default null,p_unload varchar2 default null)is
 op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');kind_value varchar2(80);state_value varchar2(20);wire clob;d json_object_t;
 begin
 if op is null or op!=p_operation or p_actor!=sys_context('RRL_STOCK_WRITE_CTX','ACTOR')or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_GROUP_FACT_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into kind_value,state_value,wire from RRL_STOCK_OPERATION where OPERATION_ID=op;d:=json_object_t.parse(wire).get_object('domain');
 if kind_value!=p_kind or state_value!='IN_FLIGHT'or not d.get_boolean('group_receipt')or d.get_string('plan_operation_id')!=p_plan or d.get_string('uid')!=p_uid or d.get_number('warehouse_id')!=p_ware then raise_application_error(-20863,'INTERWARE_GROUP_EXACT_FACT_REQUIRED');end if;
 if p_kind='INTERWARE_RECEIVE'and(d.get_string('receive_cell')!=p_cell or d.get_string('unload_operation_id')!=p_unload)then raise_application_error(-20863,'INTERWARE_GROUP_EXACT_RECEIPT_REQUIRED');end if;
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_GROUP_PLAN',p_plan));
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW',case when p_kind='INTERWARE_RECEIVE'then 'RRL_IW_GROUP_RECEIPT'else 'RRL_IW_GROUP_UNLOAD'end,op));
 end;
end;
/
create or replace trigger RRL_IW_GROUP_UNLOAD_GUARD before insert or update or delete on RRL_IW_GROUP_UNLOAD for each row
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_GROUP_UNLOAD_IMMUTABLE');end if;
 RRL_IW_GROUP_FACT_GUARD.assert_head(:new.OPERATION_ID,:new.PLAN_OPERATION_ID,:new.ROOT_UID,:new.WARE_ID,:new.ACTOR,'INTERWARE_UNLOAD');
end;
/
create or replace trigger RRL_IW_GROUP_RECEIPT_GUARD before insert or update or delete on RRL_IW_GROUP_RECEIPT for each row
begin
 if not inserting then raise_application_error(-20863,'INTERWARE_GROUP_RECEIPT_IMMUTABLE');end if;
 RRL_IW_GROUP_FACT_GUARD.assert_head(:new.OPERATION_ID,:new.PLAN_OPERATION_ID,:new.ROOT_UID,:new.WARE_ID,:new.ACTOR,'INTERWARE_RECEIVE',:new.RECEIVE_CELL,:new.UNLOAD_OPERATION_ID);
 RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_IW_GROUP_UNLOAD',:new.UNLOAD_OPERATION_ID));
end;
/
create or replace trigger RRL_IW_GROUP_REC_LINE_GUARD before insert or update or delete on RRL_IW_GROUP_RECEIPT_LINE for each row
declare op varchar2(100):=sys_context('RRL_STOCK_WRITE_CTX','OPERATION_ID');n number;wire clob;kind_value varchar2(80);state_value varchar2(20);cell_value varchar2(60);
begin
 if not inserting or op is null or op!=:new.OPERATION_ID or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')is null or sys_context('RRL_STOCK_WRITE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)then raise_application_error(-20863,'INTERWARE_GROUP_LINE_ROOT_REQUIRED');end if;
 select COMMAND_TYPE,STATE,RESOLVED_PLAN_JSON into kind_value,state_value,wire from RRL_STOCK_OPERATION where OPERATION_ID=op;
 cell_value:=json_object_t.parse(wire).get_object('domain').get_string('receive_cell');
 select count(*)into n from json_table(wire,'$.domain.lots[*]'columns(U varchar2(200)path '$.uid',ST_ID number path '$.st_id',ARTICLE_VALUE varchar2(160)path '$.article',QTY_VALUE varchar2(60)path '$.quantity',UOM_VALUE varchar2(20)path '$.base_uom'))j
 where U=:new.ROOT_UID and ST_ID=:new.ST_ID and ARTICLE_VALUE=:new.ARTICLE and RRL_STOCK_MATH.quantity(QTY_VALUE)=:new.BASE_QTY and UOM_VALUE=:new.BASE_UOM;
 if kind_value!='INTERWARE_RECEIVE'or state_value!='IN_FLIGHT'or n!=1 then raise_application_error(-20863,'INTERWARE_GROUP_LINE_RESOLVED_SOURCE_REQUIRED');end if;
 select count(*)into n from RRL_EVENTS where ID_EVENT=:new.STOCK_EVENT_ID and OPERATION_ID=op and UID_POLETA=:new.ROOT_UID and BASE_QTY=:new.BASE_QTY and BASE_UOM=:new.BASE_UOM and CELL_TO=cell_value;
 if n!=1 then raise_application_error(-20863,'INTERWARE_GROUP_LINE_EXACT_EVENT_REQUIRED');end if;
end;
/
"""
out[d+'/006_recompile.sql']="""alter package RRL_IW_HU_REC_CORE compile body;
alter package RRL_STOCK_INTERWARE_REC compile body;
alter package RRL_STOCK_POSTING_API compile body;
"""
out[d+'/007_ledger.sql']="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-409-grouped-interware-receipt' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Whole grouped unload/receipt through existing single stock owner with exact perSKU units and restored HU tree',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
"""
out[d+'/apply.sql']='\n'.join('@@'+f for f in ['001_archive.sql','002_schema.sql','003_core.sql','004_owner.sql','005_fact_guards.sql','006_recompile.sql','007_ledger.sql'])+'\n'
out[d+'/rollback.sql']="""declare n number;begin select count(*)into n from RRL_IW_GROUP_UNLOAD;if n!=0 then raise_application_error(-20899,'GROUP_PHYSICAL_FACTS_REQUIRE_FORWARD_RECOVERY');end if;end;
/
@@000_before_rec.sql
drop trigger RRL_IW_GROUP_REC_LINE_GUARD;
drop trigger RRL_IW_GROUP_RECEIPT_GUARD;
drop trigger RRL_IW_GROUP_UNLOAD_GUARD;
drop package RRL_IW_GROUP_FACT_GUARD;
drop package RRL_IW_GROUP_REC;
drop table RRL_IW_GROUP_RECEIPT_LINE;
drop table RRL_IW_GROUP_RECEIPT;
drop table RRL_IW_GROUP_UNLOAD;
alter package RRL_STOCK_POSTING_API compile body;
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-12-409-grouped-interware-receipt';
commit;
"""
print(json.dumps(out))
