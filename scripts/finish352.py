from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for f in["001_store.sql","002_ship.sql","003_recompile.sql"]:
 entry="../2026-10-12_ni061_mixed_consolidation/"+f
 if entry not in m["additional_scripts"]:m["additional_scripts"].append(entry)
out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
page="wiki/database/retailcase_ni061_mixed_consolidation_20261012.md"
out[page]="""# Смешанное маркированное и обычное верхнее место
345 APPLIED в RABAEV/orcl. Прежний HU_SHIP/двеdispatch строки/STORE_RECEIPT сохраняют разные правила товара. Для маркированного SKU применяется exact current savedprofile-version и матрица каждой единицы. Для обычного SKU issued_manifest доказывает ноль trackedunits и отсутствие обязательного профиля; ordinary_lots содержит только UID такого исходного STOCK листа. Количественные строки по этим UID проверяет прежний immutable receipt compiler. QR для обычного товара не создаются и не требуются.

STORE_MARK_CORE сверяет marked disposition отдельно по каждой lot_uid, а обычные строки допускает только по заранее доказанным ordinary_lots. Дубликат/чужая/пропущенная строка отклоняется. Полный union профилей/число QR относится только к маркированным единицам. Количество товара не выводится из числа сканов. Смена карточки на маркированную при отсутствии tracked units отклоняется native issued_manifest; serialized units без профилей блокируются.

Actual346–350: marked3EA/3units6codes +ordinary3EA/no codes, две реальные приёмки/старые задания/передача ответственности/СТ/QC →oneTOP →actualLOAD/DEPART/STOREbothordersaccepted3once/P0. LateLOAD rollback/exactrepeat/protected20/20. tmp/context348.json полностью доставлен, source346347/initial349 forbidden.

351 UI: типизированный StoreMarkMatrix отдельно показывает артикул, товарную паллету, число единиц и обязательные профили каждого товара; ordinary_lots показывает обычную количественную сверку. Select ключ включает version/mode, предотвращая совпадение React keys для одного профиля разных версий. Существующие durable drafts/operation retries/серверная финальная проверка сохранены. TypeScript admin PASS, architecture635/0cycles/76debt. Отдельный модуль не раздувает основной экран.

Не объявлены выполненными hardware/независимая приёмка/GovACK, multi-recovery и atomic grouped first-leg multiSKU receipt. SQL inventory owner: perleaf profileproof bounded byUID/card/200tree; warm plan and batching on large tree remain explicit backlog.
"""
p=Path("wiki/index.md");out[p.as_posix()]="- [Смешанная консолидация и интерфейс матриц](database/retailcase_ni061_mixed_consolidation_20261012.md):345–351 marked3/6codes+ordinary3 inoneTOP→STOREeach3; perSKU/profile UI/adminTS/archPASS.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 12.10.2026 345–351 mixedmarked/ordinary originalkernel actualsource346347→oneTOP→350STOREeachorder3/no duplicateFF/no ordinaryQR/P0/protected20/20. Guardedordinarylotset+permarkedunitmatrix. StoreMarkMatrix modularUI/versioned selectkeys/adminTypeScriptPASS/arch6350cycles76. Source348 actualcontextdelivered, factories/initial cases forbidden.\n"
p=Path("wiki/runbooks/retailcase_active_work.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\nCurrent351 native345VALID/serv333/currentAPIreadcode320. Context348 marked3+ordinary3 delivered350/P0/6oldcodes/no ordinarycodes. adminTS/arch635/0cycles76. StoreMarkMatrix newUI no browser/hardwareclaim. Next NI07.1 monthly common work included in same existing rate; no secondbilling engine.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/execution/active/ni06_1.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n345–351 mixed marked3/6codes+ordinary3 actualsameTOP/2ST/LOAD/DEPART/STOREbothorders3; ordinarylot evidence/nofakeQR/currentcardversions. PerSKU Matrix UI/adminTS. Multi-recovery/groupedfirstleg/partialnested/industrialindependent remain.\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"))
for x in m["increments"]:
 if x["id"]=="NI06.1":
  x["implementedSlices"].append("345–351 mixed marked3 and ordinary3 actual oneTOP/2ST/STOREbothorders3, current matrix and proved ordinarylot quantities; perSKU UI/adminTS")
  x["remainingScope"]=[v.replace("mixed ordinary/marked and recovery consolidation; atomic grouped multi-SKU first-leg nested receipt","recovery consolidation; atomic grouped multi-SKU first-leg nested receipt")for v in x["remainingScope"]]
out[p.as_posix()]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(root/"NI06.1/351_mixed_matrix_ui.md").as_posix()]="# Qwen345–351\nMixed marked3EA/6codes+ordinary3EA/nocodes, exact ordinarylots header and perSKU marked matrix. Under newmarkedcard with missingunits refusal; ordinaryscanqty doesn'tcreateQR. Correct perlot totals no groupdoublecount. UI cards display current profiles separately/markedunitcount only/versioned keys; durablependingpayload/actor/load/address/signature preserved. Actualcontext348 alreadySTORE both3, no factories/initial349. Hardware andindependent acceptance absent.\n"
print(json.dumps(out))
