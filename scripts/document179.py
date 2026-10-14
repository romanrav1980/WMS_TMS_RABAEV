import json,hashlib
from pathlib import Path
out={};folder=Path("db/migrations/2026-10-11_ni042_weight_box_capture")
ledger="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-179-weight-box-physical-capture'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Serialized weighted boxes in existing physical unit registry, exact GS1 net KG, independent WMS policy flag',sysdate,user,
'db/migrations/2026-10-11_ni042_weight_box_capture/apply.sql','db/migrations/2026-10-11_ni042_weight_box_capture/rollback.sql','APPLIED',
'Own QW1794B408748 born P9.8KG/H0/unit1/codes0; exact replay, duplicate and mass mismatch refused without orphan lot; native count cleanup; original135 P20H20 preserved; changed packages VALID; SAP/CASE scanner remain next');
commit;
"""
out[str(folder/"005_ledger.sql")]=ledger
p=folder/"apply.sql";out[str(p)]=p.read_text(encoding="utf-8")+"@@005_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
m["components"]=[x.replace("../2026-10-11_ni041_slot_repack/006_root_contract.sql","../2026-10-11_ni042_weight_box_capture/003_root_contract.sql").replace("039_unit_core.sql","../2026-10-11_ni042_weight_box_capture/004_unit_contract.sql")for x in m["components"]]
m["components"].append("../2026-10-11_ni042_weight_box_capture/002_decoder.sql")
m["packages"].append("RRL_WEIGHT_BOX_READ");m["additional_scripts"].append("../2026-10-11_ni042_weight_box_capture/001_schema.sql")
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
p=Path("wiki/database/retailcase_ni042_weight_box_capture_20261011.md");s=p.read_text(encoding="utf-8").replace("подготовлена.","APPLIED в RABAEV/orcl.")
s=s.replace("Реализация и живые случаи pending.","""Живой случай scripts/ni042_weight_box_capture_case.py: QW1794B408748 / WEIGHT179.BIRTH:4b408748 дал P9.8KG/H0, одну AVAILABLE физическую единицу, government codes0. Exact replay; duplicate birth409 и масса9.7 вместо9.8 отклонены без orphan pallet. Cleanup только штатным INVENTORY_COUNT, исходный135 P20H20 сохранён.
Первый авторский запрос использовал неверное имя UNIT_STATUS; исправлен на реальное STOCK_STATUS, первая собственная коробка снята штатным count (cleanup179_first_case.py). Второй прогон обнаружил необработанное исключение в авторском negative-case; cleanup finally выполнен. Третий прогон полностью PASS. Unique physical constraint refusal переведён в явный PHYSICAL_UNIT_ALREADY_RECEIVED409, остальные IntegrityError не скрываются.
Карточка SKU содержит независимый checkbox; запрет включения для невесового/неKG товара даёт422. Прежние клиенты без нового поля сохраняют старую настройку.
Quality gate PASS:538 Python files/0 cycles/76 existing debt/24 tests/both TypeScript builds. Native changed-object specs/bodies VALID.
SQL: current policy+lot c1kn25gbvsg82 0.962ms/5; flag/profile selects0.355–1.984ms. Решение: сохранить PK/bounded lookups, не добавлять индексы по флагу; 10000boxes command bound; batching per-box metadata owned inventory backlog для промышленных объёмов. Это не нагрузочный сертификат.
Rollback сохраняет аддитивные поля/историю и запрещён при включённой политике; копия базы не создавалась.""")
out[str(p)]=s
p=Path("wiki/index.md");s=p.read_text(encoding="utf-8");s+="\n- [Серийные весовые коробки](database/retailcase_ni042_weight_box_capture_20261011.md):179 native GS1 netKG/current SKU flag/existing physical registry/P9.8/unit1/replay/no duplicate birth; SAP/CASE next.\n";out[str(p)]=s
p=Path("wiki/log.md");out[str(p)]=p.read_text(encoding="utf-8")+"\n2026-10-11: NI04.2 slice179 APPLIED: independent weighted-box SKU setting, native GS1 decoder, inventory/MES existing physical capture; own P9.8KG/unit1/replay/duplicate refusal/native cleanup; quality PASS538/0/76. SQL bounded PK lookup retained; SAP/CASE remaining.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md");out[str(p)]=p.read_text(encoding="utf-8")+"\n11.10.2026:179 [весовая серийная коробка](../../../../database/retailcase_ni042_weight_box_capture_20261011.md) APPLIED. Inventory/MES birth and SKU UI use existing physical registry/native single writer; actual9.8KG/onebox/no duplicate. SAP capture/CASE scanner/scale equipment/last-box policy remain open.\n"
# Reuse the existing task root, regardless of its legacy spelling.
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:
 out[str(roots[0]/"NI04.2"/"179_weight_box_capture.md")]="""# Qwen: NI04.2 slice179
Execute scripts/ni042_weight_box_capture_case.py in RABAEV/orcl with own tagged SKU only. Confirm one box9.8KG/unit1/no government codes, exact replay, duplicate and mass mismatch refusal, native count cleanup, original135 P20H20. Check UI independent SKU flag and422 for nonweighted/nonKG; omitted field preserves flag. Decoder: HRI/raw GS, correct GTIN check digit, AI3100..3105, serial1..20; unsupported AI/duplicate/zero mass rejected. Never fabricate regulatory ACK. Marked weighted variant, SAP and CASE scanner are not accepted by this task. Report longest relevant SQL and decision. Do not use database copy or direct stock DML.
"""
for f in [folder,Path("db/migrations/2026-10-11_ni081_container_cell")]:
 out[str(f/"installed_sources.json")]=json.dumps({p.name:hashlib.sha256((out.get(str(p),p.read_text(encoding="utf-8"))).encode("utf-8")).hexdigest().upper()for p in f.glob("*.sql")},indent=2)+"\n"
for path,content in out.items():
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding="utf-8")
print("179 documents, manifest and source hashes saved")
