from pathlib import Path
import json
out={}
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8"))
for f in ["../2026-10-12_ni061_aggregation_quantity/001_aggregation.sql","../2026-10-12_ni061_nested_replan/001_put.sql"]:
 if f not in m["additional_scripts"]:m["additional_scripts"].append(f)
out[p.as_posix()]=json.dumps(m,indent=2)+"\n"
for dirname,guard in [("2026-10-12_ni061_nested_placement","select count(*)into n from RRL_INTERWARE_PUT_PLAN p join RRL_WAREHOUSE_TASK t on t.TASK_ID=p.TASK_ID where t.SOURCE_DOC_TYPE='WAREHOUSE_HU'"),("2026-10-12_ni061_nested_replan","select count(*)into n from RRL_STOCK_OPERATION where STATE='APPLIED'and COMMAND_TYPE='INTERWARE_PUTAWAY_PLAN'and json_exists(RESOLVED_PLAN_JSON,'$.domain.physical_place_uid')and json_exists(RESOLVED_PLAN_JSON,'$.domain.superseded_task_id')")]:
 p=Path("db/migrations")/dirname/"rollback.sql";out[p.as_posix()]="declare n number;begin "+guard+";if n>0 then raise_application_error(-20899,'RETAINED_HU_TASK_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;\n/\n"+p.read_text(encoding="utf-8")
page="wiki/database/nicora_ni061_nested_replan_20261012.md"
out[page]="""# Перепланирование целого принятого HU
323 APPLIED в RABAEV/orcl. Прежний INTERWARE_PUTAWAY_PLAN отменяет старое PLANNED/неначатое/неназначенное задание и создаёт новое в одной Root транзакции. Для WAREHOUSE_HU проверяются точный верхний UID, current HU version, исходная ячейка, QTY1/UNIT HU и receipt lineage; старый INTERWARE commodity layout сохранён. Ресурсы старого/нового task, receipt, plan, stockleaf и всех HU/link объявляются до упорядоченного захвата. После блокировок исходное описание проверяется вновь. Старое задание/plan не удаляются. Начатое, исполненное или закреплённое за ресурсом задание не заменяется этим механизмом.

Actual source322: исходная SAP агрегация не содержит Quantity участников. Миграция321 использует точное уже сохранённое BASE_QTY исходной физической единицы при отсутствии этого поля; explicit Quantity должен совпасть. Applied birth/order-line/profile/raw code/unitID proof сохранён. Это не повторное вычисление или новая проводка. Источники исходного и текущего UID не подменяются.

Source322 прошёл прежние SAP receipt, pick/ST, вложенную погрузку/выезд и межскладскую whole receipt3. case323 создал старое 1HU задание, проверил поздний rollback отмены/нового plan, затем actual atomic cancel-replan и exact repeat. P3/H0 в receiving quarantine, две активные ссылки, товар не перемещён. tmp/context323.json содержит актуальное новое task_id. Фабрику322 и исходный case322 повторно не запускать.

Следом требуется исполнить именно новое задание, затем прежние custody/onward/delivery. Независимая Qwen/оборудование/реальные ERP-government ACK остаются отдельными открытыми работами. Rollback не ослабляет guards при retained HU task history; forward recovery.
"""
for name in ["ni06_1.md","ni04_1.md"]:
 p=Path("wiki/requirements/nikora_delivery_v55/execution/active")/name
 out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n317–323: actual source316 sameTOP/BOX/stock3 received/wholeHU task1 with commodityfact3/custodytop/secondleg/STOREaccepted3. Source315 finalSTORE3 also complete. Existing atomic unstarted wholeHU cancel-replan323 actualrollback/replay/noPchange; Source322 currentP3receiving/newPLANNEDtask. SAP source member quantity omission321 reads already-born exactquantity. MultiST/multiSKU/partialnested/thirdwarehouse/independenthardware/external remain open. See nested_completion and nested_replan wiki.\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8"))
for x in m["increments"]:
 if x["id"]=="NI06.1":
  x["status"]="in_progress_bounded_nested_aggregate_partial_recovery"
  x["implementedSlices"].append("314–323 actual same nested SAP TOP/BOX/STOCK received, wholeHU task1/commodity3, custodytop, originalsecondleg STORE3, operator physical/stock projections; atomic unstarted HU cancel-replan and omitted SAP member quantity")
  x["remainingScope"]=[v for v in x["remainingScope"]if v!="warehouse nested first-leg receipt and physical tree reconstruction"]
 if x["id"]=="NI04.1":x["implementedSlices"].append("314–323 same physical nested one-STOCK tree across warehouse receipt/wholeHU placement/custody/secondleg/finalSTORE; existing atomic unstarted oneHU replan")
out[p.as_posix()]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
p=Path("wiki/index.md");out[p.as_posix()]="- [Перепланирование принятого целого HU](database/nicora_ni061_nested_replan_20261012.md):321–323 SAP omitted quantities retain born unit amounts; atomic cancel-replan 1HU without movement.\n"+p.read_text(encoding="utf-8")
p=Path("wiki/log.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\n- 12.10.2026 321–323 liveVALID: source322 SAP omissions → actualnestedreceive3/6oldcodes; original atomicHU cancel-replan actuallate rollback/replay/P3 links2, no movement. Source315 STORE3 finished. Maintained plan NI06.1 removes completed nested first-leg gap, keeps consolidation/partial/multihop/independent scope. Architecture634/0cycles/76debt, UTF8PASS. SlowSQL323 incoming cold386ms607buffers → bounded201/current-trip source; ownerinventory warm plan review, no production claim. Active-task lookup0.604ms14calls retains receipt/task keys; link update4.576ms2 retains exactPK.\n"
p=Path("wiki/runbooks/nicora_active_work.md");out[p.as_posix()]=p.read_text(encoding="utf-8")+"\nCurrent323: native321/323 override VALID, serv321/API320 reads; source315 STOREaccepted3 complete. Source322 nowP3 quarantine/sameTOPBOX/old6codes, context323 oldtaskCANCELLED/newtaskPLANNED; next execute currentreplan task then existingcustody/onwarddelivery. Do not rerun factories/initialnativecases. Arch6340cycles76/encodingPASS.\n"
root=next(Path(".").glob("*/NI08.1/178_container_cell_index.md")).parent.parent
out[(root/"NI06.1/323_nested_replan.md").as_posix()]="# Qwen321–323\nSAP Quantity optional: use exact persisted original physicalunit BASE_QTY, explicit mismatch denied, oldbirth/code/profileversion/orderline proof mandatory. Current Source322 P3 receiving with newPLANNED1HUtask context323: nofactories. Atomic cancel-replan latefailure rollsback both statuses/journals/outbox; two contenders onlyone oldtask replacement; wrongHUversion/source/started/assigned/resource/session denied. Execute newtask only, oldCANCELLED forbidden, fact1HU moves3EAwhole tree once. No realhardware/GovACK assumed.\n"
print(json.dumps(out))
