from pathlib import Path
import json
out={};f=Path("db/migrations/2026-10-11_ni072_task_finish_time");data=json.loads(Path("tmp/context254.json").read_text(encoding="utf-8"))
summary=f"""# NI07.2: подтверждённые начала и окончания заданий
254 uses existing WarehouseTaskService.start writer/STARTED_AT_INSTANT TZ. Initial guessed FINISHED_AT_INSTANT did not exist; inspected live schema confirmed FINISHED_AT andresourceEVENT_AT naive. Added nullable TIMESTAMP WITH TIME ZONE FINISHED_AT_INSTANT without oldrow backfill. New source stage never interprets naive dates asUTC.
Small RRL_WTASK_FINISH_TIME_GUARD stamps SYSTIMESTAMP only at an existing accepted transition toDONE in the same row transaction. No extra SQL/resource locks/queue/calls. Existing domain authority/status/stockguards still decide whether completion allowed. Clock rollback follows original domain/stock transaction, duplicate existingDONE leaves same clock. Newborn clock injection, clearing/changing recordedinstant and silently stamping oldDONE are rejected20863. It records successful status transaction time, not physical hardware or driver event. Quantity root/writers/wareunit semantics unchanged.
Current DayReconciliation same READONLY snapshot uses aware start/finish only (DONE qualifier for finish), counts tasks involved in sourceORdestination warehouse once per report; not sum goods/employee hours. Oldstart date withoutinstant and finishwithoutinstant separate coveragecounts, no arbitrary daily assignment. UI labels 'с подтверждённым временем', unknown dates visible. No duration estimate/closedday inferred.
Migration2026-10-11-254-warehouse-task-finish-instant: column/guard/affected invalidpackage spec+body recompile, nativeVALID, pooledAPIrestart. Future completedtask records retained; rollback refuses any recordedfinish before droppingcolumn. Runtime required columns/startup/guard/recompile mirrors.
Actual new own{data['tag']} through original source factory, native marked inventorybirth3/codes6/HARD3/nativewave release. Original warehouse task{data['task_id']} WARE{data['source_ware']} explicit start viaexistingservice =>IN_PROGRESS/awarestart. TASK_COMPLETE3 full root executed thenouterrollback: oldstatus/start preserved/finishNULL/stock effects undone. Same fixedID thencommit andexactrepeat preserve newfinishinstant/result. Original bind/QC6/load/depart through existingowners same3units6codes ISSUED/sourceP0, targetplan{data['plan']} pending withoutnewquantity.
Dayboard sourceWARE returns awarestart1/finish1, actualHTTP200. Direct newclockclear andoldDONE953currentstamp denied20863/no changes. Protected P20H20 intact. Newsource fixture is controlled devbirth, no databasecopy or third quantitywriter; manual synthetic scans/start not actual hardware/government acceptance. Its targetWARE{data['target_ware']}/TT{data['target_trip']} awaiting samegoods for next warehouse-ready scenario.
Architecture5750cycles76/rawJSsyntax PASS/nativeerrors[]invalid[]. SQLday counts2.313/4.691ms2 andwarequery2.671ms2: retain existing warehouse/state/task indexes, aware range filtering +same snapshot, no new index from smallsamewarecase. Ownerfinance narrows/indices wareclock if periodscan grows. Generic source helpers/source254/build/docs must notrerun completed fixture; context254 preserved, no duplicate births.
"""
out["wiki/database/retailcase_ni072_task_times_20261011.md"]=summary;out[str(f/"README.md")]=summary
out[str(f/"004_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-254-warehouse-task-finish-instant'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Future warehouse task completion clock and same-snapshot operational day counts',sysdate,user,
'db/migrations/2026-10-11_ni072_task_finish_time/apply.sql','db/migrations/2026-10-11_ni072_task_finish_time/rollback.sql','APPLIED',
'Own4ecffb36dd/task979/WARE5265051/native awarestart/TASK_COMPLETE3 rootlate rollback/restored clock+quantity/fixedID repeat samefinish; nativeQC6/load-depart33569/same3units6codes/sourceP0/target33570 pending. OldDONE953 nobackfill/currentclockimmutable20863/dayaware start1finish1/HTTP/no closedday/nativeVALID/protected20-20. Architecture5750cycles76/JS.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@004_ledger.sql\n"
out[str(f/"verify.sql")]="""select COLUMN_NAME,DATA_TYPE from USER_TAB_COLUMNS where TABLE_NAME='RRL_WAREHOUSE_TASK'and COLUMN_NAME in('STARTED_AT_INSTANT','FINISHED_AT_INSTANT');
select TASK_ID,STATUS,STARTED_AT_INSTANT,FINISHED_AT_INSTANT from RRL_WAREHOUSE_TASK where TASK_ID in(979,953);
select OBJECT_NAME,OBJECT_TYPE,STATUS from USER_OBJECTS where OBJECT_NAME='RRL_WTASK_FINISH_TIME_GUARD';
"""
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
out[str(f/"000_before_manifest.json")]=p.read_text(encoding="utf-8")
m["required_columns"]["RRL_WAREHOUSE_TASK"]=list(dict.fromkeys(m["required_columns"].get("RRL_WAREHOUSE_TASK",[])+["FINISHED_AT_INSTANT"]))
m["startup_scripts"].append("../2026-10-11_ni072_task_finish_time/001_schema.sql")
m["additional_scripts"].extend(["../2026-10-11_ni072_task_finish_time/002_clock_guard.sql","../2026-10-11_ni072_task_finish_time/003_recompile.sql"])
out[str(p)]=json.dumps(m,indent=2)+"\n"
for path,line in [
("wiki/index.md","- [Дневные факты заданий](database/retailcase_ni072_task_times_20261011.md):254 existingawarestart/newimmutableDONEclock/same row TX/rollback+repeat/task979/day1-1/oldtimestamps unclassified/no stockwriter."),
("wiki/log.md","2026-10-11:254 actualschema finish timestamp wasnaive/no instant; addednullablefuture finishinstant/rowclockguard at acceptedDONE/sameTX/immutable/nobirthinjection oroldbackfill/existing statusauthority retained. Current dayaware start-finish counts/legacycoverage/UI. Own4ecffb36dd/979 originalrootbirth3/HARD3/start/complete3late rollback/clock+qty restored/sameIDrepeat stable/nativeQC6/loaddepart33569/current3units6codes/sourceP0/target33570pending/day1-1/old953no backfill20863/HTTP/protected20-20. NativeVALID/architecture5750cycles76JS/SQ L2.3134.6912.671ms retain warehouse/taskkeys; no indexduplication. RuntimeDDLguardrecompile mirrored; noqty secondwriter/closedday orrealhardware claim."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni07_2.md","11.10.2026:254 aware operational day taskstarted/finished counts usingoriginal start andfutureimmutabledoneclock, no olddate timezoneguess. Native979 complete3rootlate rollback/clockquantityrollback/samereplaythenexistingQC6/loaddepart/sourceP0/day1-1/API; actualdriver/hardware/outboundACK/dayclose notcertified.")
]:out[path]=Path(path).read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"))
next(x for x in j["increments"]if x["id"]=="NI07.2").setdefault("implementedSlices",[]).append("254 future immutable same-transaction warehouse task finishinstant/oldstartaware/day startfinish counts/unknownlegacytimes explicit/root rollback+repeat/no stockwriter")
j["firstChange"]="Continue shared warehouse readiness/cutoff coordination on original interwarehouse source254 and approved transport times; external lifecycle/real ACK and full increments remain."
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
p=Path("wiki/runbooks/retailcase_active_work.md");s=p.read_text(encoding="utf-8")
s=s.replace("Current native manifest250.","Current native manifest254 (time250 +regulatorywarehouseindex252 +transportplanneddefault253 +warehousefuturefinishclock254).")
s=s.replace("Current app251","Current app254 day-aware taskfacts plus252regulatoryqueue; app251")
s+="\nLatest actual own source254tag4ecffb36dd/WARE5265051/target55265051/task979/TT33569→33570/sourceP0/current3 originalunits6codesISSUED7. tmp/context254.json preserved. Original targetplan awaiting receive/placement for shared readiness next. APIserv254b. No rerun source factory/docs builders; duplicates wouldbe newbirths.\n"
out[str(p)]=s
root=next(p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md"))
out[str(root/"NI07.2"/"254_task_times.md")]="# Qwen:254 — время задания\nColumnfuturefinishTZ guard acceptedtransitionDONE sameTX, no newresource locks/quantity/stockwriter. OldDONE null remainsunclassified; rejectbirth injection/directclear/change/backfill. Resource/nonresource/nativeSAP/HU/normal actual statusowners mustwork; rowtype recompile/poolrestart. Native979 own3markedactualtask late rootrollback restoresclock+qty thencommit/fixedIDrepeat sameclock/start1finish1/old953 untouched/HTTP. Residualchild clonedrow mustnotinherit actualfinish fromdoneparent. DailycountWAREfromORto taskonce, no goods/employeehour sum; unknowntimes explicit. Other nativeTaskType modes independentQwen remain. Source254 factory alreadydone/currenttarget33570 pending, no repeatbirths. Architecture5750cycles76/JS/SQ Lbounddecision.\n"
print(json.dumps(out,ensure_ascii=True))
