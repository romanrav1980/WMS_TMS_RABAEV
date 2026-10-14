from pathlib import Path
import json
out={}
out["wiki/database/retailcase_ni053_small_weight_receipt_20261011.md"]="""# NI05.3: магазин принимает измеренный малый CASE

208: повторно использованы существующие приёмка магазина, архив оригинальных фото, шлюз весов и native STORE_RECEIPT. Новая функция UI StoreBoxMassPanel показывает сохранённый идентификатор, брутто, тару, нетто, источник и явный TEST. Показания не редактируются. Отдельной приёмки или движения запаса не создано.

Own load SMALL207.LOAD:5ab68dd7 / QPB2075AB68DD7 / CASE6EA / архивная коробка.400 / внешняя тара1.0 / груз1.4. Настоящий API и Oracle с отдельными отправителем весов и получателем магазина: синтетический стабильный пакет1.199999999 получил409 STORE_WEIGHT_ACT_REQUIRED, документ не появился;1.2 принят по включительной границе допуска±.2. Три разные оригинальные фотографии FRONT/LEFT/RIGHT, принято6, exact replay, один outbox, ноль quantity journal, повторного списания и government ACK нет. Receipt STORE208.RECEIPT:212751cc. Созданные пользователи после кейса отключены; protected13520/20 сохранено. Программный контракт подтверждён; реальные весы/камеры/магазинный пилот и независимая приёмка отдельно.

207 full quality PASS:24 tests, обе TypeScript-проверки, architecture554/0cycles/76debt. После208 проверен TypeScript admin. Slow SQL: frozen-box read8.616ms/1, bounded51 scales list7.423ms/1; retain PK/bounds, owner delivery при производственном объёме профилирует native receipt. Отдельная маркированная приёмка не заменяется этим ordinary сценарием.
"""
for path,line in [
("wiki/index.md","- [Приёмка малого измеренного CASE магазином](database/retailcase_ni053_small_weight_receipt_20261011.md):208 existing weight/photo flow accepts6 at1.2/source1.4/tolerance.2 with three views/nonadmin/replay; UI frozen box mass."),
("wiki/log.md","2026-10-11:208 existing STORE_RECEIPT accepts measured small CASE6 from207 under WEIGHT_PHOTO; nonadmin receiver/synthetic gateway/3 original views/epsilon refusal/inclusive1.2/replay/outbox1/no second stock. UI displays frozen box gross/tare/net/source/TEST. Independent equipment/pilot not claimed."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni05_3.md","11.10.2026:208 ordinary measured small CASE end-to-end from207 load to existing weight-photo store receipt. Actual synthetic1.2/source1.4/.2 inclusive, epsilon refusal, three original views, nonadmin6EA/replay/no second stock. UI shows archive box mass/source/TEST; marked recipient and physical pilot remain."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:208 measuredsmall own control→HU→original departure→existing store WEIGHT_PHOTO accepted6EA with exact .2 tolerance/three views; [[retailcase_ni053_small_weight_receipt_20261011]]. Marked small/route sequencing/physical equipment remain.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"))
next(x for x in j["increments"]if x["id"]=="NI05.3").setdefault("implementedSlices",[]).append("208 original weight/photo receipt of measured smallCASE6/source1.4/tolerance.2/nonadmin/photos3/exact replay and frozen box mass UI")
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI05.3"/"208_small_case_store_weight.md")]="""# Qwen:208
Create fresh source with scripts/ni042_case_mass_manifest_case.py, pass printed SMALL207.LOAD:<tag> into scripts/ni053_small_case_weight_receipt_case.py. Default historical source already received; do not demand another receipt. Check original frozen .400 box/.100 tare/.300 net/TEST, outer1.0=1.4, half-lightest .2 tolerance, separate gateway and receiver, three original views, epsilon below1.2 refused/no document,1.2 accepted6/replay/outbox1/events0/no second warehouse quantity. UI shows frozen masses and TEST. Browser picture fixtures and synthetic packets do not prove physical hardware; marked recipient flow separate.
"""
print(json.dumps(out,ensure_ascii=True))
