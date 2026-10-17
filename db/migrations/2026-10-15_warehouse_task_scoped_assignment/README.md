# Installation and recorded verifier recovery

For a CLEAN installation use **apply_verified.sql**, then the separately versioned warehouse_task_session_warehouse forward migration. The original apply.sql and verify.sql are preserved evidence of the first stopped run: all DDL compiled and exact16 sources passed, but WTASK_INDEXES counted Oracle-owned LOB storage indexes (5 instead of the intended 3 user/PK indexes). They are not the fresh-install entry point.

Root recovered the existing prefix with complete_after_index_verify_fix.sql (6 statements, 0 errors), without repeating DDL or deleting data; corrected full verification, trusted-context probe and ledger APPLIED passed. Do not rerun an installation script against that existing prefix. verify_index_fix.sql is the corrected verification entry point; verify.sql remains original evidence.

Rollback checks exact AFTER sources and requires BOTH empty clock and receipt tables. After any retained version/receipt history, recovery is forward-only. The sidecar and parent identity guards intentionally preserve task IDs and metadata history. Older QA cleanup now uses canonical cancellation/resource close and explicit retirement, not DELETE.
