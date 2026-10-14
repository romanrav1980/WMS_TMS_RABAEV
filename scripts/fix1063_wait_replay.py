from pathlib import Path
import json,hashlib
d="db/migrations/2026-10-13_ni072_nested_hu_wait/";files={}
t=Path(d+"007_wait_api.sql").read_text(encoding="utf-8")
needle="   p_result:=existing.RESULT_JSON;return;"
assert t.count(needle)==1
replacement="""   select count(*)into n from RRL_ST_DEFER_WAIT_PLAN where PLAN_OPERATION_ID=p_operation and BASE_UOM='HU';
   if n>0 then
    if RRL_HAS_WRIGHT(p_actor,'warehouse_task_execute')!=1 then raise_application_error(-20882,'DEFER_HU_CURRENT_EXECUTION_RIGHT_REQUIRED');end if;
    begin select RESULT_JSON into p_result from RRL_STOCK_OPERATION
     where OPERATION_ID=p_operation and COMMAND_TYPE='HU_PLAN_MOVE'and STATE='APPLIED'and ACTOR=p_actor;
    exception when no_data_found then raise_application_error(-20890,'DEFER_HU_APPLIED_ROOT_RESULT_REQUIRED');end;
   else p_result:=existing.RESULT_JSON;end if;
   return;"""
files[d+"015_wait_replay.sql"]=t.replace(needle,replacement)
p=d+"apply.sql";files[p]=Path(p).read_text(encoding="utf-8")+"@@015_wait_replay.sql\n"
p=d+"checkpoint.json";v=json.loads(Path(p).read_text(encoding="utf-8"));v["state"]="APPLIED_VALID_REPLAY_CORRECTION_PREPARED"
v["replay_correction"]="1063 same final APPLIED root result includes outbox_id; immutable WAIT_RUN remains pre-root projection; retained task1149/no duplicate plan"
v["sha256"].update({p:hashlib.sha256(t.encode()).hexdigest()for p,t in files.items()});files[p]=json.dumps(v,indent=2)
p="wiki/database/retailcase_ni072_nested_hu_wait_20261013.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n1063: corrected narrow locks plan positiveRollback succeeded; committed Rootplan1149/1HU/outbox5131. Replay returned pre-outbox WAIT_RUN projection, mismatch detected. Correct015 returns authoritative final APPLIED Root.RESULT_JSON after originalrequest/currentactor checks. No WAIT_RUN rewrite; recovery reads existing appliedplan and proceeds PLANNED. P20H20/retainedroot8 preserved.\n"
p="wiki/index.md";files[p]="- [Replay1063](database/retailcase_ni072_nested_hu_wait_20261013.md): original1149/1HU alreadyPLANNED; replay now finalRootoutboxcache, correction prepared/no duplicate.\n"+Path(p).read_text(encoding="utf-8")
p="wiki/log.md";files[p]=Path(p).read_text(encoding="utf-8")+"\n- checkpoint1063: plan1149 committed afterpositiveRollback; first/replay outbox field mismatch in WAITprojection, prepared015 currentactor/finalRootresult; recoveredsameplan in source1057, no newstock or task.\n"
print(json.dumps(files,ensure_ascii=True))
