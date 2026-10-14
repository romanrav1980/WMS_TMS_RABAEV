import json
from pathlib import Path
d=Path("db/migrations/2026-10-11_ni041_slot_repack");out={}
def change(t,old,new):
 assert old in t,old
 return t.replace(old,new)
for n,short in [(2,"hu"),(3,"slot"),(4,"placement"),(5,"reserve")]:
 t=(d/("000_before_"+short+".sql")).read_text(encoding="utf-8")
 pos=t.index(") as",t.index("accessible by("))
 t=t[:pos]+",package RRL_STOCK_HU_REPACK_CMD"+t[pos:]
 out[str(d/(f"{n:03}_{short}_contract.sql"))]=t
 out[str(d/(f"{n:03}_{short}_spec.sql"))]=t[:t.index("create or replace package body")]
t=(d/"000_before_root.sql").read_text(encoding="utf-8")
t=change(t,"'HU_RELOCATE_SLOT','HU_ATTACH','HU_DETACH','HU_UNPACK'","'HU_RELOCATE_SLOT','HU_ATTACH','HU_DETACH','HU_UNPACK','HU_REPACK_SLOT'")
helper=""" procedure assert_repack_actor(p_request clob,p_actor varchar2)is
  d json_object_t:=json_object_t.parse(p_request);uid varchar2(200);ware number;user_ware number;grp varchar2(100);
 begin
  if d.get_string('command_type')!='HU_REPACK_SLOT'then return;end if;uid:=d.get_object('source').get_string('uid');
  select c.WARE_ID into ware from RRL_PALLETS p join RRL_CELLS c on c.CELL=p.HU_CURRENT_CELL where p.UID_PALLET=uid;
  select WARE_ID,USER_GROUP into user_ware,grp from RUSERS where ID=p_actor and nvl(DELETED,0)=0;
  if ware is null or ware<1 then raise_application_error(-20886,'HU_REPACK_WARE_REQUIRED');end if;
  if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 or(nvl(upper(trim(grp)),'-')!='GLOBAL_ADMIN'and(user_ware is null or user_ware!=ware))then raise_application_error(-20882,'HU_REPACK_CURRENT_WARE_EXECUTOR_REQUIRED');end if;
 exception when no_data_found then raise_application_error(-20886,'HU_REPACK_CURRENT_SOURCE_REQUIRED');end;
"""
t=change(t," procedure reset_connection is",helper+" procedure reset_connection is")
t=t.replace("assert_case_slot_actor(p_request,p_actor);","assert_case_slot_actor(p_request,p_actor);assert_repack_actor(p_request,p_actor);")
t=change(t,"  elsif g_kind='HU_UNPACK' then RRL_STOCK_HU_UNPACK_CMD.compile_command", "  elsif g_kind='HU_REPACK_SLOT'then RRL_STOCK_HU_REPACK_CMD.compile_command(p_request,g_operation,v_policies,v_resources,v_domain);\n  elsif g_kind='HU_UNPACK' then RRL_STOCK_HU_UNPACK_CMD.compile_command")
t=change(t,"  elsif g_kind='HU_UNPACK' then RRL_STOCK_HU_UNPACK_CMD.execute_command","  elsif g_kind='HU_REPACK_SLOT'then RRL_STOCK_HU_REPACK_CMD.execute_command(g_request,g_actor,p_result);\n  elsif g_kind='HU_UNPACK' then RRL_STOCK_HU_UNPACK_CMD.execute_command")
out[str(d/"006_root_contract.sql")]=t;out[str(d/"006_root_body.sql")]=t[t.index("create or replace package body"):]
guards=[]
for p in sorted(d.glob("000_before_rrl_hu*.sql")):
 t=p.read_text(encoding="utf-8")
 if p.name=="000_before_rrl_hu_tare_link_guard.sql":
  t=change(t,"command_kind!='HU_ATTACH'","command_kind not in('HU_ATTACH','HU_REPACK_SLOT')")
 else:
  # Retain every old whitelist member and its guards, add only the new physical action.
  t=t.replace("'HU_RELOCATE_SLOT')","'HU_RELOCATE_SLOT','HU_REPACK_SLOT')").replace("'HU_SHIP','HU_UNPACK')","'HU_SHIP','HU_UNPACK','HU_REPACK_SLOT')")
 guards.append(t)
out[str(d/"007_guards.sql")]="\n".join(guards)
out[str(d/"apply.sql")]="-- MIGRATION_ID:2026-10-11-177-slot-repacking\n@@002_hu_spec.sql\n@@003_slot_spec.sql\n@@004_placement_spec.sql\n@@005_reserve_spec.sql\n@@001_repack.sql\n@@006_root_body.sql\n@@007_guards.sql\n@@../2026-10-08_stock_posting_core/014b_recompile.sql\n"
old=[p.name for p in sorted(d.glob("000_before*.sql"))]
out[str(d/"rollback.sql")]="-- Keep physical history: refuse downgrade once repacking was committed.\ndeclare n number;begin select count(*)into n from RRL_STOCK_OPERATION where COMMAND_TYPE='HU_REPACK_SLOT'and STATE='APPLIED';if n>0 then raise_application_error(-20808,'HU_REPACK_FORWARD_REPAIR_REQUIRED');end if;end;\n/\n"+"".join("@@"+n+"\n"for n in old)+"drop package RRL_STOCK_HU_REPACK_CMD;\n@@../2026-10-08_stock_posting_core/014b_recompile.sql\n"
out[str(d/"verify.sql")]="select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_HU_REPACK_CMD','RRL_STOCK_HU_CMD','RRL_STOCK_HU_SLOT','RRL_STOCK_HU_PLACEMENT_CORE','RRL_STOCK_RESERVE_CORE','RRL_STOCK_POSTING_API');\nselect NAME,LINE,TEXT from USER_ERRORS where NAME like 'RRL_STOCK_HU%'or NAME='RRL_STOCK_POSTING_API';\n"
print(json.dumps(out))
