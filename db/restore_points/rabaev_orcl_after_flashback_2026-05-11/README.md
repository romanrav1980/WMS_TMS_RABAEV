# RABAEV Oracle Restore Point: after-flashback-repair-2026-05-11

This folder is a SQL restore bundle exported from Oracle Developer VM service `orcl` after the RABAEV schema was restored from recycle bin and fully recompiled.

## Context

On 2026-05-11, the Oracle VM schema `RABAEV` was accidentally affected by a DDL run. There were no pre-existing VirtualBox snapshots. A safety snapshot was created before repair, then the schema was restored from Oracle recycle bin entries dropped at `2026-05-10 16:26`.

VirtualBox snapshots created during recovery:

- `before-flashback-repair-2026-05-11`
- `after-flashback-repair-2026-05-11`

Current Oracle verification after repair:

- all `RABAEV` objects are `VALID`;
- `RRL_ARTICULS`: 5328 rows;
- `RRL_CELLS`: 28641 rows;
- `RUSERS`: 923 rows;
- `RRL_TRANSPORT_TASK`: 30256 rows;
- `RRL_SBORKA_PALLETS`: 379194 rows;
- `RRL_SBORKA_PALLET_ROWS`: 379194 rows.

## Layout

```text
restore.sql     master restore script
verify.sql      post-restore checks
ddl/            DBMS_METADATA-generated DDL
data/           table data INSERT scripts, tracked through Git LFS
metadata/       exported object status and table metadata
repair/         repair scripts used before this restore point was exported
```

## Restore

Run `restore.sql` as `SYSTEM` or another privileged user connected to the target PDB.
The script creates or unlocks the `RABAEV` user for a clean VM.

If the target already has a `RABAEV` schema, take a snapshot or export first. Do not run this restore over the only working schema without an explicit rollback point.

```sql
@restore.sql
```

Then run:

```sql
@verify.sql
```

## Notes

- This is an emergency restore point, not a normalized migration.
- `data/*.sql` files are intentionally split below GitHub's 100 MB single-file limit.
- The data files contain operational warehouse data and should be kept in a private repository.
