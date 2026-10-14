from pathlib import Path
import json
folder=Path("db/migrations/2026-10-12_ni061_nested_onward");out={}
def read(name):return(folder/("000_before_"+name.lower()+".sql")).read_text(encoding="utf-8")
def put(name,source):out[(folder/name).as_posix()]=source
s=read("RRL_STOCK_HU_SHIP_CMD")
needle="   order by LEGACY_SBORKA_PALLET_ID) loop"
assert needle in s
s=s.replace(needle,"""   union
   select ST_ID from RRL_INTERWARE_ONWARD_BIND where ROOT_UID in(
    select U from json_table(nodes,'$[*]'columns(U varchar2(200)path '$.uid',K varchar2(20)path '$.kind'))where K='STOCK')
   union
   select ST_ID from RRL_IW_RECOVERY_ST_BIND where ROOT_UID in(
    select U from json_table(nodes,'$[*]'columns(U varchar2(200)path '$.uid',K varchar2(20)path '$.kind'))where K='STOCK')
"""+needle.replace("order by LEGACY_SBORKA_PALLET_ID","order by 1"),1)
# First bounded slice has one onward source; multiple dispatch facts share the root op and require a later relational contract.
needle="  a:=snap.get_array('links');"
s=s.replace(needle,"""  for i in 0..plans.get_size-1 loop
   x:=treat(plans.get(i)as json_object_t);subdomain:=x.get_object('domain');
   if subdomain.has('interwarehouse_onward_source')and(plans.get_size!=1 or expected_qty.count!=1)then
    raise_application_error(-20886,'INTERWARE_NESTED_SINGLE_WHOLE_STOCK_LEAF_REQUIRED');
   end if;
  end loop;
"""+needle,1);put("001_hu_shipping.sql",s)
for name,file in [("RRL_STOCK_INTERWARE_NEXT","002_next.sql"),("RRL_STOCK_IW_RECOVERY_NEXT","003_recovery_next.sql")]:
 s=read(name);needle=" if v_kind!='LOAD_SHIPMENT' then raise_application_error(-20886,'INTERWARE_ONWARD_ACTUAL_LOADING_REQUIRED');end if;"
 assert needle in s,name
 replacement=""" if v_kind='HU_SHIP'then
 select count(*)into n from RRL_STOCK_OPERATION root_op
 where root_op.OPERATION_ID=op and root_op.STATE='IN_FLIGHT'
 and json_value(root_op.RESOLVED_PLAN_JSON,'$.domain.loading.trip'returning number)=trip_id
 and exists(select 1 from json_table(root_op.RESOLVED_PLAN_JSON,'$.domain.shipments[*]'columns(
  BINDING_ID varchar2(100)path '$.domain.interwarehouse_onward_source.binding_operation_id',
  ST_NO number path '$.domain.interwarehouse_onward_source.st_id'))resolved
  where resolved.BINDING_ID=p_source.get_string('binding_operation_id')and resolved.ST_NO=st_id);
 if n!=1 then raise_application_error(-20886,'INTERWARE_NESTED_ACTUAL_TARGET_LOADING_REQUIRED');end if;
 elsif v_kind!='LOAD_SHIPMENT'then raise_application_error(-20886,'INTERWARE_ONWARD_ACTUAL_LOADING_REQUIRED');end if;"""
 # JSON object method cannot appear directly in SQL.
 replacement=replacement.replace("resolved.BINDING_ID=p_source.get_string('binding_operation_id')","resolved.BINDING_ID=v_binding ")
 s=s.replace("v_kind varchar2(80);","v_kind varchar2(80);v_binding varchar2(100):=p_source.get_string('binding_operation_id');",1).replace(needle,replacement,1);put(file,s)
s=read("RRL_INTERWARE_ONWARD_FACT_GUARD")
needle="COMMAND_TYPE='LOAD_SHIPMENT'and STATE='IN_FLIGHT'and ACTOR=:new.ACTOR and json_value(RESOLVED_PLAN_JSON,'$.domain.shipment.domain.interwarehouse_onward_source.binding_operation_id')=:new.BIND_OPERATION_ID"
assert needle in s
s=s.replace(needle,"""STATE='IN_FLIGHT'and ACTOR=:new.ACTOR and(
 (COMMAND_TYPE='LOAD_SHIPMENT'and json_value(RESOLVED_PLAN_JSON,'$.domain.shipment.domain.interwarehouse_onward_source.binding_operation_id')=:new.BIND_OPERATION_ID)
 or(COMMAND_TYPE='HU_SHIP'and exists(select 1 from json_table(RESOLVED_PLAN_JSON,'$.domain.shipments[*]'columns(
  BINDING_ID varchar2(100)path '$.domain.interwarehouse_onward_source.binding_operation_id',
  ST_NO number path '$.domain.interwarehouse_onward_source.st_id'))resolved
  where resolved.BINDING_ID=:new.BIND_OPERATION_ID and resolved.ST_NO=:new.ST_ID)
 and json_value(RESOLVED_PLAN_JSON,'$.domain.loading.trip'returning number)=(select TARGET_TT_ID from RRL_INTERWARE_ONWARD_BIND where OPERATION_ID=:new.BIND_OPERATION_ID)))""",1);put("004_onward_guard.sql",s)
s=read("RRL_IW_REC_DISPATCH_GUARD")
import re
s=re.sub(r"for each row\s+begin","for each row\ndeclare v_kind varchar2(80);n number;\nbegin",s,count=1)
needle=" RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'LOAD_SHIPMENT');";assert needle in s
s=s.replace(needle,""" select COMMAND_TYPE into v_kind from RRL_STOCK_OPERATION where OPERATION_ID=:new.OPERATION_ID;
 if v_kind='HU_SHIP'then
 RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'HU_SHIP');
 select count(*)into n from RRL_STOCK_OPERATION root_op where root_op.OPERATION_ID=:new.OPERATION_ID and root_op.ACTOR=:new.ACTOR
 and json_value(root_op.RESOLVED_PLAN_JSON,'$.domain.loading.trip'returning number)=(select TARGET_TT_ID from RRL_IW_RECOVERY_ST_BIND where OPERATION_ID=:new.BIND_OPERATION_ID)
 and exists(select 1 from json_table(root_op.RESOLVED_PLAN_JSON,'$.domain.shipments[*]'columns(
  BINDING_ID varchar2(100)path '$.domain.interwarehouse_onward_source.binding_operation_id',
  ST_NO number path '$.domain.interwarehouse_onward_source.st_id'))resolved
  where resolved.BINDING_ID=:new.BIND_OPERATION_ID and resolved.ST_NO=:new.ST_ID);
 if n!=1 then raise_application_error(-20863,'RECOVERY_NESTED_ACTUAL_LOADING_REQUIRED');end if;
 else RRL_IW_SHORTAGE_GUARD.require_command(:new.OPERATION_ID,'LOAD_SHIPMENT');end if;""",1);put("005_recovery_guard.sql",s)
put("006_ledger.sql","""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-12-312-nested-onward-leaf' MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(s.MIGRATION_ID,'Existing HU shipping includes one whole interwarehouse onward stock leaf; native target loading proof and frozen source bindings retained; no second fulfillment',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
""")
files=[k.split("/")[-1]for k in out if not k.endswith("006_ledger.sql")]
put("apply.sql","".join("@@"+n+"\n"for n in files)+"@@006_ledger.sql\n")
put("rollback.sql","".join("@@000_before_"+n.lower()+".sql\n"for n in["RRL_STOCK_HU_SHIP_CMD","RRL_STOCK_INTERWARE_NEXT","RRL_STOCK_IW_RECOVERY_NEXT","RRL_INTERWARE_ONWARD_FACT_GUARD","RRL_IW_REC_DISPATCH_GUARD"]))
put("verify.sql","select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_HU_SHIP_CMD','RRL_STOCK_INTERWARE_NEXT','RRL_STOCK_IW_RECOVERY_NEXT','RRL_INTERWARE_ONWARD_FACT_GUARD','RRL_IW_REC_DISPATCH_GUARD');\n")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"));put("000_before_manifest.json",p.read_text(encoding="utf-8"))
m["additional_scripts"]+=["../2026-10-12_ni061_nested_onward/"+n for n in files];out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
print(json.dumps(out))
