from pathlib import Path
import json,hashlib
read=lambda p:Path(p).read_text(encoding="utf-8");d="db/migrations/2026-10-13_ni072_case_wait_identity/";files={}
for n in("RRL_ST_DEFER_CASE_WAIT","RRL_ST_DEFER_WAIT_API"):
 raw=read("tmp/980_"+n.lower()+".sql");files[d+"000_before_"+n.lower()+".sql"]=raw
body="\n".join(x for x in files[d+"000_before_rrl_st_defer_case_wait.sql"].splitlines()if x.strip())+"\n"
needle="or t.SOURCE_TASK_ID!=p.CASE_TASK_ID or t.UID_PALLET"
assert body.count(needle)==1
body=body.replace(needle,"or(t.SOURCE_TASK_ID is null or(t.SOURCE_TASK_ID!=p.CASE_TASK_ID and t.SOURCE_TASK_ID!=t.TASK_ID))or t.UID_PALLET")
needle="w.SOURCE_DOC_TYPE='ST_DEFER_CASE'and w.SOURCE_TASK_ID=ct.CASE_PICK_TASK_ID"
assert body.count(needle)==1
body=body.replace(needle,"w.SOURCE_DOC_TYPE='ST_DEFER_CASE'and exists(select 1 from RRL_ST_DEFER_WAIT_PLAN cp where cp.TASK_ID=w.TASK_ID and cp.CASE_TASK_ID=ct.CASE_PICK_TASK_ID)")
files[d+"001_scope.sql"]=body
body="\n".join(x for x in files[d+"000_before_rrl_st_defer_wait_api.sql"].splitlines()if x.strip())+"\n"
needle="values(task_id,'PUTAWAY','MANUAL',src_case,'ST_DEFER_CASE'"
assert body.count(needle)==1
body=body.replace(needle,"values(task_id,'PUTAWAY','MANUAL',task_id,'ST_DEFER_CASE'")
files[d+"002_planner.sql"]=body
files[d+"003_sequence.sql"]="""-- Affected dev metadata only: avoid future self-task IDs colliding with the two earlier CASE-source IDs.
-- Sequence gaps are retained; rollback never rewinds a used task sequence.
declare max_source number;next_task number;iterations number:=0;begin
 select nvl(max(SOURCE_TASK_ID),0)into max_source from RRL_WAREHOUSE_TASK where TASK_SOURCE='MANUAL'and TASK_TYPE='PUTAWAY';
 loop
  select RRL_WAREHOUSE_TASK_SQ.nextval into next_task from dual;iterations:=iterations+1;
  exit when next_task>max_source;
  if iterations>=10000 then raise_application_error(-20886,'WAIT_TASK_SEQUENCE_CATCHUP_BOUND_REQUIRED');end if;
 end loop;
end;
/
"""
files[d+"004_compile.sql"]=read("db/migrations/2026-10-13_ni072_case_wait/008_compile.sql")
files[d+"005_ledger.sql"]="""merge into RRL_SCHEMA_MIGRATIONS t using(select '2026-10-13-006-ni072-case-wait-identity'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Waiting physical task owns its self source task ID; original CASE ID remains in immutable plan; permits repeated rescheduling without changing old records',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
files[d+"apply.sql"]="@@001_scope.sql\n@@002_planner.sql\n@@003_sequence.sql\n@@004_compile.sql\n@@005_ledger.sql\n"
files[d+"rollback.sql"]="@@000_before_rrl_st_defer_case_wait.sql\n@@000_before_rrl_st_defer_wait_api.sql\n@@004_compile.sql\n-- Sequence gaps and completed history are not reversed.\n"
files[d+"verify.sql"]="select TASK_ID,SOURCE_TASK_ID,SOURCE_DOC_TYPE from RRL_WAREHOUSE_TASK where SOURCE_DOC_TYPE='ST_DEFER_CASE'order by TASK_ID;\nselect NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME not like 'BIN$%';\n"
files[d+"checkpoint.json"]=json.dumps({"migration_id":"2026-10-13-006-ni072-case-wait-identity","state":"PREPARED","target":"RABAEV/orcl","recovery":"affected sources980 + paired rollback; retain task sequence gaps/history","sha256":{p:hashlib.sha256(b.encode()).hexdigest()for p,b in files.items()}},indent=2)
page="""# NI07.2 — повторное ожидание того же CASE

Migration2026-10-13-006-ni072-case-wait-identity PREPARED. Actual977 повторно переназначил retained CASE1129 на следующий плановый день; новое WHT insert00001 refused before stock move.

Live979: RRL_WAREHOUSE_TASK_U2 — unique INDEX, не constraint. Keys: TASK_SOURCE, NVL(SOURCE_TASK_ID,-1), NVL(SOURCE_MOVEMENT_ID,-1), TASK_TYPE, special SAP UID / otherwise parent ID. FirstCASE implementation used CASE id as SOURCE_TASK_ID, поэтому второй MANUAL/PUTAWAY для того же CASE конфликтовал с прошлым завершённым заданием.

New CASE waiting uses SOURCE_TASK_ID=TASK_ID, как прежняя flat waiting branch. Original CASE remains explicit CASE_TASK_ID in immutable WAIT_PLAN; source read/command validates that exact CASE and current WHT. Two earlier dev records retain their original source ID and remain replay-compatible. No PARENT_TASK_ID is invented for sequential full movement: it is not partial residual quantity. One-time bounded dev sequence catchup past observed MANUAL PUTAWAY maxsource1130 prevents collisions with those earlier CASE ids; no rewind/copy/history rewrite or stock change. Subsequent tasks use the monotonic self ID. Open CASE task detection uses authoritative plan CASE_TASK_ID plus carrier identifier.

Capture980/SHA/paired code rollback; unused numeric gaps are normal retained allocation, not reversed. Need compile and retained977 planning/physical finish through current one FF-version writer974. FullNI07.2 still open. Previous QC signature expectation in975 harness was wrong: whole movement preserves goods composition hash; actual976 currentCASE3/FF3 with same signature is correct. Prior claims about automatic invalidation of every old QC approval on any relocation were unproven and are superseded by current-policy evidence; no oldapproval fixture was tested.
"""
files["wiki/database/retailcase_ni072_case_wait_identity_20261013.md"]=page
p="wiki/index.md";files[p]="- [CASE повторное ожидание981](database/retailcase_ni072_case_wait_identity_20261013.md): prepared original-index-compatible self-task identity/explicit CASE plan, retained history.\n"+read(p)
p="wiki/log.md";files[p]=read(p)+"\n- 2026-10-13 checkpoint981:974 applyVALID;975 actualCASE12 forwardRootrollback/commit/cache/CT3=FF3/oldfacts, final wrongcompositionhash expectation corrected976.977 nativeSTdecision advancedday/version but waiting insert00001 refused.979 currentindexkeys observed;981 self-tasksource/explicit CASEplan + boundedone-time seqcatchup1130, no parent/residual/historyrewrite/stockchange; checkpoint beforeapply.\n"
print(json.dumps(files,ensure_ascii=True))
