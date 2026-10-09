---
name: nicora-oracle
description: Develop NICORA Oracle and PL/SQL contracts, reservations, concurrent operations and migrations. Use for legacy schema drift, transactional effects and SQL performance in TMS.
---

# NICORA Oracle

Read wiki/index.md, wiki/database/oracle_change_protocol.md and the relevant database mirror. For transport read wiki/database/tms2_oracle_contract.md. Inspect actual columns, arguments and callers before assuming legacy names.

- Use tms-oracle for bounded diagnostics and OracleApply/versioned SQL for changes. Never invoke a potentially mutating function merely because it is wrapped in SELECT. Tool credentials may have write privileges.
- Confirm service/schema and isolated fixture before writes. Observed dev: Oracle 19c ORCL/orcl, RABAEV; this does not prove isolation. Capture fresh INVALID baseline: 59 objects were invalid on 2026-10-07. Separate pre-existing failures from regressions without silently relaxing zero-INVALID gates.
- Define one transaction for physical facts, reservations, composition, business journal and required outgoing event. Several gateway calls with individual commits are not atomic. Test competition over the same SKU/lot/location/load unit, idempotency, timeout after commit and intermediate failure.
- Planned receipts are not physical stock; reserve conversion follows process requirements. Call DML PL/SQL functions in PL/SQL blocks, not SELECT FROM DUAL. Preserve RUSERS/USER_GROUP/RIGHTS and GLOBAL_ADMIN semantics.
- Mirror changes in wiki/database and SQL with stable migration ID and apply/rollback/verify. Follow checkpoint, authorization and recovery requirements from the change protocol, resolving existing user authorization before requesting it again. Tooling setup does not authorize business DDL.
- After meaningful cases review RRL_SQL_SLOW_LOG, admin slow SQL, Oracle top SQL and API audit as available. Record rewrite, bounded window, batching, cache, index/migration, plan/statistics check or owned backlog decision; disclose unavailable evidence.
- Russian SQL stays UTF-8; verify seed values for mojibake and run scripts/check-encoding.ps1. Verify changed-object compilation, constraints, balance and migration ledger. SQLite and untested rollback do not prove Oracle recovery.
