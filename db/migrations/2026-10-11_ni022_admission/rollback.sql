-- Explicit restoration after sourcecheckpoint recovery, no business deletion.
declare n number;begin select count(*)into n from RRL_SAP_STORE_DECISION;
 if n>0 then raise_application_error(-20863,'ADMISSION_HISTORY_REQUIRES_RETENTION');end if;end;
/
drop trigger RRL_SAP_STORE_ADM_GUARD;
drop trigger RRL_SAP_STORE_DEC_GUARD;
drop package RRL_SAP_STORE_ADMISSION_API;
drop table RRL_SAP_STORE_DECISION;
@@../2026-10-11_ni022_calendar/002_api.sql
@@../2026-10-11_ni022_calendar/004_metadata_permission.sql
@@rollback_pick_guard.sql
