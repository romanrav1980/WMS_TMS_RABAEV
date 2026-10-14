from pathlib import Path
import json,hashlib
d="db/migrations/2026-10-13_ni041_repack_clock/";mid="2026-10-13-011-ni041-repack-clock";files={}
before=Path("tmp/1058_rrl_hu_pack_clock_package_body.sql").read_text(encoding="utf-8")
old="kind not in('HU_ATTACH','HU_REPACK')";assert before.count(old)==1
fixed=before.replace(old,"kind not in('HU_ATTACH','HU_REPACK','HU_REPACK_SLOT')")
files[d+"000_before.sql"]=before;files[d+"001_clock.sql"]=fixed
files[d+"002_ledger.sql"]=f"""merge into RRL_SCHEMA_MIGRATIONS t using(select '{mid}'MIGRATION_ID from dual)s on(t.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing box packing clock accepts actual HU_REPACK_SLOT root command; nonBOX remains no clock, root/state/actor/anchor checks preserved',sysdate,user,'apply.sql','rollback.sql','APPLIED');
/
"""
files[d+"apply.sql"]="@@001_clock.sql\n@@002_ledger.sql\n";files[d+"rollback.sql"]="@@000_before.sql\n"
files[d+"verify.sql"]="select NAME,TYPE,LINE,TEXT from USER_ERRORS where NAME='RRL_HU_PACK_CLOCK';\n"
files[d+"checkpoint.json"]=json.dumps({"migration_id":mid,"state":"PREPARED","target":"RABAEV/orcl","source_capture":1058,"recovery":"single package body paired rollback/no data or database copy","sha256":{p:hashlib.sha256(t.encode()).hexdigest()for p,t in files.items()}},indent=2)
page="""# NI04.1 — начало упаковки при слотовой переупаковке
1059 PREPARED, migration2026-10-13-011-ni041-repack-clock. Live1058 captured.

Actual1057 на сохранённом1002 грузе: HU_REPACK_SLOT→existingHU_ATTACH delegate→RRL_HU_PACK_CLOCK отверг реальный Root kind, разрешая только HU_ATTACH и несуществующее здесь HU_REPACK. Корневое движение полностью откатилось, P20H20 и CASE/root версии сохранены; source factory не запускалась.

Малое исправление добавляет действующий HU_REPACK_SLOT к проверке CLOCK. Root context/transaction/IN_FLIGHT/actor/heldHU anchor сохраняются; clock создаётся только при первой фактической упаковке пустого BOX. Для ROLL_CAGE/CASE не создаётся фиктивный упаковочный цикл. Existing link/measure/root validation сохраняются. Live apply/continuation pending. Pair rollback saved.
"""
files["wiki/database/nicora_ni041_repack_clock_20261013.md"]=page
for p,note in [
("wiki/index.md","- [Clock1059](database/nicora_ni041_repack_clock_20261013.md): actual slottedrepack refused by oldclock enum, prepared minimal correction, P20H20 retained.\n"),
("wiki/log.md","\n- checkpoint1059: native HU1057.PACK failed BOX_PACKING_ATTACH_REQUIRED, no goods/versions committed. Actual oldclock captured1058; actualHU_REPACK_SLOT enum correction prepared with pairedrollback beforeapply.\n")]:
 t=Path(p).read_text(encoding="utf-8");files[p]=note+t if p.endswith("index.md") else t+note
print(json.dumps(files,ensure_ascii=True))
