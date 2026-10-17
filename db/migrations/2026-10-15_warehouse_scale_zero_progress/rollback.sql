@@after_source_guard.sql
declare n number;begin select count(*)into n from RRL_WH_WEIGH_ZERO;if n!=0 then raise_application_error(-20886,'WH_ZERO_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;select count(*)into n from RRL_WH_WEIGH_REQUEST where json_value(SOURCE_JSON,'$.zero_progress_required' returning varchar2(10))='true';if n!=0 then raise_application_error(-20886,'WH_ZERO_INTENT_HISTORY_REQUIRES_FORWARD_RECOVERY');end if;end;
/
@@before_spec.sql
@@before_body.sql
alter package RRL_WH_SCALE_API compile body;
alter package RRL_ASSEMBLY_SCALE_API compile body;
alter trigger RRL_WH_WEIGH_REQUEST_GUARD compile;
alter trigger RRL_WH_WEIGH_CLAIM_GUARD compile;
drop table RRL_WH_WEIGH_ZERO;
declare n number;begin select count(*)into n from USER_ERRORS where NAME in('RRL_WH_WEIGH_REQUEST_API','RRL_WH_WEIGH_ZERO_GUARD','RRL_WH_SCALE_API','RRL_ASSEMBLY_SCALE_API','RRL_WH_WEIGH_REQUEST_GUARD','RRL_WH_WEIGH_CLAIM_GUARD');if n!=0 then raise_application_error(-20886,'WH_ZERO_COMPILE_ERRORS');end if;select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'WH_ZERO_GLOBAL_INVALID');end if;end;
/
@@rollback_verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-warehouse-scale-zero-progress';
commit;
