# 2026-05-17 Feed Factory Traceability

Versioned Oracle migration for the feed-factory WMS/MES traceability layer.

This migration is prepared for review only. Do not apply it to the live Oracle VM until the user explicitly approves the exact script.

## Files

- `001_apply.sql`: additive forward migration.
- `001_rollback.sql`: rollback script for the migration.
- `001_verify.sql`: read-only verification after apply or rollback.

## Scope

The migration adds the first database layer for:

- production batches;
- raw-material batches and usage;
- production batch to pallet links;
- Mercury batch metadata;
- Honest Sign / CRPT codes and SSCC aggregation;
- regulated integration outbox;
- production-release JSON file exchange log;
- client regulatory profile for aggregation mode;
- schema migration ledger.

It also adds non-destructive columns to existing WMS tables:

- `RRL_PALLETS`;
- `RRL_SBORKA_PALLET_ROWS`.

## Safety

The apply script is intended to be additive and idempotent:

- it creates missing tables/sequences/indexes;
- it adds missing columns;
- it records migration version `2026-05-17-001-feed-factory-traceability`;
- it does not drop existing objects;
- it does not update existing warehouse rows.

The rollback script is destructive for the new migration objects and should only be used after exporting any data written into the new tables.

## Required Procedure

1. Create or confirm a VirtualBox snapshot before applying to the live Oracle VM.
2. Review `001_apply.sql`.
3. Apply only after explicit approval.
4. Run `001_verify.sql`.
5. Confirm no invalid current objects in `USER_OBJECTS`.
6. Commit the repo state so code/database versions can be rolled back together.

## Version ID

`2026-05-17-001-feed-factory-traceability`

