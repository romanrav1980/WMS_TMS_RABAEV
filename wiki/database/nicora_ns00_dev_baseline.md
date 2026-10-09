# NICORA NS00: Oracle dev baseline

7 October 2026. The owner confirmed ORCL/orcl is a dedicated development database and explicitly directed NICORA work and future structure changes in RABAEV. No new schema is required. Redesign follows revision-55 GAP and versioned migrations; this does not authorize erasing unrelated development data.

Initial baseline: 59 INVALID objects (51 functions, seven package bodies, one view), no active USER_ERRORS outside BIN$ recycle-bin objects. Source and code-reference checkpoint: db/restore_points/nicora_ns00_20261007/. Source text is captured before compilation.

Operational maintenance SQL: db/compatibility_fixes/2026-10-07_ns00_recompile/ (apply, verify, rollback explanation), maintenance ID 2026-10-07-NS00-RECOMPILE. It recompiles an explicit list of existing definitions, without table/data reconstruction, package definition edits or new schema. This is compile maintenance, not a structural migration; no migration-ledger DDL is introduced. Invalid compilation status has no business rollback; unchanged source and data are the invariant.

The sprint remains in progress pending actual apply/verify, fixture/reproduction evidence and acceptance. Live verify must exclude BIN$ recycled trigger errors. Functional release gates still require no active INVALID objects.

Verified: OracleApply completed 60 statements, zero errors. INVALID count is now zero, active USER_ERRORS outside BIN$ is zero, and all 59 source definitions are byte-for-byte identical after compilation. No new schema was created.
