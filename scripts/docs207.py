from pathlib import Path
import json,re
out={};f=Path("db/migrations/2026-10-11_ni042_case_mass")
out[str(f/"009_ledger.sql")]="""merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-11-207-case-measured-mass-manifest'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS,NOTES)
values(s.MIGRATION_ID,'Measured CASE mass frozen in original HU load and store manifest',sysdate,user,
'db/migrations/2026-10-11_ni042_case_mass/apply.sql','db/migrations/2026-10-11_ni042_case_mass/rollback.sql','APPLIED',
'Own QPB2075AB68DD7/type17/6EA/SSCC090000000000000209/.400-.100=.300; existing HU outer1+.4=1.4; native rollback, fake CASE manual mass refused, load replay and departure without second stock, store frozen proof/tolerance. Original13520/20; TEST only.');
commit;
"""
out[str(f/"apply.sql")]=(f/"apply.sql").read_text(encoding="utf-8")+"@@009_ledger.sql\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for name,new in [("RRL_WH_FINAL_SCALE_ADMISSION","002_admission.sql"),("RRL_STOCK_HU_READ","003_read.sql"),("RRL_STOCK_LOAD_BOX_CORE","004_boxes.sql"),("RRL_STOCK_HU_LOAD_CORE","005_load.sql"),("RRL_STOCK_STORE_WEIGHT_CORE","006_store_weight.sql"),("RRL_STOCK_STORE_RECEIPT_READ","008_store.sql")]:
 matches=[x for x in m["components"] if re.search(r"create\s+or\s+replace\s+package(?:\s+body)?\s+"+name+r"\s",(p.parent/x).read_text(encoding="utf-8"),re.I)]
 assert matches,name
 m["components"]=[("../2026-10-11_ni042_case_mass/"+new)if x==matches[-1]else x for x in m["components"]if x not in matches[:-1]]
m["startup_scripts"].append("../2026-10-11_ni042_case_mass/001_schema.sql")
matches=[x for x in m["additional_scripts"]if re.search(r"create\s+or\s+replace\s+trigger\s+RRL_TT_LOAD_BOX_WEIGHT_GUARD\s",(p.parent/x).read_text(encoding="utf-8"),re.I)]
assert matches
m["additional_scripts"]=[x for x in m["additional_scripts"]if x not in matches]+["../2026-10-11_ni042_case_mass/007_guard.sql"]
m["required_columns"].setdefault("RRL_TT_LOAD_BOX_WEIGHT",[]).extend(["CASE_BOX_TASK_ID","FINAL_SCALE_CAPTURE","WAREHOUSE_QC_OPERATION","TARE_WEIGHT_KG","NET_WEIGHT_KG","DEVICE_MODE","COMPOSITION_SIGNATURE","SIGNATURE_VERSION","MEASURED_CONTENT_VERSION","COVERAGE_COMPLETE","PALLET_BOX_UID"])
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["wiki/database/nicora_ni042_case_mass_20261011.md"]="""# NI04.2: измеренная коробка в погрузке и приёмке магазина

207 APPLIED в RABAEV/orcl. [[nicora_ni042_case_mass_design_20261011]]; [[nicora_ni042_small_hu_20261011]].
Существующее чтение CASE возвращает подтверждённую фактическую массу и источник контроля. Существующий HU preview считает .400 один раз вместе с внешней тарой1.0, сохраняя6EA на физических листьях. Native HU load автоматически получает массу малого CASE из принятого QC, запрещает подменять её ручной записью. Остальные BOX сохраняют прежний контракт. Для WEIGHT_PHOTO требуется полный состав измеренных коробок; частичное покрытие в BARCODE явно отмечено и не допускается позднее как полное.

Существующая RRL_TT_LOAD_BOX_WEIGHT сохраняет CASE:id, FK настоящего CASE, SSCC сканирования, .400 gross/.100 tare/.300 net, архив весов, исходную операцию QC, TEST/HARDWARE, версию измеренного состава и подпись3. Условный виртуальный PALLET_BOX_UID сохраняет прежний FK для обычных BOX. Для CASE фиктивная строка PALLETS не создаётся. Append-only guard сравнивает сохранённую проводку с точным frozen native plan, текущий состав после списания не подставляет.

Own QPB2075AB68DD7/type17/SSCC090000000000000209: SAP20→CASE6/source14; реальные архивы весов и независимый QC; упаковка, фактическая масса1.4, отказ ручной подмены, native late rollback без frozen rows и с CASE P6H6, HU_SHIP/replay, оригинальное отправление без второго списания. Store preview получает SSCC, .400/.100/.300, TEST, capture/QC, signature3, полное покрытие; прежний допуск .400/2=.200. Исторический состав сохраняет1.4. Остаток источника14 очищен native count, исходная контрольная fixture135 P20H20 сохранена. Отправленные6 остаются в истории; возврат не выдумывался, реальная тара ожидает передачи. Первый тест не создал справочный RRL_ADDR и закономерно получил409; собственные остатки очищены, fixture исправлена.

Live USER_ERRORS/INVALID clear. Longest applicable frozen-box read1fnbms6kfznx0 8.616ms/1; final capture list50nt4sufyvyq8 7.423ms/1. Сохраняем PK load+box и ограничение200/51; owner inventory/delivery проверит планы при производственном объёме. Запрос самого диагностического v$sql не считается бизнес-запросом. Физические весы, магазинная приёмка WEIGHT_PHOTO и независимая приёмка полного спринта не объявлены выполненными.
"""
for path,line in [
("wiki/index.md","- [Масса коробки в рейсе и магазине](database/nicora_ni042_case_mass_20261011.md):207 actual6EA/.400+.outer1=1.4/native load rollback/replay/frozen CASE identity and original store tolerance."),
("wiki/log.md","2026-10-11:207 measured CASE mass integrated into existing HU read/load/store manifest, conditional real FK and frozen-plan guard. Own QPB2075AB68DD7 load/depart/replay/rollback/current archived proof passed; stock cleanup preserves13520/20. First missing address fixture refused409 and cleaned. Reads8.616ms retain bounds/keys; TEST facts explicit."),
("wiki/requirements/nikora_delivery_v55/execution/active/ni04_2.md","11.10.2026:207 actual small measured CASE6 mass.400/tare.100/net.300 preserved inside HU1.4 and original load/depart/store preview with SSCC, source archive/QC/mode/signature3; no fake pallet/no duplicate stock/tare. WEIGHT_PHOTO complete coverage enforced. Actual store confirmation/mixed marked small/route sequencing remain open.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");plan=json.loads(p.read_text(encoding="utf-8"));next(x for x in plan["increments"]if x["id"]=="NI04.2").setdefault("implementedSlices",[]).append("207 accepted small CASE actual mass/identity/QC archive frozen by existing HU load and exposed to store; complete weight-photo box coverage, no duplicate tare or stock")
out[str(p)]=json.dumps(plan,ensure_ascii=True,indent=2)+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"207_case_mass_manifest.md")]="""# Qwen:207
Run scripts/ni042_case_mass_manifest_case.py only dedicated dev. CASE6EA/.400 gross/.100 actual tare/.300 net, outer1.0 ->1.4. Check fake CASE manual mass refused, late native rollback leaves no BOX weight facts and P6H6, real load/replay/depart no second consumption, frozen CASE:id conditional FK without fake PALLETS, original store preview SSCC/source/mode/signature3/tolerance. Existing manual BOX compatibility retained; weight-photo incomplete composition refused even after policy change. TEST never legal hardware evidence. Retain real shipped/tare history, native cleanup source14 and protected13520/20. Independent physical store confirmation remains separate.
"""
print(json.dumps(out,ensure_ascii=True))
