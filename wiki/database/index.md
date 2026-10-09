> Актуальное продолжение 121–130: [[nicora_stock_posting_continuation_20261008]]. 47 package pairs; 10 ADAPTED / 21 UNCONVERTED; PREPARED, полного cutover нет.

# Database Mirror: Oracle Schema

## Role

This directory is the local wiki mirror of the Oracle `RABAEV` schema.

Its purpose is to let future development reason about tables, procedures, packages, and integration contracts without repeatedly querying the live Oracle VM for basic structure.

The live Oracle database remains the runtime authority. The wiki mirror is the maintained working map that explains what the schema is supposed to mean and how changes should move through the project.

## Active Oracle Context

- 08.10.2026: [Реализация stock posting](nicora_stock_posting_implementation.md): разрешённая очистка dev, 013/014/015 APPLIED, unique/NOT NULL/P+H constraints и служебные metadata. Новая physical posting ещё выключена; direct SYS package grants отсутствуют. Не выдавать подготовку за целый cutover.

- 07.10.2026: [Целевой stock contract](nicora_stock_posting_target.md) и [ТЗ 2.0](../requirements/stock_posting_core_tz.md): P/H, единый HARD, stock key/полный concurrency protocol, карантинные ячейки. Read-only metadata подтверждены; это проектируемое изменение, не применённое DDL/новое ядро.

- 07.10.2026: [NI03 task effect, 010](nicora_ni03_task_effect.md): COMPLETION_HASH/JSON в существующей WAREHOUSE_TASK; installed/live metadata confirmed, один cursor для WAVE completion/stock/reservation. Новый inventory/task registry не создаётся.

- 07.10.2026: [NI02 SAP–СТ bridge](nicora_ni02_store_orders.md), migration 009 установлена в той же RABAEV: сохранённая подготовка и PLANNED fulfillment; существующее TRANSTASK_ID назначение сохранено. Вложенная SSCC агрегация в CRPT найдена, складской жизненный цикл требует доработки NI04 — [анализ](../components/nicora_global_reuse_analysis_20261007.md).

- 07.10.2026: владелец подтвердил dev-изоляцию ORCL и поручил разработку/переработку структуры непосредственно в RABAEV. Новая схема не создаётся. [NS00 baseline](nicora_ns00_dev_baseline.md): 59 INVALID перекомпилированы до 0 без изменения исходников; активных ошибок вне BIN$ нет.

- Live development service: `127.0.0.1:1521/orcl`
- Application schema: `RABAEV`
- Compatibility target: legacy C# `WindowsApplication2`, `Tserver`, and future API server
- Current safety rule: no destructive Oracle DDL/DML without explicit permission and a VM snapshot or restore plan

Do not store database passwords, personal credentials, private tokens, or signing secrets in this wiki.

## Mirror Sources

The local schema mirror is maintained from these sources:

- [`../../db/windowsapplication2_xp12_oracle/`](../../db/windowsapplication2_xp12_oracle/): normalized Oracle schema scripts
- [`../../db/clean_install/`](../../db/clean_install/): from-zero install kit that orchestrates structure, settings, fixtures, profiles, and verification for a separate isolated `RABAEV` installation
- [`../../db/compatibility_fixes/`](../../db/compatibility_fixes/): dated compatibility patches applied after recovery
- [`../../db/restore_points/`](../../db/restore_points/): exported restore points for disaster recovery
- live read-only Oracle checks through managed ODP.NET when the wiki or scripts need verification

## Change Rule

Every Oracle schema change must be represented in three places:

1. Wiki mirror: describe the intended table/procedure/package shape and business meaning here.
2. SQL source: update the relevant script under `db/windowsapplication2_xp12_oracle/` or a dated patch under `db/compatibility_fixes/`.
3. Live Oracle: apply only after the change is understood, permission is clear, and the safety rule is satisfied.

After applying a change, verify `USER_OBJECTS` and `USER_ERRORS`, then append [`../log.md`](../log.md).

## Working Protocol

1. Read this mirror before querying Oracle for structure.
2. If the mirror is incomplete, inspect local SQL scripts first.
3. Use live Oracle read-only queries to confirm uncertain facts.
4. For proposed schema changes, update the wiki mirror before or alongside the SQL patch.
5. Apply to Oracle only after the intended effect is documented.
6. Record verification results: connection target, invalid object count, and any remaining errors.

## Initial Mirror Scope

The first priority is to mirror the parts of the schema touched by active modernization work:

- pallets and production batches: `RRL_PALLETS`, `RRL_REMAINS`, `RRL_SBORKA_PALLETS`, `RRL_SBORKA_PALLET_ROWS`
- incoming and outgoing documents: `RRL_PRIHOD_NAKLAD`, `RRL_PRIHOD_NAKLAD_ROWS`, `RRL_OTHOD_NAKLAD`, `RRL_OTHOD_NAKLAD_ROWS`
- terminal/API procedure surface used by `Tserver`
- compatibility packages used by the desktop client: `COMPL`, `PRIHOD`, `PALL_SPLITTER`, `TRANSPORT_PLN`, `STORE_ADRESSES`, `HELP`
- future regulated integration fields for `Меркурий` and `Честный знак`

## Versioned Migrations

- [feed_factory_traceability_schema.md](feed_factory_traceability_schema.md): local mirror for migration `2026-05-17-001-feed-factory-traceability`

## Clean Install Kit

The clean install entry point is [`../../db/clean_install/README.md`](../../db/clean_install/README.md).

Decision:

- Keep canonical legacy object SQL in `db/windowsapplication2_xp12_oracle/`.
- Keep reviewed deltas in `db/migrations/`.
- Use `db/clean_install/` only for install orchestration, phase scripts, profiles, fixtures, and verification.

Profiles:

- `legacy-runtime`: legacy structure plus minimal runtime/admin settings.
- `legacy-master`: legacy structure plus full imported master reference data.
- `modern-prod`: legacy master data plus WMS/MES/warehouse-map and TMS-2 production structure.
- `tms2-acceptance`: `modern-prod` plus Dobrotseny, Sprint 9 planner template, and test geocode fixtures.

Clean install assumes a separate Oracle service/PDB/VM with owner `RABAEV`; the legacy app and PL/SQL remain hard-wired to that owner. The TMS-2 clean production profile intentionally does not replay historical `042/043` transport migrations because they reference the non-existent legacy column `RRL_SBORKA_PALLETS.DELETED`; it applies the final compatible TMS-2 structure through `051+` and verifies the resulting objects.

## Related Pages

- [Oracle / PL/SQL Core](../branches/01_oracle_plsql_core.md)
- [Oracle Schema subproject](../subprojects/oracle_schema.md)
- [DB/app compatibility check](../runbooks/db_app_compatibility_check_2026_05_11.md)
- [Oracle recovery runbook](../runbooks/oracle_recovery_2026_05_11.md)


## NICORA маркировка редакция 57

[nicora_track_trace_requirements.md](nicora_track_trace_requirements.md) — требования к общему поэкземплярному и регуляторному учёту, настройкам SKU и нескольким профилям (табак, CRPT/Честный знак, ЕГАИС, другие системы). Существующие CRPT-объекты — кандидаты переиспользования; фактическое отображение и миграции утверждаются после GAP. Все изменения относятся к RABAEV. На 07.10.2026 этим дополнением DDL не применялся; наличие документа не означает наличие универсальной реализации.


## NS00 test fixture

[nicora_ns00_fixture.md](nicora_ns00_fixture.md) — реализованное ядро DS-BASE в RABAEV: 22 owned строки, девять таблиц, exact-key/provenance reset, transactional rollback и сохранность внешнего запаса. Seed data only, без структурной миграции.

## NI01: SAP Retail и настройки SKU

[NI01 SAP, приёмка и размещение](nicora_ni01_sap_retail.md): 7 октября 2026 года, миграции 001–007 установлены в существующей RABAEV. Функциональная реализация завершена: article apply, приход/марки/весовые единицы, этикетки/слоты/сверка/ACK; metadata прочитана, промышленная приёмка не выполнялась.

## NI02 — заказы магазинов SAP

[Неизменный заказ и календарь](nicora_ni02_store_orders.md): migration 2026-10-07-008-ni02-store-orders установлена 07.10.2026 в существующей RABAEV. Три добавочные таблицы и три guard trigger VALID; source checkpoint и apply logs runtime/ni02. Потребность сохраняется в действующих customer orders, stock не меняется. NI02 in_progress.
