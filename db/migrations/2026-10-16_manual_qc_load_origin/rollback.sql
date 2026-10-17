@@after_sources.sql
@@after_constraint.sql
declare n number;begin select count(*)into n from RRL_TT_LOAD_BOX_WEIGHT where MEASUREMENT_ORIGIN='MANUAL_CONFIRMED'and CASE_BOX_TASK_ID is not null;if n>0 then raise_application_error(-20886,'MANUAL_CASE_LOAD_ROLLBACK_HISTORY_EXISTS');end if;end;
/
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/

@@restore_rrl_stock_load_box_core_package_body.sql
@@restore_rrl_tt_load_box_weight_guard_trigger.sql
@@restore_constraint.sql
@@compile_dependents.sql
@@before_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/

update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-16-manual-qc-load-origin';
commit;
