# Repair Scripts

These scripts document the recovery actions used before exporting this restore point.

They are included for auditability only. Do not run them on a healthy database.

Order used during recovery:

1. `flashback_rabaev_20260510_1626.sql`
2. `recompile_rabaev.sql`
3. `fix_sfera_ean_invalid.sql`
4. `repair_sequences_after_flashback.sql`

The final exported state after these scripts had all `RABAEV` objects valid.
