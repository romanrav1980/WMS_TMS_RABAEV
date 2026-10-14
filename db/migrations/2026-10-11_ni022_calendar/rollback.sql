-- Explicit rollback only after saving facts and checkpointed app sources.
declare n number;begin
 select(select count(*)from RRL_SAP_STORE_CAL_EXCEPTION)+(select count(*)from RRL_SAP_STORE_ORDER where ADMISSION_STATUS='PENDING_CALENDAR')into n from dual;
 if n>0 then raise_application_error(-20863,'CALENDAR_FACTS_REQUIRE_EXPLICIT_RETENTION');end if;
end;
/
drop trigger RRL_SAP_CAL_WRITE_GUARD;
drop trigger RRL_SAP_CAL_EX_GUARD;
drop package RRL_STORE_CALENDAR_API;
drop table RRL_SAP_STORE_CAL_EXCEPTION;
alter table RRL_SAP_STORE_ORDER drop constraint RRL_SAP_STORE_ORDER_CK;
alter table RRL_SAP_STORE_ORDER add constraint RRL_SAP_STORE_ORDER_CK check(ADMISSION_STATUS in('ACCEPTED','PENDING_LATE','REJECTED'));

@@../2026-10-10_ni081_workload_config/004_metadata_permission.sql
