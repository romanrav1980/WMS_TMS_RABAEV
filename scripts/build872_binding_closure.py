from pathlib import Path
import json,re,hashlib
read=lambda p:Path(p).read_text(encoding="utf-8")
before_bind=read("tmp/870_bind_body.sql");before_next=read("tmp/871_continuation_body.sql")
bind=re.sub(r"\n[ \t\r]*\n(?:[ \t\r]*\n)+","\n\n",before_bind)
bind=bind.replace('declare pt RRL_PICK_TASK%rowtype;covered_target number;begin','declare pt RRL_PICK_TASK%rowtype;covered_target number;incoming_other number:=0;begin',1)
needle="    p_plan.put('target_covered',RRL_STOCK_PLAN_HELPER.decimal_text(covered_target));"
assert bind.count(needle)==1
bind=bind.replace(needle,needle+"""
    if p_task.QTY_MODE='PALLET' then
     select nvl(sum(BASE_QTY),0) into incoming_other from RRL_STOCK_RESERVATION
      where UID_PALLET=p_task.UID_PALLET and CELL=p_task.FROM_CELL
       and SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=rt.PICK_WAVE_ID
       and SOURCE_LINE_ID=rt.PICK_TASK_ID and RESERVATION_DOMAIN='PICKING'
       and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING')
       and RESERVATION_ID!=rt.SOURCE_RESERVATION_ID and BASE_QTY>0;
    end if;
    p_plan.put('expected_target_covered',RRL_STOCK_PLAN_HELPER.decimal_text(covered_target+incoming_other));
""",1)
old="RRL_STOCK_PLAN_HELPER.decimal_text(total)!=p_plan.get_string('target_covered')"
assert bind.count(old)==1
bind=bind.replace(old,"RRL_STOCK_PLAN_HELPER.decimal_text(total)!=p_plan.get_string('expected_target_covered')")
continuation=re.sub(r"\n[ \t\r]*\n(?:[ \t\r]*\n)+","\n\n",before_next)
old="   select least(BASE_QTY,p_qty) into v_incoming_owned from RRL_STOCK_RESERVATION where RESERVATION_ID=rt.SOURCE_RESERVATION_ID;"
assert continuation.count(old)==1
continuation=continuation.replace(old,"""   if p_task.QTY_MODE='PALLET' then
    select least(nvl(sum(BASE_QTY),0),p_qty) into v_incoming_owned from RRL_STOCK_RESERVATION
     where UID_PALLET=p_task.UID_PALLET and CELL=p_task.FROM_CELL
      and SOURCE_DOC_TYPE='PICK_WAVE' and SOURCE_DOC_ID=rt.PICK_WAVE_ID
      and SOURCE_LINE_ID=rt.PICK_TASK_ID and RESERVATION_DOMAIN='PICKING'
      and RESERVATION_KIND='HARD' and STATUS in('ACTIVE','ALLOCATED','PICKING') and BASE_QTY>0;
   else
    select least(BASE_QTY,p_qty) into v_incoming_owned from RRL_STOCK_RESERVATION where RESERVATION_ID=rt.SOURCE_RESERVATION_ID;
   end if;""")
d="db/migrations/2026-10-13_ni032_shared_binding_closure/";mid="2026-10-13-872-ni032-shared-binding-closure"
files={d+"000_before_bind.sql":before_bind,d+"000_before_continuation.sql":before_next,d+"001_bind.sql":bind,d+"002_continuation.sql":continuation,
d+"003_ledger.sql":f"""merge into RRL_SCHEMA_MIGRATIONS t using(select '{mid}'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit consumer post-arrival closure accounts for all same-owner bindings on whole source; continuation uses total own incoming',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
""",d+"apply.sql":"@@001_bind.sql\n@@002_continuation.sql\n@@003_ledger.sql\n",d+"rollback.sql":f"@@000_before_bind.sql\n@@000_before_continuation.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='{mid}';\n/\n",
d+"verify.sql":"select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME in('RRL_STOCK_REPL_BIND','RRL_STOCK_REPL_CONTINUATION');\nselect OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_REPL_BIND','RRL_STOCK_REPL_CONTINUATION');\n",
d+"checkpoint.json":json.dumps({"migration_id":mid,"state":"PREPARED","target":"RABAEV/orcl","before_sha256":{"bind":hashlib.sha256(before_bind.encode()).hexdigest(),"continuation":hashlib.sha256(before_next.encode()).hexdigest()},"after_sha256":{"bind":hashlib.sha256(bind.encode()).hexdigest(),"continuation":hashlib.sha256(continuation.encode()).hexdigest()}},indent=2)}
p=Path("wiki/database/retailcase_ni032_same_source_bindings_20261013.md");files[str(p)]=read(p)+"""
## План состава872

869 applied VALID; fresh867 выдал одно физическое задание, но execute_bind отказал CLOSURE_CHANGED до commit; own finally cleanup. Причина: pre-arrival target coverage excludes representative only; whole arrival одновременно переносит остальные own source bindings, поэтому post-target coverage увеличивается.872 prepared captures exact expected_target_covered = prior target + other own incoming only for whole PALLET. Runtime сохраняет equality check и остальные status/quantity/fact/owner guards. Root whole transfer closure captures all reservation identities/versions; no guard bypass.

Continuation whole PALLET subtracts sum of original own active HARD on same UID/fromcell, not only representative row. BASE unchanged. Потребность другого владельца не включается; нет fake continuation, если все own резервы прибыли. Captured870/871/SHA/paired rollback, live/fresh pending.
"""
p=Path("wiki/index.md");files[str(p)]="- [NI03.2 binding closure872](database/retailcase_ni032_same_source_bindings_20261013.md): prepared exact expected coverage/all own incoming;869VALID, old execution rightly rolled back.\n"+read(p)
p=Path("wiki/log.md");files[str(p)]=read(p)+"\n- 2026-10-13 prepared872: exact explicit post-arrival target coverage and whole own incoming continuation.869 appliedVALID; fresh867 failed closure before commit/owncleanup, not passed. No equality/owner guard removed. Capture870871/checkpoint.\n"
print(json.dumps(files,ensure_ascii=True))
