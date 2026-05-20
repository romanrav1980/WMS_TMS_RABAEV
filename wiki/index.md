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
- [database/feed_factory_traceability_schema.md](database/feed_factory_traceability_schema.md): schema mirror for feed-factory traceability, Mercury/CRPT lifecycle, API audit/replay, wave stock movement ledger, regulatory journal migrations, and live apply notes for the warehouse topology 038/039 layer

## Concepts

- [concepts/external_integration_supermag.md](concepts/external_integration_supermag.md): `SUPERMAG` / `Sfera` as external ERP source
- [concepts/legacy_rights_model.md](concepts/legacy_rights_model.md): legacy `RUSERS` / `USER_GROUP` / `RIGHTS` model used by admin pages
- [concepts/oracle_environment.md](concepts/oracle_environment.md): recommended Oracle environment and schema separation
- [concepts/api_method_library.md](concepts/api_method_library.md): maintained `api-med` catalog of API methods, permissions, parameters, side effects, readiness checks, and verification
- [concepts/regulatory_adapter_audit.md](concepts/regulatory_adapter_audit.md): audit/replay rules for real Mercury and Honest Sign adapters
- [concepts/tserver_api_registry.md](concepts/tserver_api_registry.md): legacy terminal API commands and `CALL_SPF` procedure registry
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
- [requirements/mes_production_completion_prompt.md](requirements/mes_production_completion_prompt.md): prompt for implementing MES production completion through a movement journal and controlled legacy WMS bridge
- [requirements/mes_raw_shortage_replenishment_tz.md](requirements/mes_raw_shortage_replenishment_tz.md): Russian technical assignment for BOM raw-material shortage calculation and transfer tasks from raw warehouse to production
- [requirements/modern_terminal_app_tz.md](requirements/modern_terminal_app_tz.md): Russian technical assignment for the modern Web/PWA terminal app replacing the legacy terminal OS client
- [requirements/picking_planning_tz.md](requirements/picking_planning_tz.md): Russian technical assignment for customer-order picking planning, reservations, customer rules, route/dock context, and shipment-part splitting
- [requirements/raw_material_admin_tz.md](requirements/raw_material_admin_tz.md): Russian technical assignment for the raw-material admin page: raw SKU settings, raw warehouses, and stock by selected warehouses
- [requirements/resource_management_module_tz.md](requirements/resource_management_module_tz.md): Russian technical assignment for a separate resource-management module covering reachtrucks, KIKA, forklifts, trolleys, pickers, loading teams, cooking, packing, shifts, sessions, dispatch, and plan-fact Gantt
- [requirements/warehouse_resource_planning_tz.md](requirements/warehouse_resource_planning_tz.md): Russian technical assignment for warehouse resources, reachtruck/KIKA equipment, driver shift login, task dispatch, planned Gantt, factual Gantt, and plan-fact load analysis
- [requirements/warehouse_tasks_reachtruck_tz.md](requirements/warehouse_tasks_reachtruck_tz.md): Russian technical assignment for common warehouse tasks, reachtruck-driver execution, wave pick-face replenishment, and full-pallet loading-zone staging
- [requirements/warehouse_task_domain_sync_tz.md](requirements/warehouse_task_domain_sync_tz.md): Russian technical assignment for synchronizing completed warehouse-task facts back into MES, wave, picking, and shipment domains; current runtime covers wave replenishment, wave full-pallet staging, MES raw supply, and finished-goods placement
- [requirements/warehouse_topology_pick_route_tz.md](requirements/warehouse_topology_pick_route_tz.md): Russian technical assignment and implementation checkpoint for warehouse topology and pick-route administration as rare versioned master-data processes, with graphical generation, route publishing, recommendations, gate-distance matrix, dock/staging separation, split pick-face slots, route-area selection UX, test-ready admin UI, PL/SQL/API contracts, and digital-twin integration
- [requirements/wave_case_pick_replenishment_tz.md](requirements/wave_case_pick_replenishment_tz.md): Russian technical assignment and current runtime checkpoint for replenishing pick-face cells under wave case picking, including `MINIMAX`, immediate replenishment, queued same-SKU drops, urgent-only dynamic/generic pick-face release, layout optimization, pallet/half-pallet, and fill-to-volume strategies
- [requirements/wave_client_e2e_acceptance_scenario.md](requirements/wave_client_e2e_acceptance_scenario.md): Russian client acceptance scenario for wave creation, pick-face replenishment, direct rack/full-pallet picking, case picking, readiness, free/physical stock evidence, TSD video fixation, negative checks, and automation
- [requirements/wave_picking_tz.md](requirements/wave_picking_tz.md): Russian technical assignment for wave picking, hard reservations, pick-face replenishment, launch dialog, and wave execution
- [requirements/wave_picking_admin_tz.md](requirements/wave_picking_admin_tz.md): Russian technical assignment for the wave-picking admin page, launch dialog, rights, monitoring, and operational controls
- [requirements/wave_user_scenarios_functional_tz.md](requirements/wave_user_scenarios_functional_tz.md): Russian technical assignment for functional user-scenario checks: assembling a wave from orders, replenishing pick faces, direct rack/full-pallet picking, case picking, 10x replenishment collision, and truck shipment readiness/dispatch

## Control Files

- [WIKI_SCHEMA.md](WIKI_SCHEMA.md): root wiki schema and maintenance rules
- [log.md](log.md): append-only wiki maintenance log
- [../AGENTS.md](../AGENTS.md): agent-facing onramp for future sessions
