from pathlib import Path
import json,re,hashlib
before=Path("tmp/865_wave_body.sql").read_text(encoding="utf-8")
source=re.sub(r"\n[ \t\r]*\n(?:[ \t\r]*\n)+","\n\n",before)
start=source.index('   -- Multiple retained bindings on the same selected physical stock require a')
end=source.index('   select REMAIN,STOCK_VERSION into v_source_p,v_source_ver',start)
source=source[:start]+"""   -- Every retained reservation is captured in old_a and verified separately.
   -- One representative binding selects physical stock; original whole arrival
   -- moves all captured owners, including multiple bindings of this same owner.
"""+source[end:]
d="db/migrations/2026-10-13_ni032_same_source_bindings/"
mid="2026-10-13-866-ni032-same-source-bindings"
files={d+"000_before_wave.sql":before,d+"001_wave.sql":source,
d+"002_ledger.sql":f"""merge into RRL_SCHEMA_MIGRATIONS t using(select '{mid}'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Retain separately versioned same-stock owner bindings in original whole-pallet arrival',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
""",
d+"apply.sql":"@@001_wave.sql\n@@002_ledger.sql\n",
d+"rollback.sql":f"@@000_before_wave.sql\nupdate RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='{mid}';\n/\n",
d+"verify.sql":"select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_STOCK_WAVE_CMD';\nselect OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_STOCK_WAVE_CMD';\n",
d+"checkpoint.json":json.dumps({"migration_id":mid,"state":"PREPARED","before_sha256":hashlib.sha256(before.encode()).hexdigest(),"after_sha256":hashlib.sha256(source.encode()).hexdigest(),"target":"RABAEV/orcl"},indent=2)}
page="""# NI03.2: несколько резервов одного источника

Migration866 подготовлена. Existing RRL_STOCK_WAVE_CMD сохраняет полный old_a всех own bindings, точные release_quantity/version/current owner и ordered stock closure. Старый отказ PARTIAL_TARGET_DISTINCT_RETAINED_SOURCE_REQUIRED убран: несколько retained reservation на одном UID/cell не означают несколько физических паллет.

Representative source сохраняет собственную BASE_QTY/version; не заменяется суммой чужих резервов. Все остальные own bindings остаются в original release/closure plan; whole TASK_COMPLETE использует существующий полный transfer план владельцев. Последующая remaining_for_task определяется по реально доставленному целевому резерву, не по одному representative id.

Нет объединения строк резерва, DML остатков, изменения public signature/stock writer. Current captured865 / SHA / paired rollback; fresh same-source positive, replay/rollback/native compilation ещё ожидают. [SQL](../../db/migrations/2026-10-13_ni032_same_source_bindings/apply.sql).
"""
files["wiki/database/nicora_ni032_same_source_bindings_20261013.md"]=page
p=Path("wiki/index.md");files[str(p)]="- [NI03.2 same-source866](database/nicora_ni032_same_source_bindings_20261013.md): prepared existing full binding closure/one physical source; live proof pending.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");files[str(p)]=p.read_text(encoding="utf-8")+"\n- 2026-10-13 prepared866 same-source retained owner bindings: captured865/SHA/paired rollback, original full old_a checks retained, only unsupported count refusal removed. Native apply/case pending; no closure claim.\n"
case=Path("scripts/case835_sequential_sources.py").read_text(encoding="utf-8").replace("835","867")
case=case.replace("for source_uid in (lot,extra):","for source_uid in (lot,lot):")
case=case.replace("assert q.fetchone()==(8,6)","assert q.fetchone()==(8,0)")
case=case.replace("assert q.fetchone()==(20,10)","assert q.fetchone()==(20,16)")
case=case.replace('assert len(next_rows)==1 and next_rows[0][1]==6,next_rows','assert len(next_rows)<=1,next_rows')
case=case.replace('"next_rt":int(next_rows[0][0])','"next_rt":int(next_rows[0][0])if next_rows else None')
case=case.replace('PASS867 target4 + own6/6 -> own source2/6 -> whole20 receipt -> original next demand6 -> target own12/other8; same replay, untouched source8/H0; cleanup follows','PASS867 same UID two own bindings6/6 retain2/6; one whole20 delivers own8 and other8; target own12/other8 and replay preserved; cleanup follows')
files["scripts/case867_same_source.py"]=case
print(json.dumps(files,ensure_ascii=True))
