from pathlib import Path
import json
out={}
out["wiki/database/retailcase_ni042_marked_small_20261011.md"]="""# NI04.2/NI04.3: маркированная малая коробка в паллете
211 повторно использует доставленные203–207 и существующие registry/CASE/QR/QC/HU/load, нового количественного механизма нет.
Actual QPB2118258E0AB/type21/SSCC090000000000001022: SAP own contract12EA/12 physical/24 synthetic codes CRPT TOBACCO and EGAIS ALCOHOL; CASE7/14 codes, source5/10 codes. WARE NONE не отменяет обязательный контроль уникальных кодов и собственный final-weight коробки. Пропуск одного применимого профильного кода даёт штатный сохранённый QC verified0/failure_reason QUALITY_UNIQUE_UNIT_PROFILE_COVERAGE_REQUIRED/readyfalse; это бизнес-результат200, а не разрешение отгрузки. Полный scan от отдельного контролёра, реальные API-архивы TEST .450 gross/.100 tare/.350 net, once-use/late rollback/concurrent distinct operations/replay/currentWARE прошли.
Контроль коробки сохраняется при упаковке; original HU load получает1.45 вместе с внешней тарой1.0, frozen mass/SSCC/QC/capture и точный состав. Late load rollback P7H7/no frozenbox; load replay/departure без повторного движения, source5/10 до cleanup. Store preview требует marked recipient flow; ordinary receipt не открывается. Native cleanup остатка5/original13520/20. Shipped7/14 codes and pending tare remain actual history. Own provider-shaped codes не подтверждают государственную подпись/ACK или легальную агрегацию нового SSCC.

Три ранних author попытки исправлены по фактическим контрактам: ST quantity6 вместо7; ожиданиеHTTP409 вместо сохранённого QC verified0; rollback обязан восстановить предыдущее scan-control состояние, а не всегда WAIT_CONTROL. Собственные P/H очищены после каждой. Исправленный scripts/ni042_marked_small_mass_case.py сохраняет штатную семантику, правила приложения не ослаблены.
Slow: original box/scale bounded reads8.616/7.423ms; stage queries .868/1.536ms. Оставлены CASE/PK/index200/51 bounds; inventory owner profile full marked composition at production size.211 не отдельная миграция.210 quality PASS24/bothTS/555files0cycles76debt; real equipment/store marked receipt/independent acceptance remain.
"""
for path,line in [
("wiki/index.md","- [Маркированная малая коробка в паллете](database/retailcase_ni042_marked_small_20261011.md):211 actual7 goods/14 codes vs source5/10, own QR+weight retained/native HU load/departure; no fabricated legal aggregation."),
("wiki/log.md","2026-10-11:211 composed existing marked small CASE/SSCC/actualscale/independent QR/fullHU load passed QPB2118258E0AB7/14 and source5/10. Incomplete QC returns saved verified0/readyfalse, actual rollback restores prior scan state. Author ST6→7 and expectations corrected, every failed fixture native-cleaned. Original13520/20; marked store remains distinct."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_2.md","11.10.2026:211 actual marked small CASE7/14 codes(two profiles), source5/10, independent QR scan+TEST .450-.100=.350 preserved inside upperHU1.45/load/depart/replay/late rollback; incomplete QR cannot approve; source cleanup native. No inferred legal aggregation; physical equipment/independent acceptance remain."),
("wiki/requirements/retailcase_delivery_v55/execution/active/ni04_3.md","11.10.2026:211 exact marked small-box CASE/HU/outgoing control/load lineage with CRPT+EGAIS per physical unit passed7 goods/14 codes, source5/10. Both profile codes required; own SSCC label is logistical and never gov aggregationACK. Existing marked-recipient flow remains required.")]:
 p=Path(path);out[path]=p.read_text(encoding="utf-8")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");j=json.loads(p.read_text(encoding="utf-8"))
next(x for x in j["increments"]if x["id"]=="NI04.2").setdefault("implementedSlices",[]).append("211 exact marked small CASE7/two-profile codes14/own full QR+actual weight retained in upper HU load/departure; source5/codes10, no duplicate quantity or fabricated legal aggregation")
out[str(p)]=json.dumps(j,ensure_ascii=True,indent=2)+"\n"
roots=[p.parent.parent for p in Path(".").glob("*/NI08.1/178_container_cell_index.md")]
if roots:out[str(roots[0]/"NI04.2"/"211_marked_small_box.md")]="""# Qwen:211
Run scripts/ni042_marked_small_mass_case.py dev only. SAP12 physical units/24 synthetic codes; marked smallCASE7/14two-profile codes/source5/10. Check independent exact QR control, omitted profile returns existing persisted verified0/readyfalse (HTTP200), never approval. Final .450-.100=.350 with TEST archive/onceuse/rollback/concurrent/replay/currentWARE; accepted QR state is prior rollback state. UpperHU1.45/native load rollback P7H7/load+depart no second consumption; frozen SSCC/proof and marked-store requirement. Distinguish logistical SSCC from legal aggregation ACK. Shipped history retained; source5 nativeclean/original13520/20.
"""
print(json.dumps(out,ensure_ascii=True))
