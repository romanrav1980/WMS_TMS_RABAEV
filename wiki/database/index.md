# Database Mirror: Oracle Schema

## Role

This directory is the local wiki mirror of the Oracle `RABAEV` schema.

Its purpose is to let future development reason about tables, procedures, packages, and integration contracts without repeatedly querying the live Oracle VM for basic structure.

The live Oracle database remains the runtime authority. The wiki mirror is the maintained working map that explains what the schema is supposed to mean and how changes should move through the project.

## Active Oracle Context

- Live development service: `127.0.0.1:1521/orcl`
- Application schema: `RABAEV`
- Compatibility target: legacy C# `WindowsApplication2`, `Tserver`, and future API server
- Current safety rule: no destructive Oracle DDL/DML without explicit permission and a VM snapshot or restore plan

Do not store database passwords, personal credentials, private tokens, or signing secrets in this wiki.

## Mirror Sources

The local schema mirror is maintained from these sources:

- [`../../db/windowsapplication2_xp12_oracle/`](../../db/windowsapplication2_xp12_oracle/): normalized Oracle schema scripts
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

## Related Pages

- [Oracle / PL/SQL Core](../branches/01_oracle_plsql_core.md)
- [Oracle Schema subproject](../subprojects/oracle_schema.md)
- [DB/app compatibility check](../runbooks/db_app_compatibility_check_2026_05_11.md)
- [Oracle recovery runbook](../runbooks/oracle_recovery_2026_05_11.md)
