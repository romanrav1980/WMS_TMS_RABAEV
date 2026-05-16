# 2026-05-17 Feed Factory Traceability

Versioned Oracle migration for the feed-factory WMS/MES traceability layer.

This migration was applied to the local Oracle VM schema `RABAEV@127.0.0.1:1521/orcl` after explicit user approval.

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

## Applied Result

- Code checkpoint before apply: `0e0c270`.
- Oracle migration ledger ID: `2026-05-17-001-feed-factory-traceability`.
- Apply result: `Statements=4; Errors=0`.
- Verify result: `Statements=6; Errors=0`.
- Post-apply recompile: `dbms_utility.compile_schema(schema => 'RABAEV', compile_all => false)`.
- Final live object check excluding recycle-bin objects: `456 VALID`, `0 INVALID`.

## Required Procedure For Future Reapply

1. Create or confirm a VirtualBox snapshot before applying to the live Oracle VM.
2. Review `001_apply.sql`.
3. Apply only after explicit approval.
4. Run `001_verify.sql`.
5. Confirm no invalid current objects in `USER_OBJECTS`.
6. Commit the repo state so code/database versions can be rolled back together.

## Version ID

`2026-05-17-001-feed-factory-traceability`
