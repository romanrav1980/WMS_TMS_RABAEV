from pathlib import Path
import json
out={};page="wiki/database/retailcase_ni081_slotting_demand_20261010.md"
out[page]="""# NI08.1 / NS59 — источники и сценарный объём,143

Inventory owns read-only SlottingDemand/same Oracle READ ONLY snapshot. Existing RRL_STOCK_POOL_READ remains source of open customer rows/unallocated/HARD/picked overlap. Unpicked warehouse need=unallocated+HARD−picked-hard-overlap, not SOFT plus orders plus picked again. Legacy requested shipment calendar dates define1..31day horizon; undated orders remain separately visible/PERIOD_ASSIGNMENT_REQUIRED, never silently assigned to a date.

POST /api/inventory/slotting/warehouses/{ware}/articles/{article}/scenario, pick_topology_view + current active actorWARE. Declared optional period-total forecast requires current BASE unit. Matching orders consume forecast: max(forecast,firm) represented as forecast+firm−min(forecast,firm); explicit lower bound firm if no forecast, never observed-zero-demand assertion. Qty calculations precision80 Decimal and whole nominal pallet rounding.

Old pick stock credit: eligible current free P−H plus in-period owned HARD, bounded by P; another period's HARD not credited. Uses canonical native eligibility with actual owner reservation. Incoming only unique current whole-pallet source/actual source qty/eligibility and original tasks, no duplicate task or source counted twice. Snapshot bounds2000 pool rows/500 current stock/200 incoming; original valid mappings and stock keys reused. Quantity estimate is not number/geometry of physical slots.

Read result explicitly SCENARIO_ONLY/apply_allowed=false/physical_layout_admission=false/automatic_sales_forecast=false/business_calendar_verified=false. Native133 outbound-workload history not asserted as shortage-corrected sales forecast. Missing availability history, unclassified open-order CASE routing, physical layout and range approval remain requirements. No new movement/config/task writer.

Author tests/retailcase/test_slotting_demand.py4 cases: forecast100+matching40→100, demand150/old50/pallet100→extra100, selected HARD/picked overlap once, no history is lower bound/no layout admission. Actual scripts/ni081_slotting_scenario_existing_case.py reused135 P20H20: original QA headers1920/1921 had no shipment date, unknown unpicked20 disclosed. Only these owned QA header dates temporarily set10Oct under CONFIG fence and restored finally; with dates firm20/HARD20 correctly counted once, old credit20, declared forecast100 consumes20→100 rather than120, wrong BOX instead EA409; P20H20 unchanged. These synthetic temporary header dates are not real ERP evidence.

Raw separate slotting-demand page shows horizon/declared optional forecast/BASE/known minimum/old stock/inbound/undated obligations and no apply button; scope changes suppress stale async result. Node syntax check PASS, independent rendered acceptance not claimed.

SQL pool snapshot42.342ms/5, selected-owner stock query29.456ms/2 (other cursor22.723ms/2). Decision retain current bounded same-snapshot/window queries. Native pool function per-row lookup work at2000 requires batched set-based aggregation before larger production usage; owner inventory, not a new allocator. No load benchmark.

NS59 dynamic candidate placement/route-compatibility/travel-pick-replenishment cost comparison and approved range/drain still next. Legacy warehouse calendar issue remains pending owner declaration. Full NI08.1 not closed.
"""
out["wiki/index.updated.tmp"]="- [Источники потребности для диапазона](database/retailcase_ni081_slotting_demand_20261010.md):143 original pool/secured overlap/period/old stock/incoming/forecast consumption/read-only scenario/no zero demand claim.\n"+Path("wiki/index.md").read_text(encoding="utf-8-sig")
for name,line in [
 ("wiki/log.md","2026-10-10:143 inventory read-only same snapshot original pool/customer period/undated disclosed, unallocated+hard-picked overlap once, old creditfree+in-period hard/unique whole source inbound, declared period forecast consumption/exact80precision/nominal pallet rounding. 4 meaningful domain examples PASS; actual original135 unknown20, own QA dates temporarily assigned/restored undercfg, firm20/currentold20/forecast100 consumes20=>100/BOX409/P20H20 unchanged. Dedicated read-only raw page/node syntax PASS. Pool42.342/owner29.456ms bounded2000/500/200 kept; future native per-row pool aggregate batching ownerinventory. Scenario not sales-exposure/physical-layout/range approval/calendar admission; full sprint open."),
 ("wiki/requirements/retailcase_delivery_v55/execution/active/ni08_1.md","Ticket143 read-only actual pool/period/HARD-pick overlap/old stock/incoming/declared forecast consumption, undated demand separate; no placement admission. See database/retailcase_ni081_slotting_demand_20261010.md. Physical NS59 ranges/approval/drain/cost comparison and calendar remain.")
]:
 p=Path(name);out[name]=p.read_text(encoding="utf-8-sig")+"\n"+line+"\n"
p=Path("wiki/requirements/retailcase_delivery_v55/implementation_plan.json");m=json.loads(p.read_text(encoding="utf-8-sig"))
for row in m["sprints"]:
 if row.get("id")=="NI08.1":
  row.setdefault("implementedSlices",[]).append("143 period-scoped original order pool/unpicked hard overlap/old stock credit/unique incoming/forecast consumption scenario")
  row["evidence"]=page;row["acceptanceStatus"]="author_dev_133_143_physical_ranges_calendar_joint_timing_independent_open"
out[str(p)]=json.dumps(m,ensure_ascii=False,indent=2)+"\n"
out["задания на проведения тестов/NI08.1/143_источники_потребности_диапазона.md"]="""# Qwen —143

Read design/evidence/source reader/native pool, domain/stock credit. Read-only endpoint, no new stock fixture. Own QA headers1920/1921 have original NULL dates restored; P20H20/wave395 existing.

Known period demand reconstructs unallocated+hard−picked-hard-overlap, does not sum SOFT a second time or count picked as future warehouse work. Undated demand separately visible/period assignment required. Matching total-period forecast consumes matching firm qty; exact100+40→100,150/old50/pallet100→additional100. No forecast is minimum, unavailable/zero dispatch not certified zero demand.

Old eligible credit excludes another period'sHARD, includes in-period source hard only once; scalar owner eligibility may use minimum own reservation but summed owned quantities must not exceed actualH/P. Incoming unique whole-pallet source/actual qty, excludes partial/duplicate/missing/blocked. Current native family/type differences must be examined before placement integration. One consistent READ ONLY snapshot, warehouse scope/unit mismatch/bounds.

Business calendar/actual sales availability history/unclassifiedCASE routing/geometry/source norm confirmation/approval missing. No apply button/certificate; raw UI stale scope hidden/Decimal input not Number. No complete NS59 acceptance or production dates inferred from temporary synthetic own-header case.
"""
print(json.dumps(out,ensure_ascii=True))
