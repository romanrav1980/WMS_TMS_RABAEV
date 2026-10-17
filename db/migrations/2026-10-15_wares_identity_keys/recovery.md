# Warehouse identity keys: recovery

Migration `2026-10-15-wares-identity-keys` adds PK(ID), mandatory NAME, UNIQUE(NAME).
It changes no row. The current explicitly authorized dev target is RABAEV/orcl.
Frozen before/name audits show291 rows; IDs and exact names are non-null and unique.
NAME uniqueness uses the existing Oracle column comparison; no trim/case rewrite.

Oracle DDL commits independently. If any statement fails, preserve stdout/stderr,
the frozen manifest and fresh USER_CONSTRAINTS/USER_INDEXES/USER_TAB_COLUMNS state.
Do not rerun apply.sql: its before gate deliberately refuses partial installation.
Do not execute rollback.sql on a partial install: it requires all exact keys.

Root recovery is forward completion after a separate reviewed checkpoint:

1. Read the exact installed subset among RRL_WARES_PK, RRL_WARES_NAME_NN and
   RRL_WARES_NAME_UK. Compare enabled/validated state, columns, named normal unique
   indexes and current non-null/duplicate checks against the frozen files.
2. Compare ID/NAME row snapshot with the pre-DDL snapshot. Stop on unexplained drift.
3. Create an additive, immutable recovery script with only the missing reviewed DDL,
   then verify.sql and the original ledger insert. Do not replace/recreate known keys.
4. Independently read back constraints, index columns, nullability, row snapshot,
   current USER_ERRORS excluding BIN$, global INVALID and APPLIED ledger.

Full rollback is allowed only before dependent foreign keys exist and only through
the paired guarded script. Once the actual-time tables reference ID, recovery is
forward-only; never CASCADE, disable dependent keys, or remove warehouse data.

Runtime verification uses caller-rollback duplicate ID/name and null-name attempts
with existing rows, plus a caller-rollback FK proof on an isolated temporary test
table only if required. No test inserts an actual warehouse permanently.
