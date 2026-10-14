from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for dirname,names in [("2026-10-12_ni061_marked_consolidation",["001_units.sql","002_store.sql","003_ship.sql","004_recompile.sql"]),("2026-10-12_ni061_per_sku_mark_matrix",["001_store.sql","002_ship.sql","003_recompile.sql"])]:
 for f in names:
  entry="../"+dirname+"/"+f
  if entry not in m["additional_scripts"]:m["additional_scripts"].append(entry)
out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
page="wiki/database/retailcase_ni061_marked_consolidation_20261012.md"
out[page]="""# Маркированные товары в одном межскладском верхнем месте
333 и339 APPLIED/liveVALID. Тот же журнал327 OP+ST/отдельные исходящие события, прежние SHIPPING_CORE/QC/Root/HU_LOAD и STORE_RECEIPT. Несколько маркированных STOCK листьев в CONTAINER-only дереве сохраняют отдельный физический unit fingerprint каждого листа; исходный архив целиком сверяется с APPLIED HU_SHIP. Сумма unit количества равна количеству своего листа, общий physical_unit_count равен сумме всех листьев. Повторная birth отсутствует.

333 actual334–338: два SKU с одинаковыми двумя профилями, шесть единиц/12 исходных кодов, отдельные receipt/task/custody/ST/QC →oneTOP→LOAD/DEPART/STORE. Оба исходных заказа accepted3/FF3once/P0. Native late LOAD rollback/replay сохранил оба запаса и все lineage.

339 расширяет матрицу на карточку каждого SKU. Каждая единица несёт свой набор текущих system/profile/version/mode; expected tuples строятся именно для неё. Верхний profiles — ограниченный union для UI, а expected_scan_count — сумма собственных профилей всех единиц. На каждой товарной паллете проверяется соответствие сохранённых code PROFILES_JSON текущим версиям карточки; новая версия карточки не разрешает принять старые непроверенные коды. Quantity disposition сверяется отдельно по lot_uid каждой исходной строки, лишняя/дублированная/пропущенная строка отказана. Пределы10000units/20000scans/50unionprofiles/200tree nodes сохраняются.

Actual340–344: первый SKU два профиля(3units/6codes), второй толькоCRPT(3units/3codes). OneTOP/sixEA, expected9сканов. Source341 не имеет EGAIS профиля или его кодов. LateSTORE rollback удалил оба факта и все6 unit dispositions; неполный профиль и текущая карточка с неподходящей savedcode version отказаны. Actual344 STORE обоих исходных заказовaccepted3, protected20/20. tmp/context342.json полностью доставлен; source340341 factories и initial343/344admission не повторять.

Пока смешанное маркированное/обычное место и multi-recovery блокируются явно. Первая межскладская приёмка многотоварного HU требует отдельного атомарного группового контракта; scalar receipt не объявляется групповым. Внешних государственных ACK нет, hardware/Qwen independent не выполнены.

SQL решение: exact per-leaf source unit/profiles queries ограничены UID, system/profile и immutable birth; текущие JSON profile joins требуют warm измерения, owner inventory. Для большого дерева batch projection per-leaf profileproof — backlog, без заявления миллионных операций на dev.
"""
p=Path("wiki/index.md");out[p.as_posix()]="- [Маркированная консолидация по карточкам SKU](database/retailcase_ni061_marked_consolidation_20261012.md):333–344 twoST/oneTOP/6units, matrices2+1/9codes, perlotSTORE3each/staleversions denied.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 12.10.2026 333/339 nativeVALID actual338 homogeneous12codes and344 heterogeneous9codes/6units/twoSKU/oneTOP→STOREboth3. Per-leaf original fingerprints/full frozenarchive/current savedcodeversions/per-unit profiles/perlot disposition. LateLOAD+STORE rollback/exactrepeat/stalecard/incompleteprofile refusal; no rebirth/FFrepeat/GovACK. Mixedordinary/marked andmulti-recovery remain guarded.\n"
p=Path("wiki/runbooks/retailcase_active_work.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\nCurrent344 native333/339VALID, serv333. Context336 deliveredmarked6EA/12codes; context342 delivered6EA/9codes/perSKUmatrices2+1/2ordersaccepted3each/P0. Factories334335340341/initial337343344admission forbidden. Source341 print old6codes labelstale actual3codes; context exactsource authoritative. Nextmixedordinary/marked, multi-recovery, groupedfirstlegSKU contract.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_1.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n333–344: markedmulti onward/STOCK2 actualoneTOP→STOREbothorders3; sixunits/12codes homogeneous and6units/9codes differentSKUprofiles2+1. Current savedcodeversions/perunitmatrix/perlotquantities/rollback/replay proven. Mixedordinary/marked/multi-recovery/groupedfirstlegmultiSKU/independent remain.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"))
for x in m["increments"]:
 if x["id"]=="NI06.1":
  x["implementedSlices"].append("333–344 actual markedmultiST STOCK2/oneTOP; homogeneous12 and perSKUprofile matrices2+1/9oldcodes/6units; individual orders STOREaccepted3each/current savedversions/late rollback/replay")
  x["remainingScope"]=[v.replace("marked multiple ST/stock-leaf matrix; multi-SKU first-leg nested receipt; recovery consolidation","mixed ordinary/marked and recovery consolidation; atomic grouped multi-SKU first-leg nested receipt")for v in x["remainingScope"]]
out[p.as_posix()]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(root/"NI06.1/344_per_sku_matrix.md").as_posix()]="# Qwen333/339–344\nPerSKU profiles2+1, sixunits/ninecodes, each unit expects only own profiles. Explicit rawCode profileVersion must match currentcard; stale/currentwrongprofile/missingduplicateforeign codes denied. Perlot accepted/missing/refused/damaged quantities exact; line duplication/omission denied. Late STORE rollback bothfacts/6unitdispositions/outbox/custody; two Root contenders one winner; oldbirth/FF3once. Context342 alreadySTOREtwoorders3: nofactories/initial343344admission. Mixedordinary/recovery/groupedfirstleg unsupported.\n"
print(json.dumps(out))
