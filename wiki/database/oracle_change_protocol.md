# Oracle Change Protocol

## Purpose

This runbook defines how Oracle structure changes are made in this project.

The rule is simple: no invisible database changes. If a procedure, package, table, sequence, trigger, or integration contract changes, the change must be visible in the local wiki mirror and in the SQL source tree.

## What Counts As A Schema Change

Track and document all of these:

- table creation or column changes
- indexes, constraints, sequences, triggers
- stored procedures, functions, packages, package bodies
- compatibility shims for legacy C# and `Tserver`
- integration-facing tables and outbox/journal tables
- semantic changes in existing procedures, even if their signatures do not change

## Required Steps

1. Describe the change in [`index.md`](index.md) or a focused database mirror page.
2. Add or update SQL under `db/windowsapplication2_xp12_oracle/` for canonical schema work, under `db/migrations/YYYY-MM-DD_name/` for versioned reviewable changes, or under `db/compatibility_fixes/YYYY-MM-DD/` for dated compatibility patches.
3. Give every migration a stable `MIGRATION_ID` and a paired rollback script.
4. Commit or otherwise checkpoint the code version before applying the migration to live Oracle.
5. For broad or destructive DDL, create or confirm a VirtualBox snapshot before applying anything.
6. Apply to live Oracle only after explicit permission when the operation can mutate data or structure.
7. Verify:
   - connection target is `RABAEV@127.0.0.1:1521/orcl`
   - `USER_OBJECTS` has no invalid current objects
   - `USER_ERRORS` has no errors for current objects, ignoring recycle-bin `BIN$...` leftovers
8. Append [`../log.md`](../log.md) with the files changed and verification result.

## Code Version Rule

Database scripts are code and must be versioned with the application repository.

For every Oracle migration:

- create a dedicated folder under `db/migrations/`;
- include `apply`, `rollback`, and `verify` scripts;
- record the same `MIGRATION_ID` in the SQL file, wiki mirror, and Oracle migration ledger;
- commit the migration files before applying them to the database;
- after a successful live apply, record the resulting commit hash and Oracle verification result in the wiki log.

Rollback has two layers:

- code rollback: `git revert` or checkout to the previous commit;
- database rollback: execute the migration's rollback script after explicit approval and data export if needed.

## Read-only Checks

Read-only metadata checks are allowed for verification and discovery:

- `USER_OBJECTS`
- `USER_ERRORS`
- `USER_SOURCE`
- `USER_TAB_COLUMNS`
- `USER_CONSTRAINTS`
- `USER_INDEXES`
- `USER_SEQUENCES`

Prefer managed ODP.NET for local checks. The old Windows `sqlplus` client may fail with `ORA-28040` against the Oracle VM and should not be treated as proof that the database is down.

## Drift Handling

If live Oracle differs from the local SQL/wiki mirror:

1. Stop and classify the drift.
2. If the live database is known-good, export or document the live shape before changing scripts.
3. If the scripts are intended truth, prepare a patch and verify with the user before applying.
4. Never repair drift by dropping/recreating objects casually.

## Completion Definition

An Oracle change is done only when:

- the wiki mirror explains the change,
- SQL files, versioned migrations, or dated patches contain the change,
- live Oracle was updated when required,
- compilation/invalid-object checks are clean,
- the wiki log records the result.
