-- MIGRATION_ID: 2026-10-15-incremental-assembly
-- Required stop-on-error: never drop nonempty production/test history.
declare n number;begin
 select(select count(*)from RRL_ASSEMBLY_STATION)+(select count(*)from RRL_ASSEMBLY_SKU_POLICY)
 +(select count(*)from RRL_ASSEMBLY_POLICY_EVENT)+(select count(*)from RRL_ASSEMBLY_SESSION)
 +(select count(*)from RRL_ASSEMBLY_STEP)+(select count(*)from RRL_ASSEMBLY_CAPTURE)+(select count(*)from RRL_ASSEMBLY_STEP_USE)into n from dual;
 if n!=0 then raise_application_error(-20886,'ASSEMBLY_ROLLBACK_PRESERVE_NONEMPTY_HISTORY');end if;
end;
/
@@before_rrl_stock_case_pick_cmd_body.sql
@@before_rrl_case_scale_admission_body.sql
@@before_rrl_scale_packet_read_spec.sql
@@before_rrl_scale_packet_read_body.sql
drop context RRL_ASSEMBLY_CTX;
drop package RRL_ASSEMBLY_SCALE_API;
drop table RRL_ASSEMBLY_STEP_USE;
drop table RRL_ASSEMBLY_CAPTURE;
drop table RRL_ASSEMBLY_STEP;
drop table RRL_ASSEMBLY_SESSION;
drop table RRL_ASSEMBLY_POLICY_EVENT;
drop table RRL_ASSEMBLY_SKU_POLICY;
drop table RRL_ASSEMBLY_STATION;
begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-incremental-assembly';
commit;
