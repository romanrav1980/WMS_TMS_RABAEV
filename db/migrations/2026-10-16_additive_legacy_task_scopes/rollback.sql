@@after_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/

@@restore_rrl_case_assignment_api_package_body.sql
@@restore_rrl_case_lifecycle_api_package_body.sql
@@restore_rrl_asm_meta_scope_package_body.sql
@@restore_rrl_assembly_scale_api_package_body.sql
@@restore_rrl_case_resource_policy_package_body.sql
@@restore_rrl_wh_weigh_request_api_package_body.sql
@@restore_rrl_stock_case_pick_cmd_package_body.sql
@@restore_rrl_inventory_task_access_package_body.sql
@@restore_rrl_stock_metadata_tx_package_body.sql
@@restore_rrl_case_task_access_package.sql
@@restore_rrl_case_task_access_package_body.sql
@@compile_dependents.sql
@@before_sources.sql
declare n number;begin
 if user!='RABAEV'or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl'then raise_application_error(-20886,'PACKAGE_KIT_TARGET');end if;
 select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_INVALID');end if;
 select count(*)into n from USER_ERRORS where NAME not like 'BIN$%';if n!=0 then raise_application_error(-20886,'PACKAGE_KIT_ERRORS');end if;
end;
/

update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-16-additive-legacy-task-scopes';
commit;
