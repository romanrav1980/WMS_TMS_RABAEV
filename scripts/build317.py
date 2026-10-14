from pathlib import Path
import json
d=Path("db/migrations/2026-10-12_ni061_nested_placement");out={}
def read_tmp(name):return "\n".join(line.rstrip()for line in Path("tmp/317_"+name+".sql").read_text(encoding="utf-8").splitlines())+"\n"
def put(n,s):out[(d/n).as_posix()]=s
put_spec=read_tmp("rrl_stock_interware_put_package").replace("package RRL_STOCK_TASK_DOMAIN)","package RRL_STOCK_TASK_DOMAIN,package RRL_STOCK_HU_TASK)",1)
put("000_before_put_spec.sql","create or replace "+read_tmp("rrl_stock_interware_put_package")+"\n/\n")
put("001_put_spec.sql","create or replace "+put_spec+"\n/\n")
s=read_tmp("rrl_stock_interware_put_package_body");put("000_before_put.sql","create or replace "+s+"\n/\n")
s=s.replace("stored_hi number;","stored_hi number;hu_tree json_object_t;hu_nodes json_array_t;hu_node json_object_t;hu_stock number:=0;",1)
needle=" p_domain.put('from_cell',receipt.RECEIVE_CELL);";i=s.index(needle);end=s.index("\n",i)
s=s[:end]+"""
 if plan.SOURCE_PLACE_UID is not null then
 hu_tree:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(plan.SOURCE_PLACE_UID,p_task));hu_nodes:=hu_tree.get_array('nodes');
 if hu_tree.get_string('cell')!=receipt.RECEIVE_CELL or hu_tree.get_number('warehouse')!=receipt.WARE_ID or hu_tree.get_number('leaf_count')!=1 or hu_tree.get_array('ancestors').get_size!=0 then raise_application_error(-20886,'INTERWARE_WHOLE_RECEIVED_HU_REQUIRED');end if;
 for i in 0..hu_nodes.get_size-1 loop hu_node:=treat(hu_nodes.get(i)as json_object_t);
 if hu_node.get_number('open_task_count')>0 then raise_application_error(-20886,'INTERWARE_HU_OTHER_PHYSICAL_TASK_OPEN');end if;
 if hu_node.get_string('kind')='STOCK'then
  hu_stock:=hu_stock+1;
  if hu_node.get_string('uid')!=receipt.ROOT_UID or RRL_STOCK_MATH.quantity(hu_node.get_string('quantity'))!=receipt.BASE_QTY then raise_application_error(-20886,'INTERWARE_HU_ORIGINAL_STOCK_LEAF_REQUIRED');end if;
 elsif hu_node.get_string('kind')!='CONTAINER'then raise_application_error(-20886,'INTERWARE_HU_STOCK_CONTAINER_ONLY');end if;
 end loop;
 if hu_stock!=1 then raise_application_error(-20886,'INTERWARE_HU_ONE_STOCK_REQUIRED');end if;
 p_domain.put('physical_place_uid',plan.SOURCE_PLACE_UID);p_domain.put('hu_version',treat(hu_nodes.get(0)as json_object_t).get_number('version'));
 p_domain.put('hu_snapshot',hu_tree);
 end if;
"""+s[end:]
# This bounded owner rejects replanning HU until cancellation mechanics have explicit reference support.
s=s.replace("   describe_current(receipt_id,p_actor,old_task,p_domain,true);","   describe_current(receipt_id,p_actor,old_task,p_domain,true);\n   if p_domain.has('physical_place_uid')then raise_application_error(-20886,'INTERWARE_HU_REPLAN_EXPLICIT_CANCEL_REQUIRED');end if;",1)
needle=" RRL_STOCK_PLAN_HELPER.stock_closure(f,r,v.get_string('uid'),v.get_string('article'),v.get_string('from_cell'),v.get_string('target_cell'));";assert needle in s
s=s.replace(needle,needle+"""
 if v.has('hu_snapshot')then
 declare nodes json_array_t:=v.get_object('hu_snapshot').get_array('nodes');links json_array_t:=v.get_object('hu_snapshot').get_array('links');item json_object_t;begin
 for i in 0..nodes.get_size-1 loop item:=treat(nodes.get(i)as json_object_t);
 RRL_STOCK_PLAN_HELPER.anchor(r,30,'HU',item.get_string('uid'));RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_PALLETS',item.get_string('uid'));end loop;
 for i in 0..links.get_size-1 loop item:=treat(links.get(i)as json_object_t);RRL_STOCK_PLAN_HELPER.row_key(r,'RRL_WMS_HU_LINK',RRL_STOCK_PLAN_HELPER.decimal_text(item.get_number('id')));end loop;
 end;
 end if;
""",1)
a=s.index(" insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE");b=s.index("\n temp_op:=",a)
old=s[a:b]
new=""" if v.has('physical_place_uid')then
 declare place_id varchar2(200):=v.get_string('physical_place_uid');version_no number:=v.get_number('hu_version');begin
 insert into RRL_WAREHOUSE_TASK(TASK_ID,TASK_TYPE,TASK_SOURCE,SOURCE_TASK_ID,SOURCE_DOC_TYPE,SOURCE_DOC_ID,UID_PALLET,TARGET_ARTICUL,FROM_CELL,TO_CELL,FROM_WARE_ID,TO_WARE_ID,QTY,UNIT_CODE,QTY_MODE,STATUS,CREATED_BY,HU_CONTENT_VERSION)
 values(v_task,'PUTAWAY','MANUAL',v_task,'WAREHOUSE_HU',v_task,place_id,v_article,v_from,v_to,v_ware,v_ware,1,'HU','PALLET','PLANNED',p_actor,version_no);
 j.put('physical_place_identifier',place_id);j.put('task_quantity','1');j.put('task_unit','HU');
 end;
 else
"""+old+"\n end if;"
s=s[:a]+new+s[b:]
a=s.index(" if p_task.TASK_SOURCE!='MANUAL'");b=s.index("\n declare_rows(v,p_resources)",a);old=s[a:b]
s=s[:a]+""" if v.has('physical_place_uid')then
 if p_task.TASK_SOURCE!='MANUAL'or p_task.TASK_TYPE!='PUTAWAY'or p_task.SOURCE_DOC_TYPE!='WAREHOUSE_HU'or p_task.SOURCE_DOC_ID!=p_task.TASK_ID or p_task.UID_PALLET!=v.get_string('physical_place_uid')or p_task.HU_CONTENT_VERSION!=v.get_number('hu_version')or p_task.FROM_CELL!=v.get_string('from_cell')or p_task.TO_CELL!=v.get_string('target_cell')or p_task.UNIT_CODE!='HU'or p_task.QTY!=1 or p_task.QTY_MODE!='PALLET'or v_target!=p_task.TO_CELL then raise_application_error(-20886,'INTERWARE_ORIGINAL_HU_TASK_REQUIRED');end if;
 else
"""+old+"\n end if;"+s[b:]
put("002_put.sql","create or replace "+s+"\n/\n")
s=read_tmp("rrl_stock_hu_task_package_body");put("000_before_hu_task.sql","create or replace "+s+"\n/\n")
s=s.replace("v_key varchar2(400);","v_key varchar2(400);iw_count number;",1) # compile procedure variable
needle="   v.put('resource_context',ctx);";assert needle in s
s=s.replace(needle,"""   select count(*)into iw_count from RRL_INTERWARE_PUT_PLAN where TASK_ID=v_id;
   if iw_count=1 then RRL_STOCK_INTERWARE_PUT.plan_task(t,d.get_string('actor'),r,v);end if;
"""+needle,1)
needle="   ctx:=json_object_t.parse(RRL_TASK_RESOURCE_POLICY.context_json(v_id,'COMPLETE',p_actor,p_actor,";assert needle in s
s=s.replace(needle,"""   if v.has('interwarehouse_placement')then RRL_STOCK_INTERWARE_PUT.validate_task(t,p_actor,v.get_object('interwarehouse_placement'));end if;
"""+needle,1)
needle="   j:=json_object_t.parse(RRL_STOCK_HU_READ.snapshot_json(v_uid));";assert needle in s
s=s.replace(needle,"""   if v.has('interwarehouse_placement')then
    x:=v.get_object('interwarehouse_placement');
    RRL_STOCK_INTERWARE_PUT.complete_task(t,RRL_STOCK_MATH.quantity(x.get_string('quantity')),x.get_string('uid'),p_actor);
   end if;
"""+needle,1)
put("003_hu_task.sql","create or replace "+s+"\n/\n")
s=read_tmp("rrl_hu_task_plan_guard");put("000_before_task_guard.sql","create or replace "+s+"\n/\n")
s=s.replace("'HU_REPACK_SLOT','UNLOAD_SHIPMENT')","'HU_REPACK_SLOT','UNLOAD_SHIPMENT','INTERWARE_PUTAWAY_PLAN')",1)
needle=" if v_kind='UNLOAD_SHIPMENT'then";assert needle in s
s=s.replace(needle,""" if v_kind='INTERWARE_PUTAWAY_PLAN'then
 declare wire clob;state_name varchar2(20);proof json_object_t;begin
 select STATE,RESOLVED_PLAN_JSON into state_name,wire from RRL_STOCK_OPERATION where OPERATION_ID=v_op;proof:=json_object_t.parse(wire).get_object('domain');
 if state_name!='IN_FLIGHT'or proof.get_string('physical_place_uid')is null or proof.get_string('physical_place_uid')!=:new.UID_PALLET or proof.get_number('hu_version')!=:new.HU_CONTENT_VERSION or proof.get_number('task_id')!=:new.TASK_ID or proof.get_string('from_cell')!=:new.FROM_CELL or proof.get_string('target_cell')!=:new.TO_CELL or :new.UNIT_CODE!='HU'or :new.QTY!=1 or :new.SOURCE_DOC_TYPE!='WAREHOUSE_HU'then raise_application_error(-20863,'INTERWARE_HU_TASK_RESOLVED_SOURCE_REQUIRED');end if;
 end;
 end if;
"""+needle,1);put("004_task_guard.sql","create or replace "+s+"\n/\n")
s=read_tmp("rrl_interware_placement_guard");put("000_before_placement_guard.sql","create or replace "+s+"\n/\n")
s=s.replace("COMMAND_TYPE='TASK_COMPLETE'","COMMAND_TYPE in('TASK_COMPLETE','HU_TASK_COMPLETE')",1);put("005_placement_guard.sql","create or replace "+s+"\n/\n")
put("006_recompile.sql","@@../2026-10-12_ni061_nested_receiving/009_recompile.sql\n")
put("007_ledger.sql","""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-317-whole-hu-interware-placement' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Interwarehouse receipt creates existing oneHU task and completes whole physical tree through old HU_TASK_COMPLETE; original stock placement journal records actual base quantity',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
""")
put("apply.sql","".join("@@"+n+"\n"for n in["001_put_spec.sql","002_put.sql","003_hu_task.sql","004_task_guard.sql","005_placement_guard.sql","006_recompile.sql","007_ledger.sql"]))
put("rollback.sql","@@000_before_put_spec.sql\n@@000_before_put.sql\n@@000_before_hu_task.sql\n@@000_before_task_guard.sql\n@@000_before_placement_guard.sql\n@@006_recompile.sql\n")
print(json.dumps(out))
