from pathlib import Path
import json
out={}
reader="wiki/database/nicora_ni043_composition_reader_20261010.md"
forecast="wiki/database/nicora_ni081_forecast_20261010.md"
out[reader]="""# NI04.3 — состав и происхождение паллеты,132
GET /api/receiving/pallets/{uid}/composition uses one READ ONLY Oracle snapshot. Existing traceability_view global auditor semantics retained. Current P/H/location/version/physical epoch, actual physical units and multiple applicable profile codes are read together. Source_births derives original CREATED_BY_STOCK_OP/canonical source and exact MES FG movement, optional sender manifest/hash/use; genuine SAP receipts remain separate. Non-SAP inventory/MES birth does not fabricate a SAP receipt.
Quantity coverage compares current P with captured units. Exact decimal strings; bounded200 locations/receipts/source rows,10000 units,5000 code pairs per page, units100 default. Cursor continuation requires original composition_signature; missing/stale signature409. Signature covers current physical epoch and stock/location versions; pages cannot silently combine changed stock snapshots.
Author scripts/ni043_composition_read_case.py: UNIT.CAPTURE:d5e9aa9590, MES.MARKED.INTERNAL.PALLET:e9732e1188, TOBACCO.CONTEXT:fe13c21d8c each current3/physical3/profiles6/MATCHED, correct revision225/MES99, no SAP receipt, three pages/current signature/409. Existing supplier-return stock0 unchanged. Genuine SAP pallet300000034518661218 retains original receipt/source despite current0.
Raw pallet-composition.html/js supports barcode input, source/history/locations/current physical codes and bounded continuation. Late responses discarded when actor/API/pallet changes, controls reset only for current sequence. Trace-manifests navigation now permits authenticated shell users, so UNIT operators without import right can reach their existing count/MES flow; import actions remain server-authorized.
Slow SQL: source/UID exact keys and bounded pages retained; no whole-history scans or stock writes. Independent browser/scanner/legal provider acceptance remains open.
"""
out[forecast]="""# NI08.1 — прогноз по фактическому исполнению,133
Incremental migration2026-10-10-133-native-execution-forecast-projection APPLIED14/0; scalar JSON leaf-count fix005 applied3/0. All2 packages/5guards/tables VALID live RABAEV. Derived immutable source/leaf/CASE origin and daily counters, source warehouse/status/departure index; no warehouse stock table writes or extra root stock writer.
Authoritative RRL_FORECAST_SOURCE_RULES validates actual DEPARTED frozen tree (max200 STOCK leaves), current original CASE lot/warehouse and exact quantity via existing RRL_STOCK_MATH. Projector source PK -> binary ordered CASE origin -> warehouse/day mutex -> SKU counters. Same load/hash returns immutable result, duplicate source cannot multiply counters; same CASE original lot is counted once as CASE_DISPATCH, later CASE_RELOADED/TRANSIT_CASE are physical handling. All transactional without internal commit. Private transaction-scoped guard context; direct counter/leaf/history DML denied.
GET semantics exposed as POST /api/transport/warehouse-forecast/warehouses/{id}/view with typed request; projection POST /project max100 and /source exact native operation. Current warehouse-bound RUSERS enforced before replay/read; existing dispatch view/edit rights. Worker python -m app.workers.warehouse_forecast_worker --warehouse ID --actor ACTOR --limit50 --loop from API directory, separate short transaction per source, sleep interval >=1, no stock/external calls.
View reads one consistent Oracle snapshot, closed UTC-day calendar mean, history1..90/horizon1..31/series<=500. Optional current partial day explicitly scales exposure; default minimum active3. Missing sources or missing BASE policy/insufficient history blocks estimated quantity. Decimal arithmetic and upward BASE-scale rounding. source_data_signature identifies data, not approved operational capacity. Explicit work scopes CASE_DISPATCH, FULLPAL_DISPATCH, OUTBOUND_WORKLOAD; intermediary physical handling is not final customer sales.
Actual existing native CASE sources a6bcf2cbe3:1029+1030 →12+8=20, physical places2. Original source gap2 blocked; after projection no gaps, batch repeat0/signature stable, active minimum3 denies, default closedUTC-day NO_SERIES. WARE9104 existing interwarehouse3+return1 FULLPAL=4 kept distinct from CASE. Own actor foreign replay/read/project403, direct daily update20863; counts2/top2 unchanged. scripts/ni081_actual_forecast_case.py and ni081_forecast_scope_case.py are bounded author cases, no new goods created.
Initial projector had SQL VALUES invoking JSON.get_size; fixed local scalar before successful projection. Pool lease after package recompilation returned one unconfirmed503; same immutable source retry succeeded, no duplicate counts.
UI warehouse-forecast.html/js shows exact observed/estimated BASE quantity, active history/partial-day caveat/gaps, operator materialization and no stock/plan effect. Long SQL actual projector4.475ms, source replay.872ms, source-gap1.706ms, day key9.332ms; decision retain source composite index, bounded read90days/500series/100batch. Owner transport: projector batch can scan old missing history; keep bounded source count and add time-window/backfill cursor if volume grows. No broad load gate.
Resource norms, approved people/slot recommendations, slot draining, common manual/autoplan validation and real operational history remain next tickets. NI08.1 full sprint and independent acceptance not claimed.
"""
for name,text in [(reader,out[reader]),(forecast,out[forecast])]:
 out[name]=text
idx=Path("wiki/index.md").read_text(encoding="utf-8-sig")
out["wiki/index.updated.tmp"]="- [Прогноз по исполненным грузам](database/nicora_ni081_forecast_20261010.md):133 immutable native projection/CASE20/top2/warehouse scope/UTC mean/no stock; resources and plan validator next.\n- [Состав и происхождение паллеты](database/nicora_ni043_composition_reader_20261010.md):132 same-snapshot P/H/physical units/multiple profiles/original inventory-MES-SAP source/signature-bound pages.\n- [Проект прогноза](database/nicora_ni081_forecast_design_20261010.md):133 derived history only, native root unchanged.\n"+idx
for name,line in [
 ("wiki/log.md","2026-10-10:132 composition same-snapshot actual P/H/units/source/nativeJSON cursor signature delivered; existing three marked+ordinary+genuine SAP sources read, no writes.133 native forecast migrationAPPLIED/VALID, actualCASE12+8=20/top2/replay/foreign403/directguard/partialUTC mean blocked on gaps/history; separate FULLPAL4. Worker/raw UI added, current NI08.1 resources/slot/manual-auto validator next. SQL bounded source/day indices retained, no full sprint/independent acceptance claim."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni04_3.md","Tickets130..132: tobacco currentGTIN comparison, no implicit regulatory mock, original-source/current-composition reader delivered. See database/nicora_ni043_regulatory_runtime_20261010.md and nicora_ni043_composition_reader_20261010.md. Actual gov providers/ACK/tree acceptance remain open."),
 ("wiki/requirements/nikora_delivery_v55/execution/active/ni08_1.md","Ticket133 delivered bounded native departed-history projection and quantity advisory; see database/nicora_ni081_forecast_20261010.md. Existing CASE20/top2/FULLPAL4, no stock/new TT. Next resource norms/approved recommendations/common validator; full sprint remains in progress."),
 ("wiki/requirements/nikora_delivery_v55/implementation_plan.md","10.10.2026:124..132 sender graph/UNIT-MIXED/current source warehouse/internalID/regulatory simulation boundaries/composition provenance delivered;133 NI08.1 started with actual execution forecast. Current resource/slot recommendations and common plan validator remain; all residual sprint acceptance tracked individually, not inferred from author slices.")]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/nikora_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
m["currentSprint"]="NI08.1";m["currentSprintMeaning"]="actual_execution_forecast_resource_slot_and_shared_plan_validation"
for item in m["increments"]:
 if item["id"]=="NI04.3":
  item.setdefault("implementedSlices",[]).extend(["130 tobacco contextual GTIN source comparison","131 defaultdisabled regulatoryqueue explicitsimulation never legalACK","132 current composition same snapshot/original source/paged signature"])
  item["acceptanceStatus"]="author_dev_slices_124_132_real_regulatory_and_independent_open"
 if item["id"]=="NI08.1":
  item["status"]="in_progress_actual_execution_forecast";item["implementedSlices"]=["133 native immutable execution projection/calendar quantity forecast"]
  item["evidence"]=forecast;item["acceptanceStatus"]="author_dev_133_resources_slots_validator_and_independent_open"
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
p=Path("db/migrations/2026-10-08_stock_posting_core/current_runtime_manifest.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for pkg,file in [("RRL_FORECAST_SOURCE_RULES","002_source_rules.sql"),("RRL_FORECAST_PROJECTOR","003_projector.sql")]:
 if pkg not in m["packages"]:m["packages"].append(pkg)
 path="../2026-10-10_ni081_actual_forecast/"+file
 if path not in m["components"]:m["components"].append(path)
for file in ["001_schema.sql","004_guards.sql"]:
 path="../2026-10-10_ni081_actual_forecast/"+file
 if path not in m["additional_scripts"]:m["additional_scripts"].append(path)
out[str(p)]=json.dumps(m,indent=2)+"\n"
out["задания на проведения тестов/NI04.3/132_состав_и_происхождение.md"]="""# Qwen —132
Read wiki/database/nicora_ni043_composition_reader_20261010.md and receiving queries/provenance/domain contract/UI. Existing fixtures only: inventory/MES/tobacco current3 each2 profiles, genuine SAP source current0. Verify same read snapshot, exact Decimal strings, native JSON decode, no invented SAP receipt. Bound200 sources/locations,10000 units,5000codes/page. Cursor requires original physical/version signature, stale/missing409, actor/API/pallet late responses discarded. UNIT operators navigation without import grant; server import rights retained. No legal ACK or full sprint claim.
"""
out["задания на проведения тестов/NI08.1/133_исполненная_история.md"]="""# Qwen —133
Read wiki/database/nicora_ni081_forecast_20261010.md, SQL rules/projector/guards and typed forecast adapters/domain/UI/worker.
No fresh pallets needed. Existing CASE a6bc...1029+1030 actual20/top2 projected, warehouse9104 FULLPAL4. Same load/hash exact saved result/counters unchanged; two concurrent first source copies must single commit or rollback, no double daily/CASE origin. Direct DML denied/current actor foreign read/replay403. Never stock P/H or original demand changes. CASE origin dedup is not a new customer order; intermediate outbound work distinct.
Aware UTC closed days/default no history, partial day explicit/exposure, zero/insufficient active days/missing BASE policy/missing projection suppress quantity. Exact Decimal rounding BASE scale. No invented productivity/weekday seasonal sales or people assignment. Page500/history90/batch100; worker bounded short transactions/waits. Real forecast calibration/resources/manual-auto validator not delivered by133.
"""
print(json.dumps(out,ensure_ascii=True))
