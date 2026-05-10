# Branch: Oracle / PL/SQL Core

## Role

This branch is the database and business-logic core of the WMS/TMS system.

It includes:

- Oracle schema `RABAEV`
- tables, sequences, functions, procedures, packages, triggers
- compatibility and gap patches
- master data seed scripts
- legacy SQL extracts used to reconstruct the schema

## What Lives Here

Core warehouse logic belongs here when it changes persistent state or enforces warehouse rules:

- goods and article data
- documents and document lines
- pallets and pallet lines
- cells and stock balances
- acceptance, picking, movement, inventory, shipping
- transport tasks and operational history
- user rights and warehouse permissions

## Main Current Location

- [`../../db/windowsapplication2_xp12_oracle/`](../../db/windowsapplication2_xp12_oracle/)

Legacy and investigative SQL also exists under:

- [`../../SQL/`](../../SQL/)

Treat `SQL/` as a source/archive area unless a file is explicitly promoted into the normalized schema path.

## Consumers

- [[csharp_desktop_client]] calls procedures and queries from operator workflows.
- [[terminal_contour]] confirms scanned warehouse operations through procedures.
- [[external_integrations]] supplies external source data or staging data.

## Boundaries

- Do not put UI-only behavior here.
- Do not treat ad hoc report SQL as schema truth until it is reconciled with `db/windowsapplication2_xp12_oracle`.
- Do not collapse `RABAEV` and `SUPERMAG`: `RABAEV` is the WMS application schema; `SUPERMAG` is external ERP/source context.

## Primary Sources

- [`../../db/windowsapplication2_xp12_oracle/README.md`](../../db/windowsapplication2_xp12_oracle/README.md)
- [`../../db/windowsapplication2_xp12_oracle/create_schema.sql`](../../db/windowsapplication2_xp12_oracle/create_schema.sql)
- [`../../db/windowsapplication2_xp12_oracle/01_tables.sql`](../../db/windowsapplication2_xp12_oracle/01_tables.sql)
- [`../../db/windowsapplication2_xp12_oracle/03_functions.sql`](../../db/windowsapplication2_xp12_oracle/03_functions.sql)
- [`../../db/windowsapplication2_xp12_oracle/04_procedures.sql`](../../db/windowsapplication2_xp12_oracle/04_procedures.sql)
- [`../../db/windowsapplication2_xp12_oracle/gap_report.md`](../../db/windowsapplication2_xp12_oracle/gap_report.md)
- [`../subprojects/oracle_schema.md`](../subprojects/oracle_schema.md)

