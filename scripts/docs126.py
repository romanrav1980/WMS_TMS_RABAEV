from pathlib import Path
import json
out={}
page="wiki/database/nicora_ni043_mes_manifest_20261010.md"
out[page]="""# NI04.3 — выпуск MES по составу отправителя,126
Вход — существующий FG_PALLET_RELEASE; команда MES_MOVEMENTS и единая StockPosting/RRL_STOCK_POSTING_API. Источник manifest.source_document_id равен конкретному движению, не всему заказу. Native production order/current warehouse/target cell/SKU/BASE/version/profile совпадают. Capture manifest_operation_id передаётся в существующем birth_captures[UID].
mes_commands saved replay использует platform.read_oracle_json: Oracle native dict/list и текст/CLOB поддерживаются. Раньше json.loads(native dict) ломал повтор уже проведённого движения. Типизированы изменённые функции; отдельный MES/остаточный регистр не создан.
Raw trace-manifests.html/js теперь позволяет выбрать пересчёт или выпуск MES: existing order+movement, actual pallet/aggregate scans, immutable durable path/body/user/API scoped retry. Применение через прежний /api/mes/production-orders/{id}/apply-wms; inventory branch сохранена. Состав остаётся настройкой WMS SKU/profile, no gov ACK.
Author scripts/ni043_mes_sender_case.py и existing_case.py: native BOM/order98/completion/FGmovement120/UID MES.MARKED.INTERNAL.PALLET:9643f7c26e; original MES126.MANIFEST:9643f7c26e + MES126.BIRTH:9643f7c26e. Exact graph/mode/profile/source→P3H0/physical3/codes6/use1/movementAPPLIED_TO_WMS. Existing HTTP repeat nativeJSON returns same result; foreign inventory manifest409 with no partial stock.
Первое создание фикстуры использовало mixed-case syntheticSKU, тогда как native BOM нормализует артикул uppercase; прямой вызов native completion также оставил default MES_FG вместо targetcell, которую задаёт существующий MesService. Это проблемы author setup: существующую completion повторно использовали с тем же key через service, подготовили own uppercase master/policy, конкретный release120 выбран поUID. Fresh case исправлен, продолжение PASS; второй выпуск не создавался.
Standalone synthetic FG release proves this stock/marking slice only. Raw consumption/production readiness/real hardware/regulatory ACK и независимая приёмка не доказаны. Полный NI04.3 остаётся частичным.
Slow SELECT10.301/8.745/7.794ms. Решение сохранить source order/movement PK и batch200/unit10000; inventory owner проверит планы при росте. Общий архитектурный debt gate125 FAIL438files/223debt/1cycle; новые trace/regulatory files без новых отмеченных нарушений, baseline не расширен.
"""
out["wiki/index.updated.tmp"]="- [Маркированный выпуск MES по составу отправителя](database/nicora_ni043_mes_manifest_20261010.md):126 native order98/FGmovement120/current source/capture/P3H0/physical3/use1/HTTP replay, existing commands preserved.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:126 existing MES birth now has operator source/capture UI and native OracleJSON replay reader. Actual order98/release120 existingcompletion/service target/private uppercase syntheticSKU/capture→P3H0/units3/use1/APPLIED_TO_WMS/HTTP replay and foreign source409. Authorsetup corrected without secondcompletion; rawconsumption/factory/equipment/legalACK not claimed. SQL10.301/8.745/7.794ms keepPK/batchbounds. Architecture438/223/1cycle debt persists, no baseline raise."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni04_3.md","Ticket126: [[database/nicora_ni043_mes_manifest_20261010]] native MES FG release120/root capture/P3H0/physical3/current source/HTTP replay and UI. Status remains partial; regulatory lifecycle/tree/real ACK/independent acceptance unresolved.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/execution/active/ni04_3.md");out[p.as_posix()]=out[p.as_posix()].replace("Статус: planned_delta","Статус: in_progress_bounded_sender_inventory_mes_dev")
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for item in m["increments"]:
 if item["id"]=="NI04.3":
  item["status"]="in_progress_bounded_sender_inventory_mes_dev";item["acceptanceStatus"]="author_dev_slices_124_126_not_full_sprint_acceptance";item["evidence"]=page;item["remainingScope"]=["complete regulatory nested layout and lifecycle","real government acknowledgments and adapters by SKU applicability","independent acceptance and physical scanning evidence"]
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["задания на проведения тестов/NI04.3/126_маркированный_MES.md"]="""# Qwen — NI04.3,126
Existing order98/release120/UIDMES.MARKED.INTERNAL.PALLET:9643f7c26e/operationMES126.BIRTH:9643f7c26e already committed3. Use existingcase/read exactreplay; no fresh duplicate stock. Read wiki/database/nicora_ni043_mes_manifest_20261010.md and existing MES commands/native kernel.
Validate movement source exact UID/SKU/WARE/target/BASE/policy/profile/version. Foreign inventory/MES document deny beforeP; changed OP/body conflict. All profiles cover same3units/codes6; no fakeSSCC/native canonicalregistry/use1/stockoutbox sameTX. Replay native Oracle dict/CLOB text supported. UI source selection/per-user/API durable exact-body/path, same OP retry after timeout; wrong-mode409 retained.
BOM/mes native normalizesSKUuppercase; service configures requested target cell after completion. Do not mistake author fixture setup for new runtime behavior. Synthetic standaloneFG does not prove raw consumption/factory/equipment/realgovACK. Current MES actor warehouse scope next hardening delta; ordinary foreign actor must not apply otherWARE.
"""
print(json.dumps(out,ensure_ascii=True))
