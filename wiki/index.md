# TMS Wiki Index

This is the maintained knowledge map for the TMS repository.

Start here for a fresh session:

- [overview.md](overview.md): project map, current focus, and boundaries
- [repositories/index.md](repositories/index.md): target GitHub repository and four-subrepository model
- [branches/index.md](branches/index.md): four logical branches of the project
- [runbooks/project_onramp.md](runbooks/project_onramp.md): first-5-minutes orientation
- [sources/index.md](sources/index.md): raw source catalog

## Logical Branches

- [branches/01_oracle_plsql_core.md](branches/01_oracle_plsql_core.md): Oracle schema, PL/SQL procedures, tables, functions, and core business rules
- [branches/02_csharp_desktop_client.md](branches/02_csharp_desktop_client.md): main C# WinForms operator application
- [branches/03_terminal_contour.md](branches/03_terminal_contour.md): handheld/scanner terminal client, terminal server, and operation confirmation flow
- [branches/04_external_integrations.md](branches/04_external_integrations.md): `SUPERMAG` / `Sfera`, imports, exports, and staging

## Subprojects

- [subprojects/windowsapplication2.md](subprojects/windowsapplication2.md): legacy WinForms WMS/TMS desktop application
- [subprojects/oracle_schema.md](subprojects/oracle_schema.md): reconstructed Oracle schema and deployment scripts
- [subprojects/wms_terminal_web.md](subprojects/wms_terminal_web.md): modern Web/PWA terminal application replacing the legacy terminal OS client

## Architecture

- [architecture/wms_mes_traceability_edd.md](architecture/wms_mes_traceability_edd.md): engineering design document for the WMS+MES+Traceability target architecture with Mercury and Honest Sign separation
- [architecture/wave_resource_execution_evidence_architecture.md](architecture/wave_resource_execution_evidence_architecture.md): accepted architecture decision that wave is the central operational object, people/equipment tasks use the resource model, TSD facts synchronize through warehouse-task sync or case-pick events, and every business process requires evidence-driven testing

## Database Mirror

- [database/index.md](database/index.md): local wiki mirror of the Oracle `RABAEV` schema and change discipline
- [database/oracle_change_protocol.md](database/oracle_change_protocol.md): required workflow for Oracle structure changes
- [database/feed_factory_traceability_schema.md](database/feed_factory_traceability_schema.md): schema mirror for feed-factory traceability, Mercury/CRPT lifecycle, API audit/replay, wave stock movement ledger, regulatory journal migrations, warehouse topology 038/039, linear pick-route invariant migration 040, warehouse map canvas/slot migration 041, and Oracle publish invariant package 042

## Concepts

- [concepts/external_integration_supermag.md](concepts/external_integration_supermag.md): `SUPERMAG` / `Sfera` as external ERP source
- [concepts/legacy_rights_model.md](concepts/legacy_rights_model.md): legacy `RUSERS` / `USER_GROUP` / `RIGHTS` model used by admin pages
- [concepts/oracle_environment.md](concepts/oracle_environment.md): recommended Oracle environment and schema separation
- [concepts/api_method_library.md](concepts/api_method_library.md): maintained `api-med` catalog of API methods, permissions, parameters, side effects, readiness checks, and verification, including the warehouse-map state API
- [concepts/regulatory_adapter_audit.md](concepts/regulatory_adapter_audit.md): audit/replay rules for real Mercury and Honest Sign adapters
- [concepts/tserver_api_registry.md](concepts/tserver_api_registry.md): legacy terminal API commands and `CALL_SPF` procedure registry
- [concepts/ui_interaction_rules.md](concepts/ui_interaction_rules.md): общие правила всплывающих подсказок, контекстной help-системы и визуального обозначения будущих/заглушечных UI-элементов
- [concepts/wiki_operating_model.md](concepts/wiki_operating_model.md): how this repository uses the Karpathy wiki pattern

## Runbooks

- [../scripts/README.md](../scripts/README.md): local Windows launch scripts for WMS API, admin frontend/raw UI reference, and terminal Web/PWA app
- [runbooks/create_api_server.md](runbooks/create_api_server.md): recommended API server stack and migration plan from `Tserver`
- [runbooks/evidence_driven_process_testing.md](runbooks/evidence_driven_process_testing.md): обязательный runbook для evidence-driven приемки бизнес-процессов: сценарий, модель данных, runner, Oracle/API инварианты, ARM/TSD screenshots, reports
- [../api/wms_api_server/README.md](../api/wms_api_server/README.md): first Python FastAPI implementation for WMS/TMS API and `Tserver` compatibility
- [runbooks/warehouse_task_domain_sync_operations.md](runbooks/warehouse_task_domain_sync_operations.md): эксплуатационная инструкция для мониторинга `RRL_WAREHOUSE_TASK_SYNC`, разбора ошибок и retry
- [runbooks/db_app_compatibility_check_2026_05_11.md](runbooks/db_app_compatibility_check_2026_05_11.md): compatibility check for Oracle, C# desktop client, and `Tserver`
- [runbooks/oracle_recovery_2026_05_11.md](runbooks/oracle_recovery_2026_05_11.md): Oracle VM recovery context and restore point after flashback repair
- [runbooks/project_onramp.md](runbooks/project_onramp.md): how to orient before changing code or docs

## Roadmap

- [roadmap/strategic_development_plan.md](roadmap/strategic_development_plan.md): strategic plan for DB compatibility, API boundary, queueing, Android terminals, and regulated integrations
- [roadmap/tactical_implementation_plan.md](roadmap/tactical_implementation_plan.md): tactical execution plan for feed-factory traceability, API, file exchange, and adapters
- [roadmap/wms_mes_traceability_strategic_plan.md](roadmap/wms_mes_traceability_strategic_plan.md): approved strategic plan for WMS+MES+Traceability implementation
- [roadmap/wms_mes_traceability_tactical_plan.md](roadmap/wms_mes_traceability_tactical_plan.md): tactical sprint plan for traceability spine, outbox, adapters, admin UI, MES, shipment, and recall
- [roadmap/picking_wave_implementation_plan.md](roadmap/picking_wave_implementation_plan.md): strategic and tactical implementation plan for picking planning, wave picking, reservations, admin UI, terminal execution, and WMS bridge
- [roadmap/current_checkpoint_2026_05_18.md](roadmap/current_checkpoint_2026_05_18.md): current reboot checkpoint, tactical plan, strategic plan, warehouse-task implementation, wave Minimax auto-trigger, shelf-life source selection, and wave loading-zone staging/UI status
- [roadmap/current_checkpoint_2026_05_20.md](roadmap/current_checkpoint_2026_05_20.md): recovered crash checkpoint for the warehouse digital twin, latest model-only evidence, React admin replay, and next stabilization steps
- [roadmap/wave_replenishment_queue_change_plan_2026_05_19.md](roadmap/wave_replenishment_queue_change_plan_2026_05_19.md): strategic and tactical change file for queued same-SKU wave replenishment, dynamic/generic pick-face release, readiness API, tests, risks, and next implementation steps

## Requirements

- [requirements/bom_production_block_tz.md](requirements/bom_production_block_tz.md): Russian technical assignment for MES BOM/recipe management, primary recipes, validity periods, and production-order integration
- [requirements/case_pick_tsd_tz.md](requirements/case_pick_tsd_tz.md): Russian technical assignment for picker TSD case picking of customer pallets, ARM monitoring/dispatch, wave-launch SSCC generation, address-level `PALLET_TYPE`, pick routes, scan settings, shorts/write-offs, inventory tasks, offline mode, and control workflow
- [requirements/case_pick_wave_load_test_tz.md](requirements/case_pick_wave_load_test_tz.md): Russian technical assignment for load/model testing of a case-pick wave: 7 clients, 78 customer pallets, clean warehouse fixture, pick-face replenishment, picking stages, runtime evidence, screenshots, and presentation artifacts
- [requirements/feed_factory_mercury_crpt_tz.md](requirements/feed_factory_mercury_crpt_tz.md): Russian technical assignment for feed-factory production, raw-material usage, Mercury, Honest Sign, aggregation, and shipment modes
- [requirements/finished_goods_admin_tz.md](requirements/finished_goods_admin_tz.md): Russian technical assignment for the finished-goods admin page: SKU settings, warehouses, production batches, pallets, SSCC, and stock
- [requirements/large_warehouse_minute_simulation_tz.md](requirements/large_warehouse_minute_simulation_tz.md): Russian technical assignment and first model-only implementation note for a 12-hour real-warehouse digital-twin load test with 50 clients, 10 waves, 1000 SKU, 1500 pick faces, urgent-only dynamic/overflow pick-face cells, minute-by-minute movement simulation, collision detection, resource shortage analysis, screenshots, and warehouse animation page
- [requirements/large_warehouse_map_drawing_tz.md](requirements/large_warehouse_map_drawing_tz.md): Russian technical assignment for an Excel-like lightweight 2D editor for drawing large warehouse maps at `35 x 90 x 6` scale, assigning cell roles, zooming/panning, multi-area bulk selection, level-persistent selection, format painter, context help, fractional pick-face split presets with visual split lines, and publishing drafts into topology
- [requirements/large_warehouse_map_real_warehouse_binding_tz.md](requirements/large_warehouse_map_real_warehouse_binding_tz.md): Russian technical assignment for binding the large warehouse map editor to real Oracle warehouses; now includes DB-backed canvas/camera APIs, empty-camera unavailable default, bootstrap canvas from existing DB cells, selected-area standard layouts, sticky sidebar format painter, audited detailed context help plus a module instruction modal, explicit pick/storage fractional slot preset controls with Canvas split-line rendering, side-flyout context menu variants including full-size pick/storage and pick `2/1..3/4` plus custom `V/G`, storage-slot capacity/order editing, preview-only topology projection, optimistic draft diff/locking for cells plus canvas metadata/objects/passages/links, draft pick-route order preview, route validation/publish draft evidence, Sprint 18 performance/evidence hardening, Sprint 19 Oracle publish invariant pack, Sprint 20 DB-backed save/load API switch, Sprint 21 projection-to-topology persistence, Sprint 22 route rows to Oracle pick route, Sprint 23 Oracle publish action, Sprint 24 UI publish controls with visual evidence, Sprint 25 published warehouse reload, and Sprint 26 final acceptance checkpoint
- [requirements/large_warehouse_map_functional_testing_tz.md](requirements/large_warehouse_map_functional_testing_tz.md): Russian technical assignment for functional acceptance testing of the large warehouse map on an existing Oracle warehouse without canvas: create canvas, two cameras, up to 10 gates, about 1500 storage cells per camera, pick cells across 6 levels, mixed route patterns in one camera, save/publish/reload evidence, full UI label/help audit, functional completeness conclusions, usability conclusions, and the follow-up TZ for screen/menu optimization.
- [requirements/large_warehouse_map_functional_testing_result_2026_05_23.md](requirements/large_warehouse_map_functional_testing_result_2026_05_23.md): functional audit result for the large warehouse map: Playwright UI test passes 19/19 checks, fixes visual pick-address labels on canvas and preserves selection after route draft rebuild, with a recommendation to run full publish/reload only on a controlled Oracle fixture.
- [requirements/large_warehouse_map_publish_reload_fixture_result_2026_05_23.md](requirements/large_warehouse_map_publish_reload_fixture_result_2026_05_23.md): acceptance result for the `Publish/Reload Fixture` sprint: isolated `WARE_ID=0` publishes `canvas=35`, `topology=19`, and `route=117`, then reloads warehouse state with 19/19 PASS checks, 144 route rows, and zero storage/non-pick route rows.
- [requirements/large_warehouse_map_projection_bulk_save_fix_2026_05_23.md](requirements/large_warehouse_map_projection_bulk_save_fix_2026_05_23.md): architecture fix result for warehouse-map projection persistence: replacing fake per-row `execute_many` and per-cell sequence calls with real `executemany` plus batched sequence allocation reduced a 5042-cell topology save from about 762 seconds to 3.9 seconds, with two-camera publish/reload evidence.
- [requirements/large_warehouse_map_two_camera_scale_result_2026_05_23.md](requirements/large_warehouse_map_two_camera_scale_result_2026_05_23.md): two-camera scale acceptance result after the bulk-save architecture fix: `3000` storage cells, `1202` pick cells, `5042` topology cells, two cameras, one camera link, route publish/reload, and `projection/save-to-topology = 2002 ms`.
- [requirements/large_warehouse_map_fixture_cleanup_idempotency_result_2026_05_23.md](requirements/large_warehouse_map_fixture_cleanup_idempotency_result_2026_05_23.md): fixture cleanup and idempotent retry result for warehouse-map acceptance: archive canvas API, `FX-/TC-` cleanup tool, repeat two-camera scale run, and HTTP retry returning existing topology/route instead of creating duplicates.
- [requirements/large_warehouse_map_operation_idempotency_result_2026_05_23.md](requirements/large_warehouse_map_operation_idempotency_result_2026_05_23.md): production idempotency-key result for warehouse-map canvas save, topology projection, route save, and publish; migration `043` adds Oracle columns/indexes, API smoke proves repeated requests return the same ids, and the two-camera 5042-cell scale fixture still passes.
- [requirements/large_warehouse_map_publish_reload_ux_result_2026_05_23.md](requirements/large_warehouse_map_publish_reload_ux_result_2026_05_23.md): publish/reload UX polish result for the large warehouse map: ribbon and left panel now expose the full Canvas DB -> Topology DB -> Route DB -> Publish Oracle -> Reload workflow, show operation idempotency keys/statuses, and pass visual smoke plus backend idempotency regression.
- [requirements/large_warehouse_map_full_ui_functional_acceptance_result_2026_05_23.md](requirements/large_warehouse_map_full_ui_functional_acceptance_result_2026_05_23.md): full UI functional acceptance result for the large warehouse map on a non-zero Oracle warehouse: excludes `WARE_ID=0`, passes 19/19 UI audit checks, publishes/reloads a two-camera 5042-cell fixture on `WARE_ID=1`, verifies idempotency retries, and marks the next strategic gate as final model invariant review.
- [requirements/large_warehouse_map_final_model_invariant_review_2026_05_23.md](requirements/large_warehouse_map_final_model_invariant_review_2026_05_23.md): final model invariant review for the large warehouse map: confirms canvas remains a planning/layout object, published topology/route are the operational source, storage slots stay out of pick routes, explicit publish is validated by Oracle, idempotency keys protect retries, and the next strategic gate is release checkpoint and cleanup.
- [requirements/large_warehouse_map_release_checkpoint_cleanup_2026_05_23.md](requirements/large_warehouse_map_release_checkpoint_cleanup_2026_05_23.md): release checkpoint and cleanup result for the large warehouse map: identifies warehouse-map commit scope versus unrelated dirty worktree material, documents fixture production guards, tightens API method documentation, and marks the release checkpoint accepted pending explicit commit scope review.
- [requirements/large_warehouse_map_current_status.md](requirements/large_warehouse_map_current_status.md): reboot anchor for the active LargeWarehouseMap / `warehouse-map` workstream: current scope, `3000`-only port rule, half-day green evidence, known remaining gaps, and fresh-session checklist.
- [requirements/large_warehouse_map_zero_warehouse_ban_2026_05_23.md](requirements/large_warehouse_map_zero_warehouse_ban_2026_05_23.md): zero warehouse ban result for the large warehouse map: deletes live `RRL_WARES.ID=0` and related warehouse-map/topology/route fixture rows, adds Oracle positive-id constraints, updates API validation to reject `ware_id=0`, and records live apply/verify/smoke evidence for migration `044`.
- [requirements/large_warehouse_map_release_scope_review_2026_05_23.md](requirements/large_warehouse_map_release_scope_review_2026_05_23.md): release scope review for the large warehouse map: names the warehouse-map files to include, unrelated worktree files to exclude, the minimal final release gate, and the next strategic move toward commit/PR packaging.
- [requirements/large_warehouse_map_excel_canvas_actions_tz.md](requirements/large_warehouse_map_excel_canvas_actions_tz.md): Russian technical assignment for expanding warehouse map canvas actions by Excel analogy: every working function must have a left-menu action and a context-menu tree duplicate, `Сохранить канвас` must exist in both places, Excel functions are mapped to needed canvas-map analogs with proposed icons and priorities, the first implementation checkpoint adds an Excel-like `Главная` ribbon as a third fast entry point, `Excel Actions 2` adds parity for editing/filters/navigation/validation, `Excel Actions 3` compacts the ribbon/context menu while adding template/layout and multi-pattern route actions, and the 2026-05-26 fixes scope `Регулярный склад` and fractional pick/storage generation to the active selection when one exists.
- [requirements/large_warehouse_map_ui_test_plan_2026_05_26.md](requirements/large_warehouse_map_ui_test_plan_2026_05_26.md): UI regression and end-to-end acceptance checklist for warehouse-map drawing, stale-state warehouse switching, selection-scoped templates, draft/canvas save, route build, Oracle publish, reload, negative cases, and the 2026-05-27 half-day green run.
- [requirements/mes_production_completion_prompt.md](requirements/mes_production_completion_prompt.md): prompt for implementing MES production completion through a movement journal and controlled legacy WMS bridge
- [requirements/mes_raw_shortage_replenishment_tz.md](requirements/mes_raw_shortage_replenishment_tz.md): Russian technical assignment for BOM raw-material shortage calculation and transfer tasks from raw warehouse to production
- [requirements/modern_terminal_app_tz.md](requirements/modern_terminal_app_tz.md): Russian technical assignment for the modern Web/PWA terminal app replacing the legacy terminal OS client
- [requirements/picking_planning_tz.md](requirements/picking_planning_tz.md): Russian technical assignment for customer-order picking planning, reservations, customer rules, route/dock context, and shipment-part splitting
- [requirements/raw_material_admin_tz.md](requirements/raw_material_admin_tz.md): Russian technical assignment for the raw-material admin page: raw SKU settings, raw warehouses, and stock by selected warehouses
- [requirements/resource_management_module_tz.md](requirements/resource_management_module_tz.md): Russian technical assignment for a separate resource-management module covering reachtrucks, KIKA, forklifts, trolleys, pickers, loading teams, cooking, packing, shifts, sessions, dispatch, and plan-fact Gantt
- [requirements/warehouse_resource_planning_tz.md](requirements/warehouse_resource_planning_tz.md): Russian technical assignment for warehouse resources, reachtruck/KIKA equipment, driver shift login, task dispatch, planned Gantt, factual Gantt, and plan-fact load analysis
- [requirements/warehouse_tasks_reachtruck_tz.md](requirements/warehouse_tasks_reachtruck_tz.md): Russian technical assignment for common warehouse tasks, reachtruck-driver execution, wave pick-face replenishment, and full-pallet loading-zone staging
- [requirements/warehouse_task_domain_sync_tz.md](requirements/warehouse_task_domain_sync_tz.md): Russian technical assignment for synchronizing completed warehouse-task facts back into MES, wave, picking, and shipment domains; current runtime covers wave replenishment, wave full-pallet staging, MES raw supply, and finished-goods placement
- [requirements/warehouse_topology_pick_route_tz.md](requirements/warehouse_topology_pick_route_tz.md): Russian technical assignment and implementation checkpoint for warehouse topology and pick-route administration as rare versioned master-data processes, with graphical generation, route publishing, recommendations, gate-distance matrix, dock/staging separation, split pick-face slots, stable route-area selection UX, test-ready admin UI, PL/SQL/API contracts, and digital-twin integration
- [requirements/warehouse_topology_acceptance_tz_2026_05_22.md](requirements/warehouse_topology_acceptance_tz_2026_05_22.md): tactical May 22 acceptance scope for topology admin, warehouse topology API, Oracle route invariants, and visual evidence screenshots
- [requirements/wave_case_pick_replenishment_tz.md](requirements/wave_case_pick_replenishment_tz.md): Russian technical assignment and current runtime checkpoint for replenishing pick-face cells under wave case picking, including `MINIMAX`, immediate replenishment, queued same-SKU drops, urgent-only dynamic/generic pick-face release, layout optimization, pallet/half-pallet, and fill-to-volume strategies
- [requirements/wave_client_e2e_acceptance_scenario.md](requirements/wave_client_e2e_acceptance_scenario.md): Russian client acceptance scenario for wave creation, pick-face replenishment, direct rack/full-pallet picking, case picking, readiness, free/physical stock evidence, TSD video fixation, negative checks, and automation
- [requirements/wave_picking_tz.md](requirements/wave_picking_tz.md): Russian technical assignment for wave picking, hard reservations, pick-face replenishment, launch dialog, and wave execution
- [requirements/wave_picking_admin_tz.md](requirements/wave_picking_admin_tz.md): Russian technical assignment for the wave-picking admin page, launch dialog, rights, monitoring, and operational controls
- [requirements/wave_user_scenarios_functional_tz.md](requirements/wave_user_scenarios_functional_tz.md): Russian technical assignment for functional user-scenario checks: assembling a wave from orders, replenishing pick faces, direct rack/full-pallet picking, case picking, 10x replenishment collision, and truck shipment readiness/dispatch

## Control Files

- [WIKI_SCHEMA.md](WIKI_SCHEMA.md): root wiki schema and maintenance rules
- [log.md](log.md): append-only wiki maintenance log
- [../AGENTS.md](../AGENTS.md): agent-facing onramp for future sessions
