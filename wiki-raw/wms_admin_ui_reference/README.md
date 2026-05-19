# WMS Admin UI Reference

Raw visual reference for the future WMS admin panel.

Source context:

- accepted by user on 2026-05-17 from the chat screenshot
- visual direction: `WMS PRO` style, dense operational admin dashboard
- target implementation stack: React + Ant Design, aligned with `C:\WEB\demand_forecast\demand_forecast_frontend`

Files:

- [`index.html`](index.html): static raw prototype of the accepted dashboard style
- [`styles.css`](styles.css): visual tokens and layout rules
- [`admin-nav.js`](admin-nav.js): single modular navigation definition and renderer for all raw admin pages
- [`assets/nav-icons.svg`](assets/nav-icons.svg): RAW SVG navigation icon sprite for the 17 WMS admin sections
- [`api-audit.js`](api-audit.js): lightweight API journal/replay block for the raw prototype
- [`external-outbox.html`](external-outbox.html): separate external outbox and adapter journal administration page
- [`external-outbox.js`](external-outbox.js): lightweight external outbox list/detail/retry logic
- [`bom.html`](bom.html): separate BOM recipe administration page
- [`bom.js`](bom.js): lightweight BOM list/detail/lifecycle/calculation logic
- [`customers.html`](customers.html): customer registry, customer card, addresses, legacy mapping, and customer picking rules
- [`customers.js`](customers.js): lightweight customer list/detail/edit/rules logic
- [`customer-orders.html`](customer-orders.html): customer order registry, legacy import, order rows, and fulfillment facts
- [`customer-orders.js`](customer-orders.js): lightweight customer-order list/detail/import logic
- [`product-shipment-settings.html`](product-shipment-settings.html): article-level aging norms for finished-goods shipment readiness
- [`product-shipment-settings.js`](product-shipment-settings.js): lightweight settings list/detail/save logic
- [`raw-material.html`](raw-material.html): raw-material SKU settings, raw warehouses, and stock by selected warehouse
- [`raw-material.js`](raw-material.js): lightweight raw-material list/settings/stock logic
- [`raw-supply.html`](raw-supply.html): MES raw supply control page for demand, shortages, hard reservations, and transfer tasks
- [`raw-supply.js`](raw-supply.js): lightweight operator logic for calculating, releasing, confirming, and cancelling raw-material transfer tasks
- [`shift-supervisor-wave.html`](shift-supervisor-wave.html): shift-supervisor wave control panel for visual proof of process stages, free stock changes, physical stock changes, TSD actions, readiness, and screenshot checkpoints
- [`shift-supervisor-wave.js`](shift-supervisor-wave.js): static stage model `T0..T6` for the client end-to-end acceptance scenario
- [`wave-replenishment.html`](wave-replenishment.html): wave pick-face replenishment monitor, queue filters, source reservations, driver-task status, Minimax release action, staging release, and pick-face replenishment settings
- [`wave-replenishment.js`](wave-replenishment.js): lightweight wave replenishment UI logic for queued/waiting/driver replenishment rows, Minimax/queue check, staging release, and SKU pick-face rules
- [`resource-management.html`](resource-management.html): separate resource-management page for reachtrucks, KIKA, forklifts, trolleys, pickers, loading teams, cooking, packing, active sessions, and plan-fact Gantt
- [`resource-management.js`](resource-management.js): static resource registry, filters, KPI table rendering, and plan-fact Gantt prototype
- [`warehouse-simulation.html`](warehouse-simulation.html): premium digital-twin warehouse control tower for the 12-hour minute simulation; it loads `layout.json`, `events.jsonl`, `metrics-by-minute.csv`, `collision-report.csv`, and `report.json` evidence files and shows an isometric warehouse, RTP tasks, resource badges, collision callouts, route progress, KPI, and playback timeline
- [`warehouse-simulation.js`](warehouse-simulation.js): model-only replay engine with URL/config/file loaders, demo fallback, isometric canvas scene, resource trails, heatmap, collision root-cause feed, RTP task panel, route progress, click detail cards, and timeline markers
- [`warehouse-simulation.css`](warehouse-simulation.css): premium logistics control-tower styling for the digital-twin page
- [`case-pick-management.html`](case-pick-management.html): shift-dispatcher ARM for case-pick monitoring by pickers, customer pallets, routes, progress, shorts, and route blockers
- [`case-pick-management.js`](case-pick-management.js): lightweight ARM logic backed by `/api/case-pick` with demo fallback, filtering, picker transfer, short approval/rejection, and route analytics
- [`case-pick-tsd.html`](case-pick-tsd.html): compact picker TSD page for case picking customer pallets by SSCC with shift-gated login, scan confirmation, shorts, and pallet close
- [`case-pick-tsd.js`](case-pick-tsd.js): lightweight picker TSD logic backed by `/api/case-pick`
- [`wave-client-e2e-presentation.html`](wave-client-e2e-presentation.html): HTML slide deck for the client acceptance scenario covering wave creation, pick-face replenishment, direct rack/full-pallet picking, case picking, readiness, and checks
- [`production-orders.html`](production-orders.html): MES production-order passport and completion controls; raw supply planning is linked out to `raw-supply.html`
- [`finished-goods.html`](finished-goods.html): finished-goods SKU settings, warehouses/buffers, production batches, pallets, and SSCC stock
- [`finished-goods.js`](finished-goods.js): lightweight finished-goods list/settings/batch/stock logic

Design notes:

- fixed left navigation with product logo and operational modules
- compact top header with search, notifications, help, and user profile area
- KPI strip with eight compact metric cards and sparklines
- main work area split into production, raw-material warehouse, finished-goods warehouse, and warehouse settings panels
- [`api-audit.html`](api-audit.html) is a separate administrative page, not part of `Главная`
- [`external-outbox.html`](external-outbox.html) is a separate administrative page for Mercury/CRPT outbox diagnostics and retry
- [`rights-admin.html`](rights-admin.html) is a separate rights administration page backed by legacy `RUSERS` / `USER_GROUP` / `RIGHTS`
- [`bom.html`](bom.html) is a separate MES recipe/BOM page protected by `bom_view`; lifecycle buttons require `bom_edit`, `bom_approve`, `bom_block`, or `bom_make_primary`
- [`customers.html`](customers.html) is protected by `customer_view`; customer card changes require `customer_edit`; rule creation requires `customer_rule_edit`
- [`customer-orders.html`](customer-orders.html) is protected by `customer_order_view`; legacy import requires `customer_order_import`; fulfillment facts require `customer_fulfillment_view`
- [`raw-material.html`](raw-material.html) is protected by `raw_material_view`; editing SKU settings requires `raw_material_edit`; stock rows require `raw_material_stock_view`
- [`raw-supply.html`](raw-supply.html) is protected by `mes_raw_supply_view`; calculation, release, confirmation, and cancellation use `mes_raw_supply_calculate`, `mes_raw_transfer_create`, `mes_raw_transfer_confirm`, and `mes_raw_transfer_cancel`
- [`shift-supervisor-wave.html`](shift-supervisor-wave.html) is protected by `pick_wave_view`; it is the visual evidence panel for the client wave scenario before the production frontend page is implemented
- [`wave-replenishment.html`](wave-replenishment.html) is protected by `pick_wave_view`; Minimax/queue release and staging release use `pick_wave_launch`; rule editing uses `pick_topology_edit`
- [`resource-management.html`](resource-management.html) is protected by `resource_management_view`; future resource edits, shift management, dispatch, and replan actions use `resource_management_edit`, `resource_shift_edit`, `resource_session_manage`, and `resource_gantt_replan`
- [`warehouse-simulation.html`](warehouse-simulation.html) is protected by `pick_wave_view`; it is the visual player for `runtime/test-evidence/warehouse-minute-simulation/<run-id>/` artifacts generated by `tests/load/wave/warehouse_minute_simulation_load_test.py`
- [`case-pick-management.html`](case-pick-management.html) is protected by `case_pick_view`; transfer and operational management use `case_pick_manage`; short approval/rejection uses `case_pick_short_approve`
- [`case-pick-tsd.html`](case-pick-tsd.html) is protected by `case_pick_view`; scan confirmation, shorts, and close actions require `case_pick_execute`
- [`finished-goods.html`](finished-goods.html) is protected by `finished_goods_view`; editing SKU settings requires `finished_goods_edit`; stock rows require `finished_goods_stock_view`; batches require `finished_goods_batch_view`
- raw admin pages use the global admin session connection settings from `admin-auth.js`; working screens do not show technical permission or API connection fields
- [`product-shipment-settings.html`](product-shipment-settings.html) is protected by `quality_batch_view`; editing aging norms requires `quality_batch_edit`
- API page lists calls from `GET /api/admin/api-calls`, opens details, runs dry-run replay, and can repeat selected ID or date ranges through `POST /api/admin/api-calls/replay`
- [`admin-auth.js`](admin-auth.js) adds login/password entry and hides the API page unless the user has `api_audit_view`; real replay requires `api_audit_replay`
- Login uses the legacy Oracle user table `RUSERS`; the seeded local admin is `admin/admin123`.
- left navigation is rendered by [`admin-nav.js`](admin-nav.js); pages only set `data-active-nav`, while rights can hide protected items for non-privileged users
- left navigation has fixed sidebar width, fixed row sizing, stable scrollbar gutter, and SVG icons with a fixed icon slot to avoid visual jumping between pages
- retail demo customers are repaired/seeded through `scripts/seed-retail-customers.py`; do not seed Russian text through inline PowerShell commands
- light background, thin borders, small radii, dense tables, restrained blue/green accents
- no destructive database actions are represented in the raw prototype

This folder is a raw source/prototype. The maintained synthesis belongs in `wiki/`, and the future executable admin frontend should live outside `wiki-raw`.
