@@after_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/

declare n number;begin select count(*)into n from RRL_STOCK_OPERATION where COMMAND_TYPE in('HU_CREATE','HU_ATTACH','HU_DETACH','HU_MOVE')and STATE='APPLIED'and RRL_HAS_WRIGHT(ACTOR,'warehouse_task_execute')!=1;if n>0 then raise_application_error(-20886,'HU_SCOPED_ROLLBACK_RETAINED_HISTORY');end if;end;
/
@@restore_rrl_stock_hu_cmd_package_body.sql
@@restore_rrl_stock_posting_api_package_body.sql
drop package RRL_HU_EXEC_ACCESS;
@@compile_dependents.sql
@@before_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/

update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-16-hu-scoped-execute';
commit;
