# NI08.1 / NS59 — источники и сценарный объём,143

Inventory owns read-only SlottingDemand/same Oracle READ ONLY snapshot. Existing RRL_STOCK_POOL_READ remains source of open customer rows/unallocated/HARD/picked overlap. Unpicked warehouse need=unallocated+HARD−picked-hard-overlap, not SOFT plus orders plus picked again. Legacy requested shipment calendar dates define1..31day horizon; undated orders remain separately visible/PERIOD_ASSIGNMENT_REQUIRED, never silently assigned to a date.

POST /api/inventory/slotting/warehouses/{ware}/articles/{article}/scenario, pick_topology_view + current active actorWARE. Declared optional period-total forecast requires current BASE unit. Matching orders consume forecast: max(forecast,firm) represented as forecast+firm−min(forecast,firm); explicit lower bound firm if no forecast, never observed-zero-demand assertion. Qty calculations precision80 Decimal and whole nominal pallet rounding.

Old pick stock credit: eligible current free P−H plus in-period owned HARD, bounded by P; another period's HARD not credited. Uses canonical native eligibility with actual owner reservation. Incoming only unique current whole-pallet source/actual source qty/eligibility and original tasks, no duplicate task or source counted twice. Snapshot bounds2000 pool rows/500 current stock/200 incoming; original valid mappings and stock keys reused. Quantity estimate is not number/geometry of physical slots.

Read result explicitly SCENARIO_ONLY/apply_allowed=false/physical_layout_admission=false/automatic_sales_forecast=false/business_calendar_verified=false. Native133 outbound-workload history not asserted as shortage-corrected sales forecast. Missing availability history, unclassified open-order CASE routing, physical layout and range approval remain requirements. No new movement/config/task writer.

Author tests/retailcase/test_slotting_demand.py4 cases: forecast100+matching40→100, demand150/old50/pallet100→extra100, selected HARD/picked overlap once, no history is lower bound/no layout admission. Actual scripts/ni081_slotting_scenario_existing_case.py reused135 P20H20: original QA headers1920/1921 had no shipment date, unknown unpicked20 disclosed. Only these owned QA header dates temporarily set10Oct under CONFIG fence and restored finally; with dates firm20/HARD20 correctly counted once, old credit20, declared forecast100 consumes20→100 rather than120, wrong BOX instead EA409; P20H20 unchanged. These synthetic temporary header dates are not real ERP evidence.

Raw separate slotting-demand page shows horizon/declared optional forecast/BASE/known minimum/old stock/inbound/undated obligations and no apply button; scope changes suppress stale async result. Node syntax check PASS, independent rendered acceptance not claimed.

SQL pool snapshot42.342ms/5, selected-owner stock query29.456ms/2 (other cursor22.723ms/2). Decision retain current bounded same-snapshot/window queries. Native pool function per-row lookup work at2000 requires batched set-based aggregation before larger production usage; owner inventory, not a new allocator. No load benchmark.

NS59 dynamic candidate placement/route-compatibility/travel-pick-replenishment cost comparison and approved range/drain still next. Legacy warehouse calendar issue remains pending owner declaration. Full NI08.1 not closed.
