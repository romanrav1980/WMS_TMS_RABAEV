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

## Database Mirror

- [database/index.md](database/index.md): local wiki mirror of the Oracle `RABAEV` schema and change discipline
- [database/oracle_change_protocol.md](database/oracle_change_protocol.md): required workflow for Oracle structure changes
- [database/feed_factory_traceability_schema.md](database/feed_factory_traceability_schema.md): schema mirror for the first feed-factory traceability migration

## Concepts

- [concepts/external_integration_supermag.md](concepts/external_integration_supermag.md): `SUPERMAG` / `Sfera` as external ERP source
- [concepts/oracle_environment.md](concepts/oracle_environment.md): recommended Oracle environment and schema separation
- [concepts/tserver_api_registry.md](concepts/tserver_api_registry.md): legacy terminal API commands and `CALL_SPF` procedure registry
- [concepts/wiki_operating_model.md](concepts/wiki_operating_model.md): how this repository uses the Karpathy wiki pattern

## Runbooks

- [runbooks/create_api_server.md](runbooks/create_api_server.md): recommended API server stack and migration plan from `Tserver`
- [runbooks/db_app_compatibility_check_2026_05_11.md](runbooks/db_app_compatibility_check_2026_05_11.md): compatibility check for Oracle, C# desktop client, and `Tserver`
- [runbooks/oracle_recovery_2026_05_11.md](runbooks/oracle_recovery_2026_05_11.md): Oracle VM recovery context and restore point after flashback repair
- [runbooks/project_onramp.md](runbooks/project_onramp.md): how to orient before changing code or docs

## Roadmap

- [roadmap/strategic_development_plan.md](roadmap/strategic_development_plan.md): strategic plan for DB compatibility, API boundary, queueing, Android terminals, and regulated integrations

## Requirements

- [requirements/feed_factory_mercury_crpt_tz.md](requirements/feed_factory_mercury_crpt_tz.md): Russian technical assignment for feed-factory production, raw-material usage, Mercury, Honest Sign, aggregation, and shipment modes

## Control Files

- [WIKI_SCHEMA.md](WIKI_SCHEMA.md): root wiki schema and maintenance rules
- [log.md](log.md): append-only wiki maintenance log
- [../AGENTS.md](../AGENTS.md): agent-facing onramp for future sessions
