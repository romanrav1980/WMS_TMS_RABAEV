declare n number;begin select count(*)into n from RRL_WORKLOAD_OPERATION;
 if n>0 then raise_application_error(-20899,'WORKLOAD134_FORWARD_ONLY_AFTER_CONFIG_HISTORY');end if;
end;
/
drop table RRL_WORKLOAD_ATTEND_CANCEL;
/
drop table RRL_WORKLOAD_ATTENDANCE;
/
drop table RRL_WORKLOAD_NORM;
/
drop table RRL_WORKLOAD_OPERATION;
/
drop package RRL_WORKLOAD_CONFIG_API;
/
@@../2026-10-08_stock_posting_core/445_metadata_before_workload.sql
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-10-134-workload-norm-planned-attendance';
commit;
/
