-- 2026-05-17-007-backfill-user-group-reference rollback
-- Intentionally no-op: USER_GROUP rows are legacy reference data reconstructed from RUSERS/RIGHTS.
-- Deleting them would make rights administration less complete again and could affect future assignments.

select '007 rollback is intentionally no-op' message from dual;
