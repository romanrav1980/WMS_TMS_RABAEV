> Актуальное продолжение 121–130: [[retailcase_stock_posting_continuation_20261008]]. 47 package pairs; 10 ADAPTED / 21 UNCONVERTED; PREPARED, полного cutover нет.

# Database Mirror: Oracle Schema

- [Карантин по назначенной роли23.10](quarantine_role_scope_20261023.md): живой403 воспроизведён, подготовлен совместимый native кандидат; товарный цикл ещё проверяется.

- [Проведение брака23.10](tradecase_quality_posting_20261023.md): C0153 и исправления применены, настоящий цикл2EA/повтор/роль проверены. Реальные ответы внешних систем не приняты.

- [Обновление дорожных плеч23.10](trip_road_refresh_20261023.md): ограниченная команда и журнал квитанций подготовлены; приёмка ещё не завершена.
- [Дела качества23.10](tradecase_quality_case_20261023.md): C0152 установлен, откат и повтор прошли; проведение списания и native удержание принимает C0153.

- [Правила доставки магазина23.10](store_delivery_rules_20261023.md): существующие поля адреса записываются вместе с профилем; неизменные повторы и конфликт legacy-изменения проверены в Oracle. DDL не менялась.

- 15.10.2026: [[retailcase_wares_identity_keys_20261015]] — APPLIED ID PK и обязательное уникальное NAME по решению владельца;291 строка сохранена,4 отрицательные проверки PASS, actual-time4FK.

## Role

- 16.10.2026: [[retailcase_hu_scoped_execute_20261016]] — basic HU CREATE/ATTACH/DETACH/MOVE по WARE/GROUP APPLIED/5SHA/INVALID0;3EA/replay/revoke/foreign/rollback/REV и legacy PASS,14 HTTP/max219мс.

- 16.10.2026: [[retailcase_interware_case_bridge_20261016]] — immutable CASE carrier bridge APPLIED/34SHA и JSON scalar fix/1SHA; mixed26EA два плеча и магазин PASS. [[retailcase_manual_warehouse_qc_20261016]]/[[retailcase_manual_qc_load_origin_20261016]] — ручной QC и его loading provenance APPLIED/4+3SHA/INVALID0; электронные API сохранены.

16.10: [[retailcase_case_return_scope_20261016]] — scoped manager RETURN25EA/10HTTP APPLIED с отдельным compile completion; [[retailcase_single_load_scope_20261016]] — scoped single LOAD25EA/30HTTP APPLIED. Текущая цепочка37 sources/10 frozen kits сверена, ERROR0/INVALID0 (`reports/retailcase/2026-10-16/finish-gate/oracle-current.json`).

This directory is the local wiki mirror of the Oracle `RABAEV` schema.

Its purpose is to let future development reason about tables, procedures, packages, and integration contracts without repeatedly querying the live Oracle VM for basic structure.

The live Oracle database remains the runtime authority. The wiki mirror is the maintained working map that explains what the schema is supposed to mean and how changes should move through the project.

## Active Oracle Context

- 08.10.2026: [Реализация stock posting](retailcase_stock_posting_implementation.md): разрешённая очистка dev, 013/014/015 APPLIED, unique/NOT NULL/P+H constraints и служебные metadata. Новая physical posting ещё выключена; direct SYS package grants отсутствуют. Не выдавать подготовку за целый cutover.

- 07.10.2026: [Целевой stock contract](retailcase_stock_posting_target.md) и [ТЗ 2.0](../requirements/stock_posting_core_tz.md): P/H, единый HARD, stock key/полный concurrency protocol, карантинные ячейки. Read-only metadata подтверждены; это проектируемое изменение, не применённое DDL/новое ядро.

- 07.10.2026: [NI03 task effect, 010](retailcase_ni03_task_effect.md): COMPLETION_HASH/JSON в существующей WAREHOUSE_TASK; installed/live metadata confirmed, один cursor для WAVE completion/stock/reservation. Новый inventory/task registry не создаётся.

- 07.10.2026: [NI02 SAP–СТ bridge](retailcase_ni02_store_orders.md), migration 009 установлена в той же RABAEV: сохранённая подготовка и PLANNED fulfillment; существующее TRANSTASK_ID назначение сохранено. Вложенная SSCC агрегация в CRPT найдена, складской жизненный цикл требует доработки NI04 — [анализ](../components/retailcase_global_reuse_analysis_20261007.md).

- 07.10.2026: владелец подтвердил dev-изоляцию ORCL и поручил разработку/переработку структуры непосредственно в RABAEV. Новая схема не создаётся. [NS00 baseline](retailcase_ns00_dev_baseline.md): 59 INVALID перекомпилированы до 0 без изменения исходников; активных ошибок вне BIN$ нет.

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


## RETAILCASE маркировка редакция 57

[retailcase_track_trace_requirements.md](retailcase_track_trace_requirements.md) — требования к общему поэкземплярному и регуляторному учёту, настройкам SKU и нескольким профилям (табак, CRPT/Честный знак, ЕГАИС, другие системы). Существующие CRPT-объекты — кандидаты переиспользования; фактическое отображение и миграции утверждаются после GAP. Все изменения относятся к RABAEV. На 07.10.2026 этим дополнением DDL не применялся; наличие документа не означает наличие универсальной реализации.


## NS00 test fixture

[retailcase_ns00_fixture.md](retailcase_ns00_fixture.md) — реализованное ядро DS-BASE в RABAEV: 22 owned строки, девять таблиц, exact-key/provenance reset, transactional rollback и сохранность внешнего запаса. Seed data only, без структурной миграции.

## NI01: SAP Retail и настройки SKU

[NI01 SAP, приёмка и размещение](retailcase_ni01_sap_retail.md): 7 октября 2026 года, миграции 001–007 установлены в существующей RABAEV. Функциональная реализация завершена: article apply, приход/марки/весовые единицы, этикетки/слоты/сверка/ACK; metadata прочитана, промышленная приёмка не выполнялась.

## NI02 — заказы магазинов SAP

[Неизменный заказ и календарь](retailcase_ni02_store_orders.md): migration 2026-10-07-008-ni02-store-orders установлена 07.10.2026 в существующей RABAEV. Три добавочные таблицы и три guard trigger VALID; source checkpoint и apply logs runtime/ni02. Потребность сохраняется в действующих customer orders, stock не меняется. NI02 in_progress.
# Текущее дополнение 2026-10-16

[HU thermal admission](retailcase_hu_thermal_admission_20261016.md): dev APPLIED/13SHA/INVALID0,15 native matrix checks; mixed ASM+BOX24+EA1 tree26EA and HTTP revoke/preview PASS; manifest/interWARE open.

[Additive legacy task scopes](retailcase_additive_legacy_task_scopes_20261016.md): dev APPLIED/23SHA/INVALID0; foreign-home flat+WARE role new CLAIM/START/BOX24+EA1/CLOSE PASS, revoke403.

[Inventory task scoped claim/count](retailcase_inventory_task_scope_20261016.md): dev APPLIED/8SHA/INVALID0; positive shortage/claim/count/replay/rights/rollback PASS,19 HTTP pairs/max258ms; QA retired.

[Scoped исполнение сборки на весах](retailcase_assembly_scoped_execute_20261016.md): dev APPLIED; package-only комплект, native close UOW и явная перекомпиляция зависимостей. 26 SHA/INVALID0/entry negatives PASS; полный бизнес-сценарий ещё не принят.

[Independent shortage decisions](retailcase_short_independent_scope_20261016.md): dev APPLIED/7SHA/INVALID0;10HTTP/current role/revoke/independent decision/REV lock PASS.

[Accepted-short inventory audit](retailcase_short_independent_scope_20261016.md): dev APPLIED/4SHA/INVALID0; accepted-short count/replay/rollback and fresh RESTORE regression PASS, existing count writer retained.

[Expected consolidation manifest](retailcase_consolidation_manifest_20261016.md): IN PROGRESS; fulfillment-owned metadata/receipt and native shipping readiness.
