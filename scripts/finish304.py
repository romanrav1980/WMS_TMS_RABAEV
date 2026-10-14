from pathlib import Path
import json,re
out={};d=Path("db/migrations/2026-10-11_ni061_recurrent_loss")
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");j=json.loads(p.read_text(encoding="utf-8"))
sources=[n for n in j["components"]if re.search(r"create\s+or\s+replace\s+package\s+RRL_STOCK_INTERWARE_SHORT_CMD\s",(p.parent/n).read_text(encoding="utf-8"),re.I)]
assert len(sources)==1,sources;j["components"][j["components"].index(sources[0])]= "../2026-10-11_ni061_recurrent_loss/002_command_current.sql"
j["startup_scripts"].append("../2026-10-11_ni061_recurrent_loss/001_event_unit_keys.sql")
j["additional_scripts"] += ["../2026-10-11_ni061_recurrent_loss/002_command_current.sql","../2026-10-11_ni061_recurrent_loss/003_unit_guard.sql"]
out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
out[(d/"004_ledger.sql").as_posix()]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-304-recurrent-loss-event-keys'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Loss/recovery journals keyed by event and unit with active-loss admission',sysdate,user,'db/migrations/2026-10-11_ni061_recurrent_loss/apply.sql','db/migrations/2026-10-11_ni061_recurrent_loss/rollback.sql','APPLIED','Both newPK VALID, old2 loss+2 recovery rows retained, active0, forgeddirectinsertdenied/allVALID/P20H20. Same UNITmutex and native recapture. Second physical cycle remains acceptance pending.');
commit;
"""
p=Path("wiki/database/retailcase_ni061_recurrent_loss_20261011.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\nПрименено вdev: оба составныхPK ENABLED, прежние loss2/recovery2rows иqty2/2 сохранены; unresolved0, direct journal INSERT denied20863; все nativeVALID/protected20-20. scripts/verify304.py. Старый customer1+2 case сохранён, второй физический цикл ещё не выполнен. SQL: текущий доступ по physicalkey/LOSS/OP PK сохраняется; root recapture bounded10000, долгие lookup при росте истории — inventory owner, измерить на настоящем втором цикле вместо глобального сканирования.\n"
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 11.10.2026 304 APPLIED: event+unit keys/livehistory2+2 retained, active0/directforgery20863/allVALID/P20H20. Native source/frozenunit trigger and manifest maintained. Second physical cycle pending, partial recovery next.\n"
p=Path("wiki/index.md");out[p.as_posix()]=p.read_text(encoding="utf-8").replace("304 event+unit journal keys/current active-loss admission; physical secondcycle pending.","304 APPLIED event+unit keys/history2+2 retained/native active-loss admission; physical secondcycle pending.",1)
p=Path("wiki/runbooks/retailcase_active_work.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\nLatest304 native loss/recovery event+physicalkey PK +SHORT_CMD active-loss recapture/strong exact frozen/currentUNIT insertguard; old2+2 facts retained/active0/allVALID/P20H20. Manifest304; Root301/NEXT302/current qtywriter unchanged. Full secondphysicalcycle pending; partial recovery next. APIserv303 before304 table recompilation, restart nextchangedHTTP; no sourcebirth replays.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"));next(x for x in j["increments"]if x["id"]=="NI06.1").setdefault("implementedSlices",[]).append("304 event+physicalunit loss/recovery journals/currentactiveLoss/nativefrozenversion guard; oldhistretained/secondphysicalcycle pending");out[p.as_posix()]=json.dumps(j,indent=2)+"\n"
qroot=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(qroot/"NI06.1/304_recurrent_event_keys.md").as_posix()]="""# Qwen304 recurrent loss event keys
Read wiki/database/retailcase_ni061_recurrent_loss_20261011.md. Same physicalkey may have multiple immutable event rows; never delete oldbook.
Own actual secondcycle requires legitimate return/newshipment/newpartialreceipt, not forged UID/status or sourcebirth replay. New native shortage confirmation after old APPLIED sameLOSS recovery permitted; unresolved old/new loss rejects source command and ordinary unit movement. Concurrent sameunit capture/confirm mustnot create2unresolved facts; existing UNIT60 and underlockrecapture authoritative.
Capturedmissing key/qty/UOM/version/currentoriginalUID/ISSUED/noH requiredbytrigger; arbitrarydirectINSERT20863, update/deleteimmutable. Composite duplicate sameevent/key fails. Newevent doesnotduplicate stock. Foreignware/revokedrights/replay/collision preserveoldjournals.
Rollback singlekey conversion refuses existing recurrentkeys. Report actualsecondphysicalcycle evidence separately; currently schema/history/currentactive0 only verified.
"""
print(json.dumps(out))
