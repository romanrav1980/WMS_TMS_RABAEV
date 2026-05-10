# Runbook: Oracle Recovery 2026-05-11

## Incident

The Oracle Developer VM service `orcl` contained the working `RABAEV` schema for the project. A SQL*Plus-style DDL entrypoint was accidentally run against that schema.

There was no pre-existing VirtualBox snapshot before the accidental DDL run.

## Recovery Performed

1. Created VirtualBox snapshot `before-flashback-repair-2026-05-11`.
2. Identified fresh recycle-bin table entries for owner `RABAEV` dropped at `2026-05-10 16:26`.
3. Removed damaged current empty table versions.
4. Restored 49 tables from recycle bin using `FLASHBACK TABLE ... TO BEFORE DROP`.
5. Recompiled `RABAEV` with `DBMS_UTILITY.COMPILE_SCHEMA`.
6. Repaired two SFERA helper objects that referenced the wrong legacy column spelling.
7. Advanced sequences that had fallen below restored table `MAX(ID)` values.
8. Created VirtualBox snapshot `after-flashback-repair-2026-05-11`.
9. Exported a SQL restore bundle to `db/restore_points/rabaev_orcl_after_flashback_2026-05-11`.

## Verification

Final object status:

- `FUNCTION`: 176 valid
- `PACKAGE`: 10 valid
- `PACKAGE BODY`: 10 valid
- `PROCEDURE`: 6 valid
- `TABLE`: 79 valid
- `TRIGGER`: 21 valid
- `VIEW`: 1 valid

Key row counts:

- `RRL_ARTICULS`: 5328
- `RRL_CELLS`: 28641
- `RUSERS`: 923
- `RRL_TRANSPORT_TASK`: 30256
- `RRL_SBORKA_PALLETS`: 379194
- `RRL_SBORKA_PALLET_ROWS`: 379194

## Guardrail

Do not run `create_schema.sql` against the working Oracle VM unless the VM has a fresh snapshot and the target schema is confirmed disposable.
