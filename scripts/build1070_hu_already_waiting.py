from pathlib import Path
import json,hashlib
d="db/migrations/2026-10-13_ni072_nested_hu_wait/";files={}
helper=Path(d+"013_hu_lock_scope.sql").read_text(encoding="utf-8")
needle="if value.get_string('cell')=value.get_string('target_cell')then raise_application_error(-20886,'DEFER_HU_ALREADY_WAITING_NO_MOVE_REQUIRED');end if;"
assert helper.count(needle)==1
helper=helper.replace(needle,"if value.get_string('cell')=value.get_string('target_cell')then return;end if;")
files[d+"017_already_waiting_scope.sql"]=helper
api=Path(d+"015_wait_replay.sql").read_text(encoding="utf-8")
needle="   if prep.get_string('state')in('PREPARED_CASE','PREPARED_CASES')then";assert api.count(needle)==1
branch="""   if prep.get_string('state')='PREPARED_HU'then
    if prep.get_string('cell')!=target then raise_application_error(-20886,'DEFER_HU_ROOT_PLANNING_REQUIRED');end if;
    skips.append(prep.get_string('root'));
    result.put('operation_id',p_operation);result.put('decision_operation_id',p_decision);result.put('st_number',decision.ST_NUMBER);
    result.put('warehouse_id',decision.WARE_ID);result.put('waiting_cell',target);result.put('tasks',targets);result.put('already_waiting',skips);
    result.put('stock_changed',false);result.put('physical_move_completed',false);p_result:=result.to_clob;
    g_tx:=dbms_transaction.local_transaction_id(true);
    insert into RRL_ST_DEFER_WAIT_RUN(OPERATION_ID,DECISION_OPERATION_ID,ACTOR,REQUEST_JSON,RESULT_JSON)
     values(p_operation,p_decision,p_actor,request_body,p_result);
    g_tx:=null;RRL_STOCK_METADATA_TX.end_change;return;
   end if;
"""
files[d+"018_already_waiting_api.sql"]=api.replace(needle,branch+needle)
p=d+"apply.sql";files[p]=Path(p).read_text(encoding="utf-8")+"@@017_already_waiting_scope.sql\n@@018_already_waiting_api.sql\n"
p=d+"checkpoint.json";v=json.loads(Path(p).read_text(encoding="utf-8"));v["state"]="APPLIED_VALID_ALREADY_WAITING_EXTENSION_PREPARED"
v["extension"]="1070 all-CASE HU already waiting: metadata receipt/noWHT/stockwrite, fresh whole source/config/decision validation, exact cached result"
v["sha256"].update({p:hashlib.sha256(t.encode()).hexdigest()for p,t in files.items()});files[p]=json.dumps(v,indent=2)
p="wiki/database/nicora_ni072_nested_hu_wait_20261013.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n1070 PREPARED already-waiting extension: current wholeHU snapshot/config/decision verified under existing metadata fence, record immutable WAIT_RUN with already_waiting root and emptytasks; noHUWHT/stock/core receipt fabricated. 1069 actualtwo-containerlevels move+bounded TT row contention passed on original20goods; report pending.\n"
for p,note in [
("wiki/index.md","- [Already waiting1070](database/nicora_ni072_nested_hu_wait_20261013.md): prepared no newHUtask/stock if alreadyatWAIT, deep1069 actualdone.\n"),
("wiki/log.md","\n- checkpoint1070 PREPARED: metadata no-move result for wholeHU alreadywaiting, source/config/decision frozenchecks maintained; captured extension017/018 beforelive. Deep1069 actualcontainer→container→twoCASE/P20H20/ROWbusy20840 passed.\n")]:
 t=Path(p).read_text(encoding="utf-8");files[p]=note+t if p.endswith("index.md")else t+note
print(json.dumps(files,ensure_ascii=True))
