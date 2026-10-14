from pathlib import Path
import json,hashlib
out={};folder=Path("db/migrations/2026-10-11_ni042_weight_box_case")
ledger="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-182-weighted-case-label'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Weighted box scan adapts to existing CASE_PICK_CONFIRM, server cumulative KG, native label/unit/own HARD validation',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_box_case/apply.sql','db/migrations/2026-10-11_ni042_weight_box_case/rollback.sql','APPLIED',
'Actual wave415 CASE1055 CASE.WEIGHT182:1055 picked9.8KG/unit1/exact replay/changed label409; source total19.6 H9.8; native return/count cleanup/waveDONE/original135 P20H20; TSD durable weighted intent; bounded fixture no volume cap; variable-box capacity remains separate');
commit;
"""
out[str(folder/"003_ledger.sql")]=ledger
p=folder/"apply.sql";out[str(p)]=p.read_text(encoding="utf-8")+"@@003_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["components"]=[x.replace("../2026-10-10_ni042_composition_epoch/009_case_birth.sql","../2026-10-11_ni042_weight_box_case/002_case_contract.sql")for x in m["components"]]
m["components"].insert(0,"../2026-10-11_ni042_weight_box_case/001_scan.sql");m["packages"].append("RRL_CASE_WEIGHT_SCAN")
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/retailcase_ni042_weighted_case_20261011.md"]="""# NI04.2: весовая коробка в существующем CASE
182 APPLIED. Один новый вход /api/case-pick/tasks/{task}/lines/{line}/weighted-box адаптирует оригинальный CASE_PICK_CONFIRM; второй запас/коробочный реестр не создаётся.
Сервер получает массу из native GS1 decoder, проверяет нынешний SKU/KG/current policy, физическую коробку и свой HARD по PICK_WAVE/PICK_TASK/current cell. Накопленный факт = previous PICKED_QTY + label netKG. Для маркированного SKU API требует ровно все текущие profile scans и ту же physical key. Native RRL_CASE_WEIGHT_SCAN проверяет label/GTIN/serial/mass/delta/policy/one unit/own HARD при compile и перед effect под существующими locks. Weighted SKU требует этот вход, ручной generic fact без label отказан.
Replay сравнивает original weighted_confirmation/actor/source и возвращается через native posting, сохраняя current warehouse authorization. Чужой payload того же operation_id409.
ТСД использует текущую SKU policy, отдельные поля применимых маркировочных профилей, блокирует ручной факт для weighted, сохраняет route+raw barcode/body в прежнем durable intent. Повтор использует исходный payload. Старые intents без route по-прежнему /confirm.
scripts/ni042_weighted_case_existing_case.py: own wave415/CASE1055/QW182FCD84E6DE1/CASE.WEIGHT182:1055. Две physical boxes по9.8KG/P19.6; own HARD9.8; actual scan reserved box→CASE9.8/unit1, source total P19.6/H9.8 retained. Exact replay journal unchanged; changed barcode409. Native carrier return/tare cancel/wave finish DONE/count0; original135 P20H20 unchanged.
Первый synthetic check digit автора был ошибочен; decoder правильно отказал. Второй/третий launch выявили существующее ограничение BOX→KG static conversion в RRL_STOCK_REPL_CAPACITY. Последний fixture выбрал явно неограниченную MAX_VOLUME=null для отдельного scanner slice: вместимость переменной коробки этим не принята. Другой scan отказан потому что native reservation выбрал вторую physical key по установленному порядку; нельзя выбирать невключённую в own HARD коробку. Автор исправлен на действительно reserved identity. Native cleanups первых волн412/413/414 CANCELLED, stocks0; empty1054 cancelled через allow_empty, held tare освобождена. Не было прямого изменения P/H.
Initial helper compilation used unsupported json_scalar_t.get_string; fixed json_array_t.get_string(0), repeat apply all7 statements0errors, USER_ERRORS empty. Fresh source/checkpoint/paired rollback preserved.
Quality PASS541 files/0 cycles/76 existing debt/24 tests/bothTS; JS and UTF-8 checks PASS. SQL44h4ct3b0gh4z weighted snapshot17.906ms/2 cold reads. Decision: physical-key/indexed reservation + bound2 rows retained; inventory owns native selected-key lookup/plan check if latency recurs on pilot, not an industrial load certificate.
Open: exact physical-box capacity/replenishment, marked weighted full scenario, real scales/last-box rules. Whole NI04.2 remains in_progress.
"""
for path,line in [
 ("wiki/index.md","- [Весовая коробка в CASE](database/retailcase_ni042_weighted_case_20261011.md):182 server-derived9.8KG/existing CASE single writer/native own HARD/TSD durable retry; exact box capacity next."),
 ("wiki/log.md","2026-10-11:182 APPLIED/scoped physical weighted CASE1055/wave415 qty9.8/unit1/replay/no extra movement/native cleanup. UI per-profile fields and saved route. Quality541/0/76 PASS; physical box volume/replenishment gap remains."),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:182 native/server/TSD weighted scan to existing CASE_PICK_CONFIRM actual9.8KG/unit1/replay/refusal/cleanup. Existing static BOX→KG capacity gap identified; scanner fixture explicitly no volume cap. Exact physical-box capacity and last-box/scales/marked end-to-end remain open.")]:
 p=Path(path);out[str(p)]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"182_weighted_case.md")]="""# Qwen: 182 weighted CASE
Run scripts/ni042_weighted_case_existing_case.py with fresh own tag. Confirm actual19.6KG/two9.8boxes/own HARD9.8, scanner picks only reserved unit, server derives9.8, one physical unit moves/reservation follows, repeat journal unchanged, changed same OP409. Native carrier return/tare release/wave finish/count0/original13520/20. Confirm TSD policy-derived weighted mode, every profile input, durable raw barcode route/body replay. Direct generic confirmation lacking weighted label for enabled SKU must fail. Native helper compile VALID. Fixture MAX_VOLUME=null intentionally: variable weight-box capacity and scales not accepted. Report slow SQL and explicit decision. No direct balance writes.
"""
out[str(folder/"installed_sources.json")]=json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest().upper()for p in folder.glob("*.sql")},indent=2)+"\n"
print(json.dumps(out,ensure_ascii=True))
