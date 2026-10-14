from pathlib import Path
import json,hashlib
read=lambda p:Path(p).read_text(encoding="utf-8");d="db/migrations/2026-10-13_ni033_case_binding_move/";files={}
for n in("RRL_STOCK_CASE_MOVE_CMD","RRL_ST_DEFER_CASE_WAIT"):
 p="tmp/973_"+n.lower()+"_package_body.sql";files[d+"000_before_"+n.lower()+".sql"]=read(p)
move="\n".join(x for x in files[d+"000_before_rrl_stock_case_move_cmd.sql"].splitlines()if x.strip())+"\n"
needle="  RRL_ST_DEFER_CASE_WAIT.plan_move(p_request,d.get_string('actor'),r,v);";assert move.count(needle)==1
move=move.replace(needle,"  RRL_STOCK_CASE_BIND_MOVE.plan_move(ct,r,v);\n"+needle)
needle="  if ct.STATUS is null or ct.STATUS not in("
assert move.count(needle)==1
move=move.replace(needle,"  RRL_STOCK_CASE_BIND_MOVE.validate_move(ct,v.get_object('shipment_binding'));\n"+needle)
needle="  select RRL_CASE_PICK_EVENT_SQ.nextval into event_id from dual;";assert move.count(needle)==1
move=move.replace(needle,"  RRL_STOCK_CASE_BIND_MOVE.finish_move(ct,v.get_object('shipment_binding'),ct.CONTENT_VERSION+1,p_actor);\n"+needle)
files[d+"002_case_move.sql"]=move
wait=files[d+"000_before_rrl_st_defer_case_wait.sql"]
needle="""  update RRL_CUSTOMER_ORDER_FULFILLMENT set PICKED_CONTENT_VERSION=new_version,UPDATED_AT=sysdate,UPDATED_BY=p_actor
   where FULFILLMENT_ID=ff_id and STATUS='PICKED'and PICKED_CASE_TASK_ID=case_id;
  if sql%rowcount!=1 then raise_application_error(-20886,'DEFER_CASE_FULFILLMENT_BINDING_CHANGED');end if;"""
# Normalize capture line endings so one versioned replacement is exact.
wait="\n".join(x for x in wait.splitlines()if x.strip())+"\n"
assert wait.count(needle)==1
wait=wait.replace(needle,"""  select count(*)into v_sync_id from RRL_CUSTOMER_ORDER_FULFILLMENT
   where FULFILLMENT_ID=ff_id and STATUS='PICKED'and PICKED_CASE_TASK_ID=case_id and PICKED_CONTENT_VERSION=new_version;
  if v_sync_id!=1 then raise_application_error(-20886,'DEFER_CASE_FULFILLMENT_BINDING_CHANGED');end if;""")
files[d+"003_wait_finish.sql"]=wait
files[d+"apply.sql"]="@@001_binding.sql\n@@002_case_move.sql\n@@003_wait_finish.sql\n@@004_compile.sql\n@@005_ledger.sql\n"
files[d+"004_compile.sql"]=read("db/migrations/2026-10-13_ni072_case_wait/008_compile.sql")
files[d+"rollback.sql"]="@@000_before_rrl_stock_case_move_cmd.sql\n@@000_before_rrl_st_defer_case_wait.sql\ndrop package RRL_STOCK_CASE_BIND_MOVE;\n@@004_compile.sql\n"
files[d+"verify.sql"]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%'order by NAME,SEQUENCE;\nselect c.CASE_PICK_TASK_ID,c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where f.STATUS='PICKED'and c.CASE_PICK_TASK_ID in(1129,1130);\n"
files[d+"005_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-005-ni033-case-bound-move'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing CASE mover freezes and locks bound fulfillment then advances its physical version in the same stock transaction, retaining original pick facts',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
helper=read(d+"001_binding.sql");files[d+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-13-005-ni033-case-bound-move","state":"PREPARED","target":"RABAEV/orcl","recovery":"captured current973 CASE mover/wait finisher and paired rollback, additive package; no DB copy","sha256":{**{p:hashlib.sha256(b.encode()).hexdigest()for p,b in files.items()},d+"001_binding.sql":hashlib.sha256(helper.encode()).hexdigest()}},indent=2)
page="""# NI03.3 — исполнение заказа при перемещении связанного CASE

Migration2026-10-13-005-ni033-case-bound-move, PREPARED before apply. Capture973 actual CASE1129/1130 inwaiting/currentCT2 and boundFF2. Current CASE_CARRIER_MOVE changes CTversion/currentcell, but its generic branch does not advance boundFF version. Waiting helper953 does; this change makes the existing physical mover the one owner of the version relationship.

Small metadata helper RRL_STOCK_CASE_BIND_MOVE, accessible only to existing CASE mover. Unbound CASE unchanged. Bound CASE requires original ST sameWARE/unloaded, exactly one original PICKED fulfillment/customer order/carrier/current version/original composition. Root declares ST/FF row locks; freezes material binding fields and composition hash, revalidates after locks before moving actual lots. After old TRANSFER_CORE and CT movement, FF picked content version is advanced in the same transaction. Original quantity/UOM/composition/pick stamps untouched. Waiting finisher changes from second FF updater to proof of that same new version.

Old QC facts remain historical; current admission uses current composition/version. No new stock writer, binding engine or shipment is created. Current role/WARE before replay remains existing CASE_TASK_ACCESS (+WHT access for waiting). Captured sources/SHA/paired rollback; no DB copy. Rollback not tested. Need live compile + actual forward movement of retained955/966, no source rebirth; no full sprint closure claimed.
"""
files["wiki/database/nicora_ni033_case_bound_move_20261013.md"]=page
p="wiki/index.md";files[p]="- [NI03.3 CASE binding974](database/nicora_ni033_case_bound_move_20261013.md): prepared sameTX original FF version on generic CASE movement; capturedcurrent973, live pending.\n"+read(p)
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint974 PREPARED smallboundCASE metadata helper/current CASE mover + one FF-version owner; captured973, additive package/SHA/rollback, no stock writer/copy. Liveapply and retainedforwardflow pending.\n"
print(json.dumps(files,ensure_ascii=True))
