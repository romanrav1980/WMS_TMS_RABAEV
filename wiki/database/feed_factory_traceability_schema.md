# Feed Factory Traceability Schema

## Role

This page is the local wiki mirror for the feed-factory traceability schema introduced by migration `2026-05-17-001-feed-factory-traceability`.

The schema supports:

- production batches;
- raw-material batches and usage;
- finished-goods pallets;
- Mercury batch metadata;
- Honest Sign / CRPT codes and SSCC aggregation;
- production-release JSON file exchange;
- regulatory outbox processing.

## Migration

SQL files:

- [`../../db/migrations/2026-05-17_feed_factory_traceability/001_apply.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/001_apply.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/001_rollback.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/001_rollback.sql)
- [`../../db/migrations/2026-05-17_feed_factory_traceability/001_verify.sql`](../../db/migrations/2026-05-17_feed_factory_traceability/001_verify.sql)

Status: applied to local Oracle VM schema `RABAEV@127.0.0.1:1521/orcl` after explicit approval.

Apply/verify result:

- Code checkpoint before apply: `0e0c270`.
- Apply: `Statements=4; Errors=0`.
- Verify: `Statements=6; Errors=0`.
- Final live object check excluding recycle-bin objects: `456 VALID`, `0 INVALID`.

## Version Ledger

The migration introduces `RRL_SCHEMA_MIGRATIONS` as the Oracle-side version ledger.

Version ID:

```text
2026-05-17-001-feed-factory-traceability
```

The ledger is intentionally kept as a small foundation table so future Oracle changes can be tracked and rolled back together with code versions.

## Core Tables

- `RRL_PROD_BATCH`: production batch header.
- `RRL_PROD_BATCH_PALLETS`: production batch to WMS pallet mapping.
- `RRL_RAW_BATCH`: raw-material batch.
- `RRL_PROD_RAW_USAGE`: raw-material usage in a production batch.
- `RRL_MERCURY_BATCH`: Mercury identifiers, statuses, and product metadata for the production batch.
- `RRL_CRPT_CODES`: item-level Honest Sign / CRPT codes.
- `RRL_CRPT_AGGREGATION`: SSCC aggregation header.
- `RRL_CRPT_AGGREGATION_ITEMS`: children of an SSCC aggregation.
- `RRL_REGULATORY_OUTBOX`: outbound regulatory event queue.
- `RRL_FILE_EXCHANGE_LOG`: production-release JSON file import journal.
- `RRL_CLIENT_REG_PROFILE`: client-specific regulatory transfer profile.
- `RRL_SYSTEM_SETTINGS`: system settings, including production batch source mode.

## PL/SQL API

Migration `2026-05-17-002-feed-factory-traceability-api` introduces package `RRL_PRODUCTION_API`.

The package is the intended database boundary for the future API server and the production-release file worker. It keeps direct writes to the traceability tables in one controlled contract.

Main operations:

- `CREATE_PROD_BATCH`: create or idempotently find a production batch.
- `ATTACH_PALLET`: link a WMS pallet to a production batch and optional `SSCC`.
- `REGISTER_RAW_BATCH`: create or idempotently find a raw-material batch.
- `ADD_RAW_USAGE`: register raw-material usage in a production batch.
- `SET_MERCURY_BATCH`: write Mercury/VetIS identifiers and statuses.
- `ADD_CRPT_CODE`: register Honest Sign item code/CIS.
- `CREATE_AGGREGATION` and `ADD_AGGREGATION_ITEM`: maintain `SSCC` aggregation.
- `ENQUEUE_EVENT`: add pending Mercury/CRPT events to `RRL_REGULATORY_OUTBOX`.
- `REGISTER_FILE_MESSAGE`, `MARK_FILE_PROCESSED`, `MARK_FILE_ERROR`: maintain JSON folder-exchange journal.
- `GET_SETTING` and `SET_SETTING`: read and update traceability settings.

Apply/verify result for `2026-05-17-002-feed-factory-traceability-api`:

- Code checkpoint before apply: `b823af6`.
- Apply: `Statements=4; Errors=0`.
- Verify: `Statements=4; Errors=0`.
- `RRL_PRODUCTION_API` package and package body are `VALID`.
- Smoke: `002_smoke_cleanup.sql` finished with `Statements=12; Errors=0`.
- Smoke cleanup check: `SMOKE-BATCH-002 = 0`, `SMOKE-20260517-002 = 0`.
- Final live object check excluding recycle-bin objects: `458 VALID`, `0 INVALID`.

## Existing Table Extensions

`RRL_PALLETS` receives:

- `PROD_BATCH_ID`
- `SSCC`
- `MERCURY_STATUS`
- `CRPT_STATUS`
- `QUALITY_STATUS`

`RRL_SBORKA_PALLET_ROWS` receives:

- `PROD_BATCH_ID`
- `SSCC`
- `CRPT_TRANSFER_MODE`

## File Exchange Settings

Initial settings inserted by the migration:

- `PRODUCTION_BATCH_SOURCE = MANUAL`
- `PROD_EXCHANGE_ROOT_DIR = null`
- `PROD_EXCHANGE_ENABLED = 0`

`FILE_EXCHANGE` mode should not be enabled until the worker/importer exists and the folder contract is tested.

## Rollback

Rollback script:

- drops the traceability tables, sequences, and added pallet columns;
- removes inserted production exchange settings;
- removes the migration row from `RRL_SCHEMA_MIGRATIONS`;
- keeps the migration ledger/settings foundation tables themselves if present.

Before rollback, export any data already written to the new traceability tables.
