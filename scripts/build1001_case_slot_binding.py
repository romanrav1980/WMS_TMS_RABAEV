from pathlib import Path
import json,hashlib
read=lambda p:Path(p).read_text(encoding="utf-8");files={};d="db/migrations/2026-10-13_ni041_case_slot_binding/"
def capture(name,suffix):
 raw=read("tmp/1000_"+name+"_"+suffix+".sql");files[d+"000_before_"+name+"_"+suffix+".sql"]=raw
 return "\n".join(x for x in raw.splitlines()if x.strip())+"\n"
spec=capture("rrl_stock_case_bind_move","package")
spec=spec.replace("package RRL_STOCK_HU_CMD)","package RRL_STOCK_HU_CMD,package RRL_STOCK_HU_SLOT_MOVE_CMD)")
files[d+"001_binding_spec.sql"]=spec
capture("rrl_stock_case_bind_move","package_body")
capture("rrl_stock_hu_slot_move_cmd","package")
body=capture("rrl_stock_hu_slot_move_cmd","package_body")
needle="  RRL_STOCK_HU_CMD.declare_tree(f,r,s);";assert body.count(needle)==1
body=body.replace(needle,needle+"\n  RRL_STOCK_CASE_BIND_MOVE.plan_tree(tree.get_array('nodes'),r,v);",1)
needle="v_case number;";assert body.count(needle)==1
body=body.replace(needle,"v_case number;v_case_before RRL_CASE_PICK_TASK%rowtype;v_nodes clob;v_locked_id number;",1)
needle="  s:=snapshot(v_uid,v_case);\n  if digest(s)";assert body.count(needle)==1
locks="""  v_nodes:=tree.get_array('nodes').to_clob;
  -- Actual row locks match the existing shipping/HU ST-before-CASE order.
  for st in(select ID from RRL_SBORKA_PALLETS where ID in(
   select LEGACY_SBORKA_PALLET_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(
    select CASE_ID from json_table(v_nodes,'$[*]' columns(CASE_ID number path '$.case_task_id')))) order by ID) loop
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_SBORKA_PALLETS',RRL_STOCK_PLAN_HELPER.decimal_text(st.ID)));
   select ID into v_locked_id from RRL_SBORKA_PALLETS where ID=st.ID for update;
  end loop;
  for ct in(select CASE_PICK_TASK_ID from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID in(
   select CASE_ID from json_table(v_nodes,'$[*]' columns(CASE_ID number path '$.case_task_id'))) order by CASE_PICK_TASK_ID) loop
   RRL_STOCK_LOCK_API.assert_held(20,RRL_STOCK_LOCK_API.resource_key('ROW','RRL_CASE_PICK_TASK',RRL_STOCK_PLAN_HELPER.decimal_text(ct.CASE_PICK_TASK_ID)));
   select CASE_PICK_TASK_ID into v_locked_id from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=ct.CASE_PICK_TASK_ID for update;
  end loop;
  RRL_STOCK_CASE_BIND_MOVE.validate_tree(tree.get_array('nodes'),v);
  if v_case is not null then select *into v_case_before from RRL_CASE_PICK_TASK where CASE_PICK_TASK_ID=v_case;end if;
"""
body=body.replace(needle,locks+needle,1)
needle="  if sql%rowcount!=1 then raise_application_error(-20890,'CLOSURE_CHANGED: HU active placement');end if;"
assert body.count(needle)==1
body=body.replace(needle,needle+"""
  if v_case is not null then
   RRL_STOCK_CASE_BIND_MOVE.finish_move(v_case_before,RRL_STOCK_CASE_BIND_MOVE.binding_for(v,v_case),v_case_before.CONTENT_VERSION+1,p_actor);
  end if;""",1)
files[d+"002_slot_move_body.sql"]=body
files[d+"003_compile.sql"]=read("db/migrations/2026-10-13_ni041_hu_case_binding/004_compile.sql")
files[d+"004_ledger.sql"]=read("db/migrations/2026-10-13_ni041_hu_case_binding/005_ledger.sql").replace("2026-10-13-008-ni041-hu-case-binding","2026-10-13-009-ni041-case-slot-binding").replace("Existing HU tree operations declare and preserve active CASE fulfillment versions in the same stock transaction through reused binding core; closed shipment history unchanged","Existing direct CASE physical slot relocation preserves active fulfillment version through the shared binding core, current ST/CASE actual-row order and original placement/reservation transaction")
files[d+"apply.sql"]="@@001_binding_spec.sql\n@@002_slot_move_body.sql\n@@003_compile.sql\n@@004_ledger.sql\ncommit;\n"
files[d+"rollback.sql"]="@@000_before_rrl_stock_case_bind_move_package.sql\n@@000_before_rrl_stock_case_bind_move_package_body.sql\n@@000_before_rrl_stock_hu_slot_move_cmd_package.sql\n@@000_before_rrl_stock_hu_slot_move_cmd_package_body.sql\n@@003_compile.sql\n"
files[d+"verify.sql"]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%';\nselect c.CASE_PICK_TASK_ID,c.CONTENT_VERSION,f.PICKED_CONTENT_VERSION from RRL_CASE_PICK_TASK c join RRL_CUSTOMER_ORDER_FULFILLMENT f on f.PICKED_CASE_TASK_ID=c.CASE_PICK_TASK_ID where c.CASE_PICK_TASK_ID in(1131,1132);\n"
files[d+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-13-009-ni041-case-slot-binding","state":"PREPARED","target":"RABAEV/orcl","recovery":"current1000 captures/pairedrollback; committed history must not be discarded","sha256":{p:hashlib.sha256(b.encode()).hexdigest()for p,b in files.items()}},indent=2)
page="""# NI04.1 — исполнение CASE при смене физического слота

1001 PREPARED: текущий RRL_STOCK_HU_SLOT_MOVE_CMD (capture1000) повышает CONTENT_VERSION прямого CASE при HU_RELOCATE_SLOT, не повышая PICKED_CONTENT_VERSION активного исполнения заказа. Используем прежний RRL_STOCK_CASE_BIND_MOVE, текущий снимок binding в плане, ST/FF ключи и согласованный ST-before-CASE actual row order. Перед записью проверяется frozen binding, затем CASE/FF версии меняются вместе с прежними placement/claim/HARD coverage в Root. Количество не изменяется.

Контейнер между слотами повышает только собственную версию; версии вложенных CASE не повышаются искусственно. Slotted unpack/repack уже вызывают HU_CMD и получают binder993 через прежнее проксирование. Captures/SHA/rollback сохранены, применение и адресный действующий bound CASE сценарий pending. ПолныйNI04.1 не закрыт.
"""
files["wiki/database/nicora_ni041_case_slot_binding_20261013.md"]=page
p="wiki/index.md";files[p]="- [CASE slot binding1001](database/nicora_ni041_case_slot_binding_20261013.md): prepared reuse binder/current actual-row order, live pending.\n"+read(p)
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint1001 PREPARED current1000 direct CASE relocation/version gap; reuse existingCaseBindMove/currentSTFF freeze/ST-before-CASE actual rows/sameRootplacement+HARD, no stock writer. Captures/rollback/SHA/wiki before apply; actualpending.\n"
print(json.dumps(files,ensure_ascii=True))
