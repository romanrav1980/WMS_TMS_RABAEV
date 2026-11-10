-- Откат идемпотентного создания обычного рейса.
DROP PACKAGE RRL_TRANSPORT_IDEMPOTENT_API;
DROP TABLE RRL_TRIP_CREATE_RESULT;

merge into RRL_SCHEMA_MIGRATIONS d
using (select '2026-10-29-transport-trip-create-idempotent' MIGRATION_ID from dual) s
on (d.MIGRATION_ID = s.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK', APPLIED_AT=sysdate, APPLIED_BY=user;
commit;
